"""
URLs para las APIs del sistema de chat
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'online-status', views.OnlineStatusViewSet,
                basename='onlinestatus')

urlpatterns = [
    path('api/chat/', include(router.urls)),
]
