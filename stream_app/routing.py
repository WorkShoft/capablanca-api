from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r"ws/game/<uuid>/", consumers.GameConsumer),
]
