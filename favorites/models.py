from django.db import models
from django.conf import settings

class Favorite(models.Model):
    # используем строковую ссылку "app_label.ModelName"
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    article = models.ForeignKey('articles.Article', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f"{self.user.username} → {self.article.title}"
