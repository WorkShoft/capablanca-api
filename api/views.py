from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import Game
from .permissions import GamePermission
from .serializers import GameSerializer

User = get_user_model()


class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()

    permission_classes = [
        GamePermission,
    ]

    @action(detail=True, methods=["put"])
    def move(self, request, *args, **kwargs):
        """
        Move a piece
        """

        from_square = request.data.get("from_square")
        to_square = request.data.get("to_square")

        game_uuid = kwargs.get("pk")

        game = get_object_or_404(Game, uuid=game_uuid)

        board = game.board
        auth_user = User.objects.get(username=request.user)

        self.check_object_permissions(self.request, game)

        move = services.move_piece(board, from_square, to_square)

        if move:
            return Response(self.serializer_class(game).data)

        else:
            return Response(
                data={"detail": f"{from_square}{to_square} is not a valid move."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["put"])
    def join(self, request, *args, **kwargs):
        """
        Join a game 
        """

        game_uuid = kwargs.get("pk")
        preferred_color = request.data.get("preferred_color")

        game = get_object_or_404(Game, uuid=game_uuid)

        services.assign_color(game, request.user, preferred_color=preferred_color)

        serialized_game = GameSerializer(game).data

        return Response(data=serialized_game, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def get_unfinished_games(self, request, *args, **kwargs):
        """
        Get a list of unfinished games played by the user
        """

        user = self.request.user
        games = Game.objects.filter(Q(whites_player=user) | Q(blacks_player=user))

        page = self.paginate_queryset(games)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serialized_games = self.get_serializer(games, many=True).data
        return Response(data=serialized_games)
