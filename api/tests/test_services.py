import chess
import pytest

from api import services
from api.models import Board, Move


@pytest.mark.django_db
def test_chess_board_from_uuid():
    """
    Test a python-chess Board can be fully recovered from a Board model instance
    by providing the game uuid
    """

    # Create board and make two moves
    chess_board = chess.Board()
    board_instance = Board.from_fen(chess_board.fen())
    board_instance.save()

    first_move = "e2e4"
    second_move = "e7e5"

    services.move_piece(board_instance, first_move[:2], first_move[2:], chess_board=chess_board)
    services.move_piece(board_instance, second_move[:2], second_move[2:], chess_board=chess_board)

    new_chess_board = services.chess_board_from_uuid(board_instance.game_uuid)

    assert(chess_board.ep_square == int(new_chess_board.ep_square))
    assert(chess_board.castling_rights == int(new_chess_board.castling_rights))
    assert(chess_board.turn == new_chess_board.turn)
    assert(chess_board.fullmove_number == new_chess_board.fullmove_number)
    assert(chess_board.halfmove_clock == new_chess_board.halfmove_clock)
    assert(chess_board.move_stack == new_chess_board.move_stack)
    
