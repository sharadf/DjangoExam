from django.core.exceptions import PermissionDenied


def is_superadmin(user):
    return user.is_authenticated and user.role == "superadmin"


def is_admin(user):
    return user.is_authenticated and user.role in ["admin", "superadmin"]


def is_user(user):
    return user.is_authenticated and user.role == "user"


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            return PermissionDenied()
        return view_func(request, *args, **kwargs)

    return wrapper


def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_superadmin(request.user):
            return PermissionDenied()
        return view_func(request, *args, **kwargs)

    return wrapper
