def is_admin(user):
    return user.role in ("admin", "superadmin")


def is_superadmin(user):
    return user.role == "superadmin"


def is_user(user):
    return user.role == "user"


def can_manage_users(current_user, target_user):
    if current_user == target_user:
        return False

    if current_user == "admin" or target_user.role in ["admin", "superadmin"]:
        return False

    if current_user.role == "superadmin":
        return True

    return False
