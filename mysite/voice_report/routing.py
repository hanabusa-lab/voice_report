# chat/routing.py
from django.urls import path

from . import consumers
from . import voice_report


websocket_urlpatterns = [
    path('ws/voice_report/', voice_report.VoiceConsumer),
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer),
]
