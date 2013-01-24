from django.db.models import Q
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from guardian.models import UserObjectPermission, GroupObjectPermission
from governor.shortcuts import (get_users_eligible_for_object,
    get_groups_eligible_for_object)
from governor.receivers import (setup_users_eligible_for_object,
    setup_groups_eligible_for_object, setup_objects_eligible_for_user,
    setup_objects_eligible_for_group)
from governor import roles
from .models import Profile, Newspaper, Article


@roles.register('tests.review_article', 'tests.preview_article')
class EditorRole(object):
    def users_eligible_for_object(self, obj, perm):
        # Global editors..
        global_editors = Q(profile__is_editor=True)

        # Editors assigned to the newspaper..
        newspaper_editors = Q(pk__in=obj.newspaper.editors.all())

        # Article editor..
        article_editor = Q(pk=obj.editor_id)

        # Author of the article..
        article_author = Q(pk=obj.author_id)

        return User.objects.filter(global_editors | newspaper_editors |
            article_editor | article_author)

    def groups_eligible_for_object(self, obj, perm):
        return Group.objects.filter(name='Editors')

    def objects_eligible_for_user(self, user, perm):
        articles = Article.objects.all()
        # Gloabl editor or in the editor group..
        if user.profile.is_editor or user.groups.filter(name='Editors').exists():
            return articles

        # Articles the user is the author or editor for..
        return articles.filter(Q(author=user) | Q(editor=user))

    def objects_eligible_for_group(self, group, perm):
        if group.name == 'Editors':
            return Article.objects.all()


class RoleTestCase(TestCase):
    def setUp(self):
        self.group = Group(name='Editors')
        self.group.save()

        self.user1 = User(username='user1')
        self.user1.save()
        Profile(user=self.user1, is_editor=False).save()

        self.user2 = User(username='user2')
        self.user2.save()
        Profile(user=self.user2, is_editor=False).save()

        self.user3 = User(username='user3')
        self.user3.save()
        Profile(user=self.user3, is_editor=False).save()

        self.user4 = User(username='user4')
        self.user4.save()
        Profile(user=self.user4, is_editor=False).save()
        self.user4.groups.add(self.group)


        self.editor1 = User(username='editor1')
        self.editor1.save()
        Profile(user=self.editor1, is_editor=True).save()

        self.editor2 = User(username='editor2')
        self.editor2.save()
        Profile(user=self.editor2, is_editor=True).save()

        self.newspaper = Newspaper(name='NYT')
        self.newspaper.save()
        self.newspaper.editors.add(self.editor1)

        self.article = Article(newspaper=self.newspaper, author=self.user1,
            editor=self.editor1)
        self.article.save()

    def test_registry(self):
        self.assertEqual(len(roles.get_perms_for_role(EditorRole)), 2)

    def test_shortcuts_noop(self):
        users = get_users_eligible_for_object('tests.add_article', self.article)
        groups = get_groups_eligible_for_object('tests.add_article', self.article)   

        self.assertEqual(len(users), 0)
        self.assertEqual(len(groups), 0)

    def test_shortcuts(self):
        users = get_users_eligible_for_object('tests.review_article', self.article)
        self.assertEqual(len(users), 3)
        self.assertEqual(len(set(users)), 3)

        pks = [self.user1.pk, self.editor1.pk, self.editor2.pk]
        self.assertTrue(all([u.pk in pks for u in users]))

        groups = get_groups_eligible_for_object('tests.review_article', self.article)
        self.assertEqual(groups[0], self.group)

    def test_receivers(self):
        receiver1 = setup_users_eligible_for_object('tests.review_article')
        post_save.connect(receiver1, sender=Article)

        receiver2 = setup_groups_eligible_for_object('tests.review_article')
        post_save.connect(receiver2, sender=Article)

        receiver3 = setup_objects_eligible_for_user('tests.review_article')
        post_save.connect(receiver3, sender=User)

        receiver4 = setup_objects_eligible_for_group('tests.review_article')
        post_save.connect(receiver4, sender=Group)

        self.assertEqual(UserObjectPermission.objects.count(), 0)
        self.assertEqual(GroupObjectPermission.objects.count(), 0)

        article = Article(newspaper=self.newspaper, author=self.user1,
            editor=self.editor1)
        article.save()

        self.assertEqual(UserObjectPermission.objects.count(), 3)
        self.assertEqual(GroupObjectPermission.objects.count(), 1)

        # user4 has permission because of the group..
        for u in (self.user1, self.editor1, self.editor2, self.user4):
            self.assertTrue(u.has_perm('tests.review_article', article))

        article = Article(newspaper=self.newspaper, author=self.user2,
            editor=self.editor1)
        article.save()

        for u in (self.user2, self.editor1, self.editor2, self.user4):
            self.assertTrue(u.has_perm('tests.review_article', article))
