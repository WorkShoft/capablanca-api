import chess.pgn

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from api.views import GameViewSet
from api.models import Game, Result


factory = APIRequestFactory()


class TestAPI(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user_one = User.objects.create_user(
            username="whitey_morgan", password="django"
        )
        self.user_two = User.objects.create_user(
            username="blackie_lawless", password="django"
        )

        self.game_create_view = GameViewSet.as_view({"post": "create",})
        self.game_list_view = GameViewSet.as_view({"get": "list",})
        self.game_detail_view = GameViewSet.as_view({"get": "retrieve",})
        self.join_game_view = GameViewSet.as_view({"put": "join",})
        self.move_piece_view = GameViewSet.as_view({"put": "move",})

    def _create_game(self, preferred_color="random"):
        data = {"preferred_color": preferred_color}
        request = factory.post("/chess/game/", data)
        force_authenticate(request, user=self.user_one)

        return self.game_create_view(request)

    def _get_game(self, uuid, user):
        get_request = factory.get(f"/chess/game/{uuid}/")
        force_authenticate(get_request, user=user)

        return self.game_detail_view(get_request, pk=uuid)

    def _join_game(self, uuid, user, preferred_color="random"):
        data = {
            "preferred_color": preferred_color,
        }

        join_request = factory.put(f"/chess/game/{uuid}/join/", data)
        force_authenticate(join_request, user=user)

        response = self.join_game_view(join_request, pk=uuid)

        return response

    def _move_piece(self, uuid, move, user):
        request = factory.put(f"/chess/game/{uuid}/move/", move)

        force_authenticate(request, user=user)

        response = self.move_piece_view(request, pk=uuid)

        return response

    def test_can_create_game(self):
        """
        Create a game
        """

        response = self._create_game()

        self.assertIn("board", response.data)

    def test_can_retrieve_game(self):
        """
        Retrieve a game
        """

        game_response = self._create_game()

        get_response = self._get_game(game_response.data.get("uuid"), self.user_one)

        self.assertEqual(game_response.data.get("uuid"), get_response.data.get("uuid"))

    def test_can_join_game(self):
        """
        Test second user is able to join the game
        """

        game_response = self._create_game(preferred_color="white")

        response = self._join_game(game_response.data.get("uuid"), self.user_two)

        self.assertEqual(
            self.user_two.username,
            response.data.get("blacks_player", {}).get("username"),
        )

    def test_players_can_move_their_pieces(self):
        response = self._create_game(preferred_color="white")

        first_move = {
            "from_square": "e2",
            "to_square": "e4",
        }

        second_move = {
            "from_square": "e7",
            "to_square": "e5",
        }

        # First player (whites)

        response_whites = self._move_piece(
            response.data.get("uuid"), first_move, self.user_one
        )

        self._join_game(
            response.data.get("uuid"), self.user_two, preferred_color="black"
        )

        response_blacks = self._move_piece(
            response.data.get("uuid"), second_move, self.user_two
        )

        self.assertIn("uuid", response_whites.data)
        self.assertIn("uuid", response_blacks.data)

    def test_players_can_only_move_pieces_they_own(self):
        response = self._create_game(preferred_color="white")

        # Attempt to move a black pawn as a white player
        move = {
            "from_square": "e7",
            "to_square": "e5",
        }

        response = self._move_piece(response.data.get("uuid"), move, self.user_one)

        self.assertIn("detail", response.data)
        self.assertEqual(
            "You can't move a piece at that square", response.data["detail"]
        )

    def test_only_valid_moves_are_allowed(self):
        response = self._create_game(preferred_color="white")

        # Attempt an illegal move
        move = {
            "from_square": "e2",
            "to_square": "e6",
        }

        response = self._move_piece(response.data.get("uuid"), move, self.user_one)

        self.assertIn("message", response.data)
        self.assertEqual(
            "{from_square}{to_square} is not a valid move.".format(
                from_square=move["from_square"], to_square=move["to_square"]
            ),
            response.data["message"],
        )

    def test_non_player_users_cant_play(self):
        response = self._create_game(preferred_color="white")

        # Attempt to move a black pawn before joining the game
        move = {
            "from_square": "e5",
            "to_square": "e7",
        }

        response = self._move_piece(response.data.get("uuid"), move, self.user_two)

        self.assertIn("detail", response.data)
        self.assertEqual(
            "You can't move a piece at that square", response.data["detail"]
        )

    def test_game_end(self):
        moves = []

        # Create board and game from PGN
        with open("api/pgn_games/fools_mate.pgn") as f:
            game_pgn = chess.pgn.read_game(f)
            moves = [move for move in game_pgn.mainline_moves()]

        # Create game
        response = self._create_game(preferred_color="white")
        game_uuid = response.data.get("uuid")

        # Second player joins
        self._join_game(game_uuid, self.user_two, preferred_color="black")

        # Play all moves
        for counter, move in enumerate(moves):
            uci = move.uci()
            from_square = uci[:2]
            to_square = uci[2:]

            move = {
                "from_square": from_square,
                "to_square": to_square,
            }

            user = self.user_one if counter % 2 == 0 else self.user_two
            self._move_piece(game_uuid, move, user)

        game = Game.objects.get(uuid=game_uuid)

        self.assertEqual(Result.BLACK_WINS, game.result.result)
        self.assertEqual(Result.NORMAL, game.result.termination)
