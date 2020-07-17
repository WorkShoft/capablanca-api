# posts/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EloViewSet, GameViewSet

router = DefaultRouter()
router.register(r"game", GameViewSet)
router.register(r"elo", EloViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
