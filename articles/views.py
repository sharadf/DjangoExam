from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib import messages
from pygments.lexers import q
from .models import Comment, ModerationLog
from .forms import ArticleForm, CommentForm
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Article, Rating
from favorites.models import Favorite
from users.models import Notification

from users.decorators import admin_required


# Список статей
def article_list(request):
    avg_rating = 0

    if request.user.is_authenticated and request.user.role in ["admin", "superadmin"]:
        articles = Article.objects.all().order_by("-created_at")
    else:
        articles = Article.objects.filter(status="approved").order_by("-created_at")
        avg_rating = Rating.objects.aggregate(
            avg=Avg("value")
        )["avg"] or 0

    return render(request,
                  "articles/article_list.html",
                  {"articles": articles,
                   "avg_rating": avg_rating})




def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # 🔐 Проверка доступа к статье
    if article.status == "pending":
        if request.user.is_authenticated and request.user.role in ["admin", "superadmin"]:
            pass
        elif request.user == article.author:
            pass
        else:
            raise Http404("Статья не опубликована")

    # ==========================
    # 📌 ОБРАБОТКА POST
    # ==========================
    if request.method == "POST":

        # ➖ Удаление комментария
        if "delete_comment" in request.POST:
            comment_id = request.POST.get("delete_comment")
            comment = get_object_or_404(Comment, id=comment_id, article=article)

            if (
                    request.user == comment.user
                    or request.user.role in ["admin", "superadmin"]
            ):
                comment.delete()
                return redirect(article.get_absolute_url())
            else:
                raise PermissionDenied()

        # ➕ Добавление комментария
        if "add_comment" in request.POST:
            if not request.user.is_authenticated:
                raise PermissionDenied()

            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.article = article
                comment.save()
                return redirect(article.get_absolute_url())

    # ==========================
    # 📌 GET-ЧАСТЬ
    # ==========================
    comments = Comment.objects.filter(article=article).select_related("user")

    # ⭐ Избранное
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            article=article
        ).exists()

    context = {
        "article": article,
        "comments": comments,
        "form": CommentForm(),
        "is_favorite": is_favorite,

        # ⭐ Рейтинг
        "rating_total": article.rating_avg(),
        "user_rating": article.user_rating(request.user),
        "likes_count": article.likes_count(),
        "dislikes_count": article.dislikes_count(),
    }

    return render(request, "articles/article_detail.html", context)


# Создание статьи
@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = "pending"
            article.save()
            return redirect("articles:article_detail", slug=article.slug)
    else:
        form = ArticleForm()

    return render(request, "articles/article_form.html", {"form": form})


@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if request.user != article.author and request.user.role not in ["admin", "superadmin"]:
        return HttpResponseForbidden("You cannot edit this article")

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect("articles:article_detail", slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/article_form.html", {"form": form})


@login_required
def article_delete(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if request.user != article.author and request.user.role not in ["admin", "superadmin"]:
        return HttpResponseForbidden("You cannot delete this article")

    article.delete()
    return redirect("articles:article_list")


def rating(self):
    return self.rating_set.aggregate(total=Sum("value"))["total"] or 0


def like_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    rating, created = Rating.objects.get_or_create(
        user=request.user, article=article,
        defaults={"value": 1}
    )

    if not created:
        rating.value = 1
        rating.save()

    return redirect("articles:article_detail", slug=slug)


def dislike_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    rating, created = Rating.objects.get_or_create(
        user=request.user, article=article,
        defaults={"value": -1}
    )

    if not created:
        rating.value = -1
        rating.save()

    return redirect("articles:article_detail", slug=slug)


@admin_required
def moderation_list(request):
    if not request.user.is_admin():
        return HttpResponseForbidden()

    articles = Article.objects.filter(status="pending").order_by("-created_at")
    return render(request, "articles/moderation_list.html", {"articles": articles})


@admin_required
@require_POST
def approve_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.status = "approved"
    article.save()

    Notification.objects.create(
        user=article.author,
        article=article,
        type="approved",
        message=f"Your article «{article.title}» has been approved 🎉"
    )

    ModerationLog.objects.create(
        article=article,
        moderator=request.user,
        action="approved"
    )

    messages.success(request, "Article approved")

    return redirect("articles:moderation_list")


@admin_required
@require_POST
def reject_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    reason = request.POST.get("reason")
    article.status = "rejected"
    article.moderation_comment = reason
    article.save()

    Notification.objects.create(
        user=article.author,
        article=article,
        type="rejected",
        message=f"Your article «{article.title}» was rejected ❌"
    )

    ModerationLog.objects.create(
        article=article,
        moderator=request.user,
        action="rejected"
    )

    messages.warning(request, "Article rejected")

    return redirect("articles:moderation_list")


@login_required
def my_articles(request):
    articles = Article.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "articles/my_articles.html", {"articles": articles})


@admin_required
def moderation_log(request):
    logs = ModerationLog.objects.select_related(
        "article", "moderator"
    ).order_by("-created_at")

    return render(request, "articles/moderation_log.html", {
        "logs": logs
    })
