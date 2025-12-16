from django.db import models
from django.db.models import Sum, Avg
from users.models import User
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


from django.utils.text import slugify
from django.db import models
import uuid


class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending moderation"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    content = models.TextField()

    # 'users.User'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    moderation_comment = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(unique=True, blank=True)

    def is_visible(self):
        return self.status == "approved"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Генерируем slug только если он пустой
        if not self.slug:
            # Создаем базовый slug из заголовка
            base_slug = slugify(self.title)

            # Если базовый slug пустой (например, title состоит из нелатинских символов)
            if not base_slug:
                base_slug = "article"

            slug = base_slug

            # Проверяем уникальность slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def rating_avg(self):
        return Rating.objects.filter(article=self).aggregate(
            avg=Avg("value")
        )["avg"] or 0
        # 👍 количество лайков

    def likes_count(self):
        return Rating.objects.filter(article=self, value=1).count()

    # 👎 количество дизлайков
    def dislikes_count(self):
        return Rating.objects.filter(article=self, value=-1).count()

    # ⭐ какая оценка пользователя
    def user_rating(self, user):
        if not user.is_authenticated:
            return 0
        obj = Rating.objects.filter(article=self, user=user).first()
        return obj.value if obj else 0

    # 🔗 Получить абсолютный URL
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('articles:article_detail', kwargs={'slug': self.slug})


class Rating(models.Model):
    LIKE_CHOICES = (
        (1, 'Like'),
        (-1, 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    value = models.IntegerField(choices=LIKE_CHOICES)

    class Meta:
        unique_together = ('user', 'article')  # одна оценка от юзера

    def __str__(self):
        return f"{self.user.username} → {self.value}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class ModerationLog(models.Model):
    ACTION_CHOICES = (
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    article = models.ForeignKey(
        "Article",
        on_delete=models.CASCADE,
        related_name="moderation_logs"
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="moderation_actions"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.article.title} — {self.action}"
