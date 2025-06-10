from django.urls import re_path
from chat.routing import websocket_urlpatterns

application = websocket_urlpatterns 