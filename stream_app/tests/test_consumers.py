import pytest
import json

from uuid import uuid4
from unittest import mock

from channels.testing import WebsocketCommunicator
from stream_app.consumers import GameConsumer


from api.models import Game

from stream_app.tests.fixtures import GAME_UUID


@pytest.mark.asyncio
@pytest.fixture
def url_route():
    return {
        "kwargs": {"uuid": str(uuid4()),},
    }


@pytest.mark.asyncio
@pytest.fixture
def game_communicator(url_route):
    game_uuid = url_route["kwargs"]["uuid"]
    communicator = WebsocketCommunicator(GameConsumer, f"/ws/game/{game_uuid}/")
    communicator.scope["url_route"] = url_route

    return communicator


@pytest.mark.asyncio
async def test_connect(game_communicator):
    connected, _ = await game_communicator.connect()

    assert connected

    await game_communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_receive(game_communicator):
    connected, _ = await game_communicator.connect()

    Game.objects.get = mock.MagicMock(return_value=Game(uuid=GAME_UUID))

    await game_communicator.send_to(json.dumps({"update": "foo"}))
    received_message = await game_communicator.receive_json_from()

    assert received_message["uuid"] == GAME_UUID

    await game_communicator.disconnect()


@pytest.mark.asyncio
async def test_routing():
    from stream_app import routing

    assert routing.websocket_urlpatterns is not None
