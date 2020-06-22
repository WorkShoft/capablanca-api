# posts/urls.py
from django.urls import path
from .views import GetCreateGame, MovePiece, JoinGame

urlpatterns = [
    path('game/', GetCreateGame.as_view()),
    path('game/board/move/', MovePiece.as_view()),
    path('game/join/', JoinGame.as_view()),
]
