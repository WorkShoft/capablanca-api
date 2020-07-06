# posts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GameViewSet


game_list = GameViewSet.as_view({"get": "list",})

game_detail = GameViewSet.as_view({"get": "detail",})

router = DefaultRouter()
router.register(r"game", GameViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
