from unittest import mock

import chess
import chess.pgn
import pytest
from api import services
from api.models import Board, Game, Result
from fixtures import users, game_instance


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

    services.move_piece(
        board_instance, first_move[:2], first_move[2:], chess_board=chess_board
    )
    services.move_piece(
        board_instance, second_move[:2], second_move[2:], chess_board=chess_board
    )

    new_chess_board = services.chess_board_from_uuid(board_instance.game_uuid)

    assert chess_board.ep_square == int(new_chess_board.ep_square)
    assert chess_board.castling_rights == int(new_chess_board.castling_rights)
    assert chess_board.turn == new_chess_board.turn
    assert chess_board.fullmove_number == new_chess_board.fullmove_number
    assert chess_board.halfmove_clock == new_chess_board.halfmove_clock
    assert chess_board.move_stack == new_chess_board.move_stack
    assert chess_board.fen() == new_chess_board.fen()
    assert chess_board.board_fen() == new_chess_board.board_fen()


@pytest.mark.django_db
def test_create_board_from_pgn():
    board_instance, chess_board = services.create_board_from_pgn(
        "api/pgn_games/fools_mate.pgn", starting_at=0
    )

    assert board_instance.fen == chess.STARTING_FEN
    assert chess_board.fen() == chess.STARTING_FEN


@pytest.mark.django_db
def test_create_board_from_pgn_starting_at():
    board_instance, chess_board = services.create_board_from_pgn(
        "api/pgn_games/fools_mate.pgn", starting_at=4
    )

    assert board_instance.fullmove_number == 3
    assert chess_board.is_checkmate()


@pytest.mark.django_db
def test_get_expected_score():
    player_rating = 1200
    opponent_rating = 1300

    expected_player_score = services._get_expected_score(player_rating, opponent_rating)

    expected_opponent_score = services._get_expected_score(
        opponent_rating, player_rating
    )

    assert expected_player_score == 0.36
    assert expected_opponent_score == 0.64


@pytest.mark.django_db
@mock.patch("api.services.K_FACTOR", 32)
def test_get_rating(users):
    player, opponent = users

    rating = services.get_rating(1, player.elo.rating, opponent.elo.rating)

    assert rating == 1216


@pytest.mark.django_db
@mock.patch("api.services.K_FACTOR", 32)
def test_update_elo_rating(users):
    player, opponent = users

    new_rating = services.update_elo_rating(
        player_score=1, player=player, opponent=opponent
    )

    assert new_rating == 1216
    assert player.elo.rating == 1216


@pytest.mark.django_db
def test_update_elo(users):
    """
    Test ELO is recalculated correctly
    The default result is Result(result=Result.WHITE_WINS, termination=Result.NORMAL)
    """

    player, opponent = users

    board_instance, _ = services.create_board_from_pgn(
        "api/pgn_games/fools_mate.pgn", starting_at=4
    )

    game = Game(
        board=board_instance,
        white_player=player,
        black_player=opponent,
        result=Result(result=Result.BLACK_WINS, termination=Result.NORMAL),
    )

    services.update_elo(game)

    assert player.elo.wins == 0
    assert opponent.elo.wins == 1

    assert player.elo.rating == 1184
    assert opponent.elo.rating == 1216


@pytest.mark.django_db
def test_update_elo_draw(users, game_instance):
    """
    game.result = Result(result=Result.DRAW, termination=Result.NORMAL)
    """

    player, opponent = users
    game = game_instance

    game.result = Result(result=Result.DRAW)
    game.result.save()

    services.update_elo(game)

    assert player.elo.draws == 1
    assert opponent.elo.draws == 1


@pytest.mark.django_db
def test_update_elo_white_wins(users, game_instance):
    """
    game.result = Result(result=Result.WHITE_WINS, termination=Result.NORMAL)
    """

    player, opponent = users
    game = game_instance

    game.result = Result(result=Result.WHITE_WINS)
    game.result.save()

    services.update_elo(game)

    assert player.elo.wins == 1
    assert opponent.elo.wins == 0
