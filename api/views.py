from rest_framework import generics, mixins
from .models import Game, Player
from .serializers import GameSerializer, PlayerSerializer


class CreateGame(mixins.RetrieveModelMixin, generics.CreateAPIView):
    serializer_class = GameSerializer

    def get_object(self):
        return Game.objects.get(uuid=self.request.GET.get('uuid'))

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CreatePlayer(generics.CreateAPIView):
    serializer_class = PlayerSerializer
