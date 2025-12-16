from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings
from django.db import models



class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    banned = models.BooleanField(default=False)
    date_of_registration = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(unique=True, blank=True)

    def is_admin(self):
        return self.role in ["admin", "superadmin"]

    def is_superadmin(self):
        return self.role == "superadmin"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f" {self.username} ({self.role})"



class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("approved", "Article approved"),
        ("rejected", "Article rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.type}"
