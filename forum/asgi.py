"""
ASGI config for forum project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from livechat.middlewares import WebSocketJWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from livechat.routing import websocket_urlpatterns  # Adjust the import according to your app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": WebSocketJWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
