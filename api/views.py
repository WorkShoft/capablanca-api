import chess
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Game
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

    def get_queryset(self, request, *args, **kwargs):
        game_uuid = request.data.get('uuid')
        return get_object_or_404(Board, game_uuid=game_uuid)

    def update(self, request, *args, **kwargs):
        from_square = request.data.get('from_square')
        to_square = request.data.get('to_square')

        game_uuid = request.data.get('uuid')
        game = get_object_or_404(Game, uuid=game_uuid)

        board = game.board
        auth_user = User.objects.get(username=request.user)

        if not self.player_owns_piece(auth_user, from_square, game):
            return Response(data={'message': 'You can\'t move a piece at that square'}, status=status.HTTP_400_BAD_REQUEST)

        move = board.move(from_square, to_square)

        if move:
            return Response(data=self.serializer_class(game).data, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(data={'message': f'{from_square}{to_square} is not a valid move.'}, status=status.HTTP_400_BAD_REQUEST)

    def player_owns_piece(self, user, from_square, game):
        """
        Returns True if the piece at from_square belongs to the user
        python-chess Piece.color is True for white pieces
        """

        square = getattr(chess, from_square.upper())
        board = chess.Board(game.board.fen)

        piece = board.piece_at(square)

        if user in (game.whites_player, game.blacks_player):
            player_color = 'white' if user == game.whites_player else 'black'

        else:
            return False

        piece_color = 'white' if piece.color else 'black'

        return player_color == piece_color


class JoinGame(generics.UpdateAPIView):
    serializer_class = GameSerializer

    # def get_queryset(self, request, *args, **kwargs):
    #     game_uuid = request.data.get('uuid')
    #     return get_object_or_404(Board, game_uuid=game_uuid)

    def update(self, request, *args, **kwargs):
        game_uuid = request.data.get('uuid')
        preferred_color = request.data.get('preferred_color')

        game = get_object_or_404(Game, uuid=game_uuid)

        game.assign_color(request.user, preferred_color=preferred_color)

        serialized_game = GameSerializer(game).data
        return Response(data=serialized_game, status=status.HTTP_204_NO_CONTENT)
