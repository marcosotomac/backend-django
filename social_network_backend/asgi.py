"""
ASGI config for social_network_backend project.
Configuración para manejar tanto HTTP como WebSockets
"""
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'social_network_backend.settings')

# Inicializar Django ASGI application primero
django_asgi_app = get_asgi_application()

# Importar después de inicializar Django

# Combinar todas las rutas WebSocket
websocket_urlpatterns = chat_websocket_urlpatterns + \
    notifications_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
