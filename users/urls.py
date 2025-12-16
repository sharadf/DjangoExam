from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('admin/users/', views.user_list, name="user_list"),
    path("admin/users/<int:pk>/ban/", views.user_ban, name="user_ban"),
    path("admin/users/<int:pk>/unban/", views.user_unban, name="user_unban"),
    path("admin/users/<int:pk>/make-admin/", views.make_admin, name="make_admin"),
    path("admin/users/<int:pk>/remove-admin/", views.remove_admin, name="remove_admin"),

    path("notifications/", views.notifications, name="notifications"),

    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register")
]
