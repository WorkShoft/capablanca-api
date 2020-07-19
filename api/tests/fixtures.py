import pytest
import chess

from api import services
from api.models import Board, Game, Result


JWT_TOKEN = {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU5NTIzMjMxMCwianRpIjoiMTViM2ZiZGNhODJlNDBiMDkyNTBiYzA5ZTlkODQwMmYiLCJ1c2VyX2lkIjoxfQ.3UZIhcS4X14zb9V7wRnf0G3TJ1f7G6UMijThokvOD_M",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTk1MTQ1OTIyLCJqdGkiOiI1ODBjNmM3ZDcyNTk0NmJmOWJiNGY1YmMyMzcyMjY0MiIsInVzZXJfaWQiOjF9.44RKjIbKXmWqjzJA0TtpbnBTt3-3tAMxUP1EZDMJais",
}

CHESS_BOARD = chess.Board()
BOARD_INSTANCE = Board.from_fen(CHESS_BOARD.fen())


@pytest.fixture
def users():
    user_one = services.User.objects.create(
        username="walterwhite",
        name="Walter Hartwell White",
        email="walter@graymatter.tech",
        password="albuquerque1992",
        is_active=True,
    )

    user_two = services.User.objects.create(
        username="jessepinkman",
        name="Jesse Bruce Pinkman",
        email="jesseyo@outlook.com",
        password="therealog",
        is_active=True,
    )

    return user_one, user_two


@pytest.fixture
def game_instance(users):
    player, opponent = users

    return Game(
        board=BOARD_INSTANCE,
        whites_player=player,
        blacks_player=opponent,
        result=Result(result=Result.BLACK_WINS, termination=Result.NORMAL),
    )
