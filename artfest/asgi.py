import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artfest.settings')

import core.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({"http": get_asgi_application(),
                                  "websocket": AuthMiddlewareStack(URLRouter(core.routing.websocket_urlpatterns)), })
