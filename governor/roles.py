from collections import defaultdict
from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth.models import Permission


class Role(object):
    def users_eligible_for_object(self, obj, perm):
        "Get all users eligible for the object's permission."

    def groups_eligible_for_object(self, obj, perm):
        "Get all groups eligible for the object's permission."

    def objects_eligible_for_user(self, user, perm):
        "Get all objects the user is eligible for the permission."
        
    def objects_eligible_for_group(self, group, perm):
        "Get all objects the group is eligible for the permission."


class Registry(object):
    def __init__(self):
        # List of roles by permission
        self._perm_roles = defaultdict(list)

        # Set of permissions per role to prevent registering a
        # permission multiple times for the same role
        self._role_perms = defaultdict(list)

    def register(self, klass, perms):
        # Register a role instance with each permission
        for perm in perms:
            if '.' not in perm:
                raise ValueError('Permission format must be "app.codename": {0}'.format(perm))
            # Skip it.. already registered
            if perm in self._role_perms[klass]:
                continue
            self._role_perms[klass].append(perm)

            # Reigster the role with the permission
            self._perm_roles[perm].append(klass())


registry = Registry()

def register(*perms):
    def decorator(klass):
        registry.register(klass, perms)
        return klass
    return decorator

def get_roles_for_perm(perm):
    if isinstance(perm, Permission):
        perm = '{0}.{1}'.format(perm.content_type.app_label, perm.codename)
    return registry._perm_roles.get(perm, [])

def get_perms_for_role(klass):
    return registry._role_perms.get(klass, [])

def autodiscover(module_name):
    """Simple auto-discover for looking through each INSTALLED_APPS for each
    ``module_name`` and fail silently when not found. This should be used for
    modules that have 'registration' like behavior.
    """
    for app in settings.INSTALLED_APPS:
        # Attempt to import the app's ``module_name``.
        try:
            import_module('{0}.{1}'.format(app, module_name))
        except:
            pass
