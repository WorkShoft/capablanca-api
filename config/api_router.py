from api.views import EloViewSet, GameViewSet
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from chess_api_project.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("users", UserViewSet)
router.register("game", GameViewSet)
router.register("elo", EloViewSet)

app_name = "api"
urlpatterns = router.urls
