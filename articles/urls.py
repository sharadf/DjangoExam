from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [

    path("my/", views.my_articles, name="my_articles"),

    path("moderation/", views.moderation_list, name="moderation_list"),
    path("article/<int:pk>/approve/", views.approve_article, name="approve_article"),
    path("article/<int:pk>/reject/", views.reject_article, name="reject_article"),

    path("moderation/logs/", views.moderation_log, name="moderation_log"),

    path("create/new/", views.article_create, name="article_create"),

    path("<slug:slug>/", views.article_detail, name="article_detail"),
    path("<slug:slug>/edit/", views.article_edit, name="article_edit"),
    path("<slug:slug>/delete/", views.article_delete, name="article_delete"),
    path("article/<slug:slug>/like/", views.like_article, name="like_article"),
    path("article/<slug:slug>/dislike/", views.dislike_article, name="dislike_article"),

    path("", views.article_list, name="article_list")
]
