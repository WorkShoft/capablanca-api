"""
API permissions for checks such as piece ownership
"""

import chess
from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class PiecePermission(permissions.BasePermission):
    """
    Check if a piece belongs to a player (who is, for instance, trying to move it)
    """

    def has_object_permission(self, request, view, obj):
        """
        Allow players to see each other's pieces
        Only allow the owner of a piece to move it (i.e. if you play as White you can only move white pieces)

        python-chess Piece.color is True for white pieces
        obj: Game instance
        """

        if request.method in permissions.SAFE_METHODS:
            return True

        from_square = request.data.get('from_square')
        square = getattr(chess, from_square.upper())
        board = chess.Board(obj.board.fen)
        user = User.objects.get(username=request.user)

        if user in (obj.whites_player, obj.blacks_player):
            player_color = 'white' if user == obj.whites_player else 'black'

        else:
            return False

        piece_color = 'white' if board.color_at(square) else 'black'

        return player_color == piece_color
