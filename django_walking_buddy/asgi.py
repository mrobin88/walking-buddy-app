"""
ASGI config for walking_buddy project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_walking_buddy.settings')

django_asgi_app = get_asgi_application()

def get_application():
    from chat.middleware import JWTAuthMiddleware
    from chat.routing import websocket_urlpatterns

    return ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })

application = get_application()