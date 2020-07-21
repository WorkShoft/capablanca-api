from channels.db import database_sync_to_async
from api.models import Game
from api.serializers import GameSerializer


@database_sync_to_async
def get_serialized_game(uuid):
    game = Game.objects.get(uuid=uuid)
    return GameSerializer(game).data
