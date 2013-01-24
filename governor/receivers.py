from functools import wraps
from django.db import transaction
from guardian.models import UserObjectPermission, GroupObjectPermission
from .shortcuts import (get_users_eligible_for_object,
    get_groups_eligible_for_object, get_objects_eligible_for_user,
    get_objects_eligible_for_group)
from . import utils


def setup_users_eligible_for_object(*perms):
    """Post-save signal receiver producer to setup a new object 

    Since this is the first time permissions are being setup, the `bulk_create`
    manager method is used for performance.
    """
    @transaction.commit_on_success
    @wraps(setup_users_eligible_for_object)
    def receiver(sender, instance, created, raw, **kwargs):
        if raw or not created:
            return

        obj_perms = []

        for perm in perms:
            perm = utils.get_perm(perm)
            users = get_users_eligible_for_object(perm, instance)

            for user in users:
                obj_perms.append(UserObjectPermission(user=user,
                    permission=perm, content_object=instance))

        UserObjectPermission.objects.bulk_create(obj_perms)

    return receiver

def setup_groups_eligible_for_object(*perms):
    """Post-save signal receiver producer to associate a eligible groups to
    a new object.

    Since this is the first time permissions are being setup, the `bulk_create`
    manager method is used for performance.
    """
    @transaction.commit_on_success
    @wraps(setup_groups_eligible_for_object)
    def receiver(sender, instance, created, raw, **kwargs):
        if raw or not created:
            return

        obj_perms = []

        for perm in perms:
            perm = utils.get_perm(perm)
            groups = get_groups_eligible_for_object(perm, instance)

            for group in groups:
                obj_perms.append(GroupObjectPermission(group=group,
                    permission=perm, content_object=instance))

        GroupObjectPermission.objects.bulk_create(obj_perms)

    return receiver


def setup_objects_eligible_for_user(*perms):
    "Post-save signal receiver producer to associate objects to a new user."

    @transaction.commit_on_success
    @wraps(setup_objects_eligible_for_user)
    def receiver(sender, instance, created, raw, **kwargs):
        if raw or not created:
            return

        obj_perms = []

        for perm in perms:
            perm = utils.get_perm(perm)
            objs = get_objects_eligible_for_user(perm, instance)

            for obj in objs:
                obj_perms.append(UserObjectPermission(user=instance, permission=perm,
                    content_object=obj))

        UserObjectPermission.objects.bulk_create(obj_perms)

    return receiver


def setup_objects_eligible_for_group(*perms):
    "Post-save signal receiver producer to associate objects to a new group."

    @transaction.commit_on_success
    @wraps(setup_objects_eligible_for_group)
    def receiver(sender, instance, created, raw, **kwargs):
        if raw or not created:
            return

        obj_perms = []

        for perm in perms:
            perm = utils.get_perm(perm)
            objs = get_objects_eligible_for_group(perm, instance)

            for obj in objs:
                obj_perms.append(GroupObjectPermission(group=instance,
                    permission=perm, content_object=obj))

        GroupObjectPermission.objects.bulk_create(obj_perms)

    return receiver
