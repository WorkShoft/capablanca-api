# posts/urls.py
from django.urls import path
from .views import CreateGame, CreatePlayer

urlpatterns = [
    path('game/', CreateGame.as_view()),
    path('player/', CreatePlayer.as_view())
]
