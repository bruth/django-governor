import logging
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from guardian.models import UserObjectPermission, GroupObjectPermission
from .roles import get_roles_for_perm
from . import utils

logger = logging.getLogger('governor')

def _compact(perm, obj, model_class, method_name, existing):
    "Construct a QuerySet of `model_class` instances from roles."
    roles = get_roles_for_perm(perm)

    # Perm not registered, nothing to do
    if not roles:
        return []

    eligible = set()

    for role in roles:
        method = getattr(role, method_name, None)
        if method is None:
            continue

        objs = method(obj, perm)

        if objs is None:
            continue

        for obj in objs:
            eligible.add(obj.pk)

    eligible = model_class.objects.filter(pk__in=eligible)

    if existing is not None:
        eligible = eligible.exclude(pk__in=existing)

    return eligible.distinct()


def get_users_eligible_for_object(perm, obj, exclude_existing=True):
    """Returns a list of eligible users that do not already have the
    permission for `obj`.
    """
    perm = utils.get_perm(perm)

    if exclude_existing:
        ct = ContentType.objects.get_for_model(obj)
        # Get set of existing objects ids to compare against..
        existing = UserObjectPermission.objects.filter(permission=perm,
            content_type=ct, object_pk=obj.pk).values_list('user__pk', flat=True)
    else:
        existing = None

    return _compact(perm, obj, User, 'users_eligible_for_object', existing)


def get_groups_eligible_for_object(perm, obj, exclude_existing=True):
    """Returns a list of eligible groups that do not already have the
    permission for `obj`.
    """
    perm = utils.get_perm(perm)

    if exclude_existing:
        ct = ContentType.objects.get_for_model(obj)
        # Get set of existing objects ids to compare against..
        existing = GroupObjectPermission.objects.filter(permission=perm,
            content_type=ct, object_pk=obj.pk).values_list('group__pk', flat=True)
    else:
        existing = None

    return _compact(perm, obj, Group, 'groups_eligible_for_object', existing)


def get_objects_eligible_for_user(perm, user, exclude_existing=True):
    """Returns a list of eligible users that do not already have the
    permission for `obj`.
    """
    perm = utils.get_perm(perm)
    model_class = perm.content_type.model_class()

    if exclude_existing:
        ct = ContentType.objects.get_for_model(model_class)
        # Get set of existing objects ids to compare against..
        existing = UserObjectPermission.objects.filter(permission=perm,
            content_type=ct, user=user).values_list('object_pk', flat=True)
    else:
        existing = None

    return _compact(perm, user, model_class, 'objects_eligible_for_user', existing)

def get_objects_eligible_for_group(perm, group, exclude_existing=True):
    """Returns a list of eligible users that do not already have the
    permission for `obj`.
    """
    perm = utils.get_perm(perm)
    model_class = perm.content_type.model_class()

    if exclude_existing:
        ct = ContentType.objects.get_for_model(model_class)
        # Get set of existing objects ids to compare against..
        existing = GroupObjectPermission.objects.filter(permission=perm,
            content_type=ct, group=group).values_list('object_pk', flat=True)
    else:
        existing = None

    return _compact(perm, group, model_class, 'objects_eligible_for_group', existing)
