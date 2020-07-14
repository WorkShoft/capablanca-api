from django.urls import path
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack

import django_eventstream


urlpatterns = [
    path("events/", AuthMiddlewareStack(
        URLRouter(django_eventstream.routing.urlpatterns)
    ), {"channels": ["test"]}),
]
