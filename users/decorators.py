from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied()
        if request.user.role not in ["admin", "superadmin"]:
            raise PermissionDenied()
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied()
        if request.user.role != "superadmin":
            raise PermissionDenied()
        return view_func(request, *args, **kwargs)
    return wrapper
