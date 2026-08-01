from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q


GROUP_GENERAL_ADMIN = 'أدمن عام'
GROUP_BRANCH_MANAGER = 'مدير فرع'


def get_user_branch(user):
    """Return the branch linked to the user profile, or None."""
    if not user.is_authenticated:
        return None
    if hasattr(user, 'profile'):
        return user.profile.branch
    return None


def is_general_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=GROUP_GENERAL_ADMIN).exists()


def is_branch_manager(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=GROUP_BRANCH_MANAGER).exists()


def filter_branches_for_user(queryset, user):
    if is_general_admin(user):
        return queryset
    branch = get_user_branch(user)
    if branch:
        return queryset.filter(pk=branch.pk)
    return queryset.none()


def filter_inventory_for_user(queryset, user):
    if is_general_admin(user):
        return queryset
    branch = get_user_branch(user)
    if branch:
        return queryset.filter(branch=branch)
    return queryset.none()


def filter_transfers_for_user(queryset, user):
    if is_general_admin(user):
        return queryset
    branch = get_user_branch(user)
    if branch:
        return queryset.filter(Q(from_branch=branch) | Q(to_branch=branch))
    return queryset.none()


def user_can_manage_branch(user, branch):
    if is_general_admin(user):
        return True
    user_branch = get_user_branch(user)
    return user_branch and user_branch.pk == branch.pk


def require_general_admin(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_general_admin(request.user):
            raise PermissionDenied('هذه الصفحة متاحة للأدمن العام فقط.')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_login_branch_access(view_func):
    """يسمح لأي مستخدم مسجّل بالدخول. الصلاحيات تُطبّق عبر فلترة البيانات."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
