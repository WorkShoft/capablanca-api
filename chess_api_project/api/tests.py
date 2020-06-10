from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from .models import Player
from .views import CreateGame
from chess_api_project.users.models import User

factory = APIRequestFactory()
#client = APIClient()


class TestAPI(TestCase):
    def test_game_creation(self):
        """
        Create a game with two guests
        """

        User = get_user_model()
        User.objects.create_user(username='mike', password='django')
        user = User.objects.get(username='mike')
        request = factory.post(path='/chess/game/', format='json')
        force_authenticate(request, user=user)

        view = CreateGame.as_view()
        response = view(request)

        self.assertIn('board', response.data)
