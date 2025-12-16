from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Favorite
from articles.models import Article


@login_required
def add_favorite(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    Favorite.objects.get_or_create(user=request.user, article=article)
    return redirect("articles:article_detail", slug=article.slug)


@login_required
def remove_favorite(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    Favorite.objects.filter(user=request.user, article=article).delete()
    return redirect("articles:article_detail", slug=article.slug)


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, "favorites/favorite_list.html", {"favorites": favorites})
