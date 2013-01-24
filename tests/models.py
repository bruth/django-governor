from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    is_editor = models.BooleanField(default=False)


class Newspaper(models.Model):
    name = models.CharField(max_length=30, unique=True)
    editors = models.ManyToManyField(User, blank=True)


class Article(models.Model):
    author = models.ForeignKey(User, related_name='articles')
    editor = models.ForeignKey(User, null=True, blank=True,
        related_name='editor_articles')
    newspaper = models.ForeignKey(Newspaper)

    class Meta(object):
        permissions = (
            ('review_article', 'Can review article'),
            ('preview_article', 'Can preview article'),
        )
