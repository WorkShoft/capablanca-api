import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from api.serializers import GameSerializer
from api.models import Game


class GameConsumer(WebsocketConsumer):
    serializer_class = GameSerializer

    def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.game_group_name = f"game_{self.uuid}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )

        self.accept()

    def receive(self, text_data):
        data_json = json.loads(text_data)

        if "update" in data_json:
            game = self.get_serialized_game()

            # Update both players' game data
            async_to_sync(self.channel_layer.group_send)(
                self.game_group_name, {"type": "game_data", "game": game,}
            )

    def game_data(self, data):
        game = data["game"]

        # Send game over WebSocket
        self.send(text_data=json.dumps(game))

    def disconnect(self):
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name, self.channel_name
        )

    def get_serialized_game(self):
        game = Game.objects.get(uuid=self.uuid)
        return self.serializer_class(game).data
