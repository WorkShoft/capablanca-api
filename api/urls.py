# posts/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GameViewSet

router = DefaultRouter()
router.register(r"game", GameViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
