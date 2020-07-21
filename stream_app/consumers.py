import json

from api.models import Game

from channels.generic.websocket import AsyncWebsocketConsumer

from stream_app.services import get_serialized_game


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.game_group_name = f"game_{self.uuid}"

        # Join room group
        await self.channel_layer.group_add(
            self.game_group_name, self.channel_name
        )
    
        await self.accept()

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        
        if "update" in data_json:
            game = await get_serialized_game(data_json.get("uuid"))

            # Update both players' game data
            await self.channel_layer.group_send(
                self.game_group_name, {"type": "game_data", "game": game, }
            )
        
    async def game_data(self, data):
        game = data["game"]

        # Send game over WebSocket
        await self.send(text_data=json.dumps(game))

    async def disconnect(self, *args, **kwargs):
        await self.channel_layer.group_discard(
            self.game_group_name, self.channel_name
        )
    
