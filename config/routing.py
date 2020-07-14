from channels.routing import ProtocolTypeRouter, URLRouter
from api import routing

application = ProtocolTypeRouter({
    'http': URLRouter(routing.urlpatterns),
})
