from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from .views import CreateGame, MovePiece, JoinGame
from chess_api_project.users.models import User


factory = APIRequestFactory()


class TestAPI(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user_one = User.objects.create_user(
            username='whitey_morgan', password='django')
        self.user_two = User.objects.create_user(
            username="blackie_lawless", password="django")

        self.create_view = CreateGame.as_view()
        self.move_piece_view = MovePiece.as_view()
        self.join_game_view = JoinGame.as_view()

    def _create_game(self, preferred_color="random"):
        data = {"preferred_color": preferred_color}
        request = factory.post("/chess/game/", data, format="json")
        force_authenticate(request, user=self.user_one)

        return request

    def _join_game(self, uuid, user, preferred_color="random"):
        data = {
            "uuid": uuid,
            "preferred_color": preferred_color,
        }

        join_request = factory.put("/chess/game/join/", data, format="json")
        force_authenticate(join_request, user=user)
        
        return join_request

    def test_can_join_game(self):
        """
        Test second user is able to join the game
        """

        game_request = self._create_game(preferred_color="white")
        game = self.create_view(game_request)

        join_request = self._join_game(game.data.get("uuid"), self.user_two)

        response = self.join_game_view(join_request)

        self.assertEqual(self.user_two.username, response.data.get(
            "blacks_player", {}).get("username"))

    def test_game_creation(self):
        """
        Create a game
        """

        game_request = self._create_game()
        response = self.create_view(game_request)

        self.assertIn("board", response.data)

    def test_players_can_move_their_pieces(self):
        game_request = self._create_game(preferred_color="white")
        game = self.create_view(game_request)

        first_move = {
            "uuid": game.data.get("uuid"),
            "from_square": "e2",
            "to_square": "e4",
        }

        second_move = {
            "uuid": game.data.get("uuid"),
            "from_square": "e7",
            "to_square": "e5",
        }

        # First player (whites)
        request_whites = factory.put(
            "/chess/game/move/", first_move, format="json")

        force_authenticate(request_whites, user=self.user_one)

        response_whites = self.move_piece_view(request_whites)

        join_request = self._join_game(game.data.get("uuid"), self.user_two,
                        preferred_color="black")
        self.join_game_view(join_request)
        
        request_blacks = factory.put(
            "/chess/game/move/", second_move, format="json")

        force_authenticate(request_blacks, user=self.user_two)

        response_blacks = self.move_piece_view(request_blacks)

        print(response_blacks.data)

        self.assertIn("uuid", response_whites.data)
        self.assertIn("uuid", response_blacks.data)
