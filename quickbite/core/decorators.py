"""Role-based access decorators for dashboard views."""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from users.models import User


def role_required(*roles, login_url=None):
    """
    Restrict view to users with one of the given roles.
    Unauthorized users are redirected to the appropriate login page.
    """
    role_set = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                url = login_url or _login_url_for_roles(role_set)
                return redirect_to_login(request.get_full_path(), login_url=url)

            if user.is_superuser or user.role == User.Role.ADMIN:
                if User.Role.ADMIN in role_set:
                    return view_func(request, *args, **kwargs)

            if user.role not in role_set:
                return redirect(_dashboard_url_for_role(user.role))

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def _login_url_for_roles(role_set):
    if User.Role.RESTAURANT in role_set:
        return "/accounts/login/restaurant/"
    if User.Role.RIDER in role_set:
        return "/accounts/login/rider/"
    return "/accounts/login/"


def _dashboard_url_for_role(role):
    mapping = {
        User.Role.ADMIN: "/admin/",
        User.Role.CUSTOMER: "/",
        User.Role.RESTAURANT: "/partners/partner-dashboard/",
        User.Role.RIDER: "/riders/rider-dashboard/",
    }
    return mapping.get(role, "/")
