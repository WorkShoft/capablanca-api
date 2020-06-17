import chess
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model

from . import services
from .models import Game
from .permissions import PiecePermission 
from .serializers import GameSerializer, BoardSerializer, UserSerializer


User = get_user_model()


class CreateGame(mixins.RetrieveModelMixin, generics.CreateAPIView):
    serializer_class = GameSerializer

    def get_object(self):
        return Game.objects.get(uuid=self.request.GET.get('uuid'))

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class MovePiece(generics.UpdateAPIView):
    serializer_class = GameSerializer
    permission_classes = [PiecePermission]

    def update(self, request, *args, **kwargs):
        from_square = request.data.get('from_square')
        to_square = request.data.get('to_square')

        game_uuid = request.data.get('uuid')
        game = get_object_or_404(Game, uuid=game_uuid)

        board = game.board
        auth_user = User.objects.get(username=request.user)

        self.check_object_permissions(self.request, game)

        move = services.move_piece(board, from_square, to_square)

        if move:
            return Response(data=self.serializer_class(game).data, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(data={'message': f'{from_square}{to_square} is not a valid move.'}, status=status.HTTP_400_BAD_REQUEST)


class JoinGame(generics.UpdateAPIView):
    serializer_class = GameSerializer

    def update(self, request, *args, **kwargs):
        game_uuid = request.data.get('uuid')
        preferred_color = request.data.get('preferred_color')

        game = get_object_or_404(Game, uuid=game_uuid)

        services.assign_color(game, request.user,
                              preferred_color=preferred_color)

        serialized_game = GameSerializer(game).data
        return Response(data=serialized_game, status=status.HTTP_204_NO_CONTENT)
