import random
import uuid

import chess
from django.contrib.auth import get_user_model
from django.utils import timezone

from .constants import K_FACTOR
from .models import Board, Game, Move, Result

RESULTS_DICT = {
    "1-0": Result.WHITE_WINS,
    "1/2-1/2": Result.DRAW,
    "0-1": Result.BLACK_WINS,
}

User = get_user_model()


def is_game_over(game_instance):
    """
    Update the game if it is over
    Return True if the game is over, False if it is not
    """

    chess_board = chess_board_from_uuid(game_instance.uuid)

    if chess_board.is_game_over():
        finish_game(game_instance, chess_board)
        return True

    return False


def finish_game(game_instance, chess_board):
    result_string = chess_board.result()
    game_instance.result = Result(
        result=RESULTS_DICT.get(result_string), termination=Result.NORMAL
    )
    game_instance.finished_at = timezone.now()
    game_instance.result.save()
    game_instance.save()


def assign_color(game_instance, username, preferred_color="white"):
    player_color = "white"

    if game_instance.whites_player and game_instance.blacks_player:
        return "full"

    if game_instance.whites_player or game_instance.blacks_player:
        player_color = "white" if game_instance.blacks_player else "black"

    elif not game_instance.whites_player and not game_instance.blacks_player:
        player_color = preferred_color

        if preferred_color == "random":
            player_color = "black" if random.randint(0, 1) == 1 else "white"

    auth_user = User.objects.get(username=username)

    if player_color == "black":
        game_instance.blacks_player = auth_user

    else:
        game_instance.whites_player = auth_user

    game_instance.save()

    return player_color


# Board


def move_piece(board_instance, from_square, to_square, chess_board=None):
    """
    Make a move if it is legal, and check if the game is over
    """

    if not chess_board:
        chess_board = chess_board_from_uuid(board_instance.game_uuid)

    requested_move = chess.Move.from_uci(f"{from_square}{to_square}")

    if requested_move in chess_board.legal_moves:
        chess_board.push(requested_move)

        Move.objects.create(
            from_square=from_square, to_square=to_square, board=board_instance
        )

        board_instance.update(chess_board)

        if hasattr(board_instance, "game"):
            is_game_over(board_instance.game)

        return requested_move

    return None


def chess_board_from_uuid(board_uuid):
    """
    It's safe to set turn, castling_rights, ep_square, halfmove_clock and fullmove_number directly.

    https://python-chess.readthedocs.io/en/latest/core.html#chess.Board
    """

    board = Board.objects.get(game_uuid=board_uuid)

    chess_board = chess.Board(board.fen)

    chess_board.ep_square = int(board.ep_square) if board.ep_square else None
    chess_board.turn = board.turn
    chess_board.castling_rights = int(board.castling_rights)
    chess_board.fullmove_number = board.fullmove_number
    chess_board.halfmove_clock = board.halfmove_clock
    chess_board.move_stack = board.move_stack

    return chess_board


def create_board_from_pgn(pgn_file, starting_at=0):
    board_instance = None
    chess_board = None

    with open(pgn_file, "r") as f:
        chess_game = chess.pgn.read_game(f)
        chess_board = chess_game.board()

        board_instance = Board.from_fen(chess_board.fen())
        board_instance.save()

        if starting_at:
            move_ucis = [i.move.uci() for i in chess_game.mainline()][:starting_at]

            for u in move_ucis:
                move_piece(board_instance, u[:2], u[2:], chess_board=chess_board)

    return (board_instance, chess_board)


# ELO


def _get_expected_score(player_rating, opponent_rating):
    """
    https://wikimedia.org/api/rest_v1/media/math/render/svg/51346e1c65f857c0025647173ae48ddac904adcb

    Returns the expected score rounded to two decimals

    For instance, a player with 100 less ELO points than their opponent has an expected score
    of 0.35993500019711494, which is rounded to 0.36 (a 36% 'chance' of winning)
    """

    expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

    return round(expected_score, 2)


def get_rating(player_score, player_rating, opponent_rating):
    expected_score = _get_expected_score(player_rating, opponent_rating)

    return round(player_rating + K_FACTOR * (player_score - expected_score))


def update_elo_rating(player_score=None, player=None, opponent=None, previous=False):
    """
    https://wikimedia.org/api/rest_v1/media/math/render/svg/09a11111b433582eccbb22c740486264549d1129

    Update a player's rating after a game 

    score: [0 | 0.5 | 1]

    The second player to be updated should set previous=True. When previous is True
    the ELO will be calculated based on their opponent's ELO before the game
    """

    if (
        player_score is not None
        and isinstance(player, User)
        and isinstance(opponent, User)
    ):
        opponent_rating = (
            opponent.elo.rating if previous is False else opponent.elo.previous_rating
        )
        new_rating = get_rating(player_score, player.elo.rating, opponent_rating)

        player.elo.update_rating(new_rating)

    return player.elo.rating


def update_elo(game_instance):
    """
    Update the ELO of a game's players according to the game's result
    Returns: white_elo, black_elo
    """

    white = game_instance.whites_player
    black = game_instance.blacks_player

    scores = {
        "white": 0,
        "black": 0,
    }

    result = game_instance.result.result

    if result == Result.DRAW:
        scores["white"] += 0.5
        scores["black"] += 0.5
        white.elo.draws += 1
        black.elo.draws += 1

    elif result == Result.WHITE_WINS:
        scores["white"] += 1
        white.elo.wins += 1
        black.elo.losses += 1

    elif result == Result.BLACK_WINS:
        scores["black"] += 1
        black.elo.wins += 1
        white.elo.losses += 1

    white.elo.save()
    black.elo.save()

    update_elo_rating(player_score=scores["white"], player=white, opponent=black)

    update_elo_rating(
        player_score=scores["black"], player=black, opponent=white, previous=True
    )

    return white.elo, black.elo


# GAME


def create_game(result_data=None, board_data=None, **validated_data):
    game_uuid = uuid.uuid4()

    chess_game = chess.Board()

    board_object = Board.objects.create(
        **board_data,
        fen=chess.STARTING_FEN,
        castling_rights=chess_game.castling_rights,
        game_uuid=game_uuid,
    )

    result_object = Result.objects.create(**result_data)

    game = Game.objects.create(
        result=result_object, board=board_object, uuid=game_uuid, **validated_data
    )

    return game
