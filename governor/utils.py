from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission

def optimize_queryset(objs):
    # Either this is not a queryset or the result cache has already been
    # filled..
    if not isinstance(objs, QuerySet) or objs._result_cache is not None:
        return objs
    objs.query.ordering = []
    return objs.distinct()


def get_perm(perm, obj=None):
    if isinstance(perm, Permission):
        return perm
    if '.' in perm:
        app_label, codename = perm.split('.')
    elif obj:
        app_label = obj._meta.app_label
        codename = perm
    else:
        raise ValueError('Permission format must be "app_label.codename"')

    return Permission.objects.get(codename=codename,
        content_type__app_label=app_label)
