from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
#from chat import routing as chat_routing
from voice_report import routing as voice_report_routing


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            #chat_routing.websocket_urlpatterns
            voice_report_routing.websocket_urlpatterns
        )
    ),
})
