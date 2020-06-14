import chess
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Game
from .serializers import GameSerializer, BoardSerializer, UserSerializer


class CreateGame(mixins.RetrieveModelMixin, generics.CreateAPIView):
    serializer_class = GameSerializer

    def get_object(self):
        return Game.objects.get(uuid=self.request.GET.get('uuid'))

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class MovePiece(generics.UpdateAPIView):
    serializer_class = BoardSerializer

    def get_queryset(self, request, *args, **kwargs):
        game_uuid = request.data.get('uuid')
        return get_object_or_404(Board, game_uuid=game_uuid)

    def update(self, request, *args, **kwargs):
        game_uuid = request.data.get('uuid')
        game = get_object_or_404(Game, uuid=game_uuid)

        from_square = request.data.get('from_square')
        to_square = request.data.get('to_square')

        board = game.board

        move = board.move(from_square, to_square)

        if move:
            serialized_board = BoardSerializer(board).data
            return Response(data=serialized_board, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(data={'message': f'{from_square}{to_square} is not a valid move.'}, status=status.HTTP_400_BAD_REQUEST)

    def player_owns_piece(request, from_square):
        """
        Returns True if the piece at from_square belongs to the user
        TODO: Finish code!
        """

        square = getattr(chess, from_square.upper())
        piece = self.board.piece_at(square)
        piece_symbol = str(piece)

        # Check piece color (Board.BLACK_PIECES / Board.WHITE_PIECES)
        # Check if player is whites_player or blacks_player
        # return True or False
        
