from django.urls import path

from .consumers import ScoreboardConsumer

websocket_urlpatterns = [path("ws/scoreboard/", ScoreboardConsumer.as_asgi()), ]
