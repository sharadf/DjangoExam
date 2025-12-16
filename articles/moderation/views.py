# from django.shortcuts import render
#
# from exDjango.articles.models import Article
# from exDjango.users.permission import admin_required
#
#
# @admin_required
# def moderation_list(request):
#     articles = Article.objects.filter(approved=False).order_by("-created_at")
#
#     return render(request, "articles/moderation_list.html", {"articles": articles})
