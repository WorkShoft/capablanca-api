import random
import uuid

import chess
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Result, Game, Board


def is_game_over(game_instance):
    """
    Update the game if it is over
    Return True if the game is over, False if it is not
    """
    results_dict = {
        '1-0': Result.WHITE_WINS,
        '1/2-1/2': Result.DRAW,
        '0-1': Result.BLACK_WINS,
    }

    board = chess.Board(game_instance.board.fen)

    if board.is_game_over():
        result_string = board.result()
        game_instance.result = Result(result=results_dict.get(
            result_string), termination=Result.NORMAL)
        game_instance.finished_at = timezone.now()
        game_instance.result.save()
        game_instance.save()
        return True

    return False


def assign_color(game_instance, username, preferred_color='white'):
    player_color = 'white'

    if game_instance.whites_player and game_instance.blacks_player:
        return 'full'

    if game_instance.whites_player or game_instance.blacks_player:
        player_color = 'white' if game_instance.blacks_player else 'black'

    elif not game_instance.whites_player and not game_instance.blacks_player:
        player_color = preferred_color

        if preferred_color == 'random':
            player_color = 'black' if random.randint(
                0, 1) == 1 else 'white'

    User = get_user_model()
    auth_user = User.objects.get(username=username)

    if player_color == 'black':
        game_instance.blacks_player = auth_user

    else:
        game_instance.whites_player = auth_user

    game_instance.save()

    return player_color


def move_piece(board_instance, from_square, to_square):
    """
    Make a move if it is legal, and check if the game is over
    """
    board = chess.Board(board_instance.fen)

    requested_move = chess.Move.from_uci(f"{from_square}{to_square}")

    if requested_move in board.legal_moves:
        board.push(requested_move)
        board_instance.fen = board.fen()

        board_instance.save()
        is_game_over(board_instance.game)

        return requested_move

    return None

# ELO
def get_expected_score(elo_instance, opponent_rating):
    """
    https://wikimedia.org/api/rest_v1/media/math/render/svg/51346e1c65f857c0025647173ae48ddac904adcb
    """

    return 1 / (1 + 10**((opponent_rating - elo_instance.rating) / 400))


def update_rating(elo_instance, score, opponent_rating):
    """
    https://wikimedia.org/api/rest_v1/media/math/render/svg/09a11111b433582eccbb22c740486264549d1129

    Update rating after a single game (score should be either 0, 0.5 or 1)
    """

    expected_score = elo_instance.get_expected_score(opponent_rating)
    elo_instance.rating = round(
        elo_instance.rating + elo_instance.k_factor * (score - expected_score))
    elo_instance.save()


def create_game(result_data=None, board_data=None, **validated_data):
    game_uuid = uuid.uuid4()

    board_object = Board.objects.create(
        **board_data, fen=chess.STARTING_FEN, game_uuid=game_uuid)

    result_object = Result.objects.create(
        **result_data)

    game = Game.objects.create(
        result=result_object,
        board=board_object,
        uuid=game_uuid,
        **validated_data
    )

    return game
