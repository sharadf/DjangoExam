from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model

from .utils import can_manage_users

User = get_user_model()


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next", "articles:article_list")
            return redirect(next_url)
        else:
            messages.error(request, "Неверный логин или пароль")

    return render(request, "users/login.html")


def user_logout(request):
    logout(request)
    return redirect("articles:article_list")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Такое имя уже занято")
            return redirect("users:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Такой email уже используется")
            return redirect("users:register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Регистрация прошла успешно!")
        return redirect("users:login")

    return render(request, "users/register.html")


def admin_required(user):
    return user.is_authenticated and user.role in ["admin", "superadmin"]


def superadmin_required(user):
    return user.is_authenticated and user.role == "superadmin"


@login_required
def user_list(request):
    if not admin_required(request.user):
        return HttpResponseForbidden("Access denied")

    users = User.objects.all().order_by("username")
    return render(request, "users/user_list.html", {"users": users})


@login_required
def user_ban(request, pk):
    if not admin_required(request.user):
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=pk)

    if not can_manage_users(request.user, user):
        return HttpResponseForbidden("You cannot ban this user")

    user.banned = True
    user.save()
    return redirect("users:user_list")


@login_required
def user_unban(request, pk):
    if not admin_required(request.user):
        return HttpResponseForbidden()

    user = get_object_or_404(User, pk=pk)

    if not can_manage_users(request.user, user):
        return HttpResponseForbidden("You cannot unban this user")

    user.banned = False
    user.save()
    return redirect("users:user_list")


@login_required
def make_admin(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user.role == "user":
        user.role = "admin"
        user.save()
    return redirect("users:user_list")


# В users/views.py добавьте эту функцию:

@login_required
def remove_admin(request, pk):
    """Убрать права администратора у пользователя"""
    if request.user.role != "superadmin":
        messages.error(request, "У вас нет прав для выполнения этого действия")
        return redirect("users:user_list")

    user_to_demote = get_object_or_404(User, pk=pk)

    # Проверяем, что нельзя снять права у суперадмина или себя
    if user_to_demote.role == "superadmin":
        messages.error(request, "Нельзя снять права у супер-администратора")
        return redirect("users:user_list")

    if user_to_demote == request.user:
        messages.error(request, "Вы не можете снять права администратора у себя")
        return redirect("users:user_list")

    # Меняем роль только если пользователь является админом
    if user_to_demote.role == "admin":
        user_to_demote.role = "user"
        user_to_demote.save()
        messages.success(request, f"Пользователь {user_to_demote.username} лишен прав администратора")

    return redirect("users:user_list")


@login_required
def notifications(request):
    notifications = request.user.notifications.order_by("-created_at")
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, "users/notifications.html", {"notifications": notifications})
