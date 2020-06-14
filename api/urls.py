# posts/urls.py
from django.urls import path
from .views import CreateGame, MovePiece, JoinGame

urlpatterns = [
    path('game/', CreateGame.as_view()),
    path('game/move/', MovePiece.as_view()),
    path('game/join/', JoinGame.as_view()),
]
