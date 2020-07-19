import pytest
import chess

from api.models import Board


def test_board_from_fen():
    chess_board = chess.Board()
    fen = chess_board.fen()
    board = Board.from_fen(fen)

    assert board.ep_square is None
    assert board.halfmove_clock == 0
    assert board.fullmove_number == 1
    assert board.castling_xfen == "KQkq"


@pytest.mark.django_db
def test_get_empty_move_stack():
    board = Board()

    assert board.move_stack == []


@pytest.mark.django_db
def test_board_model_string():
    board = Board()
    assert str(board) == board.fen
