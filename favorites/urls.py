from django.urls import path
from . import views

app_name = "favorites"

urlpatterns = [
    path("add/<int:article_id>/", views.add_favorite, name="add"),
    path("remove/<int:article_id>/", views.remove_favorite, name="remove"),
    path("", views.favorite_list, name="list")
]
