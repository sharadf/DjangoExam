from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated and user.banned:
            allowed_paths = [
                "/users/login/",
                "/users/logout/",
            ]

            if request.path not in allowed_paths:
                logout(request)
                messages.error(request, "Your account is banned.")
                return redirect("users:login")

        return self.get_response(request)
