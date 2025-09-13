"""
Script para verificar URLs del chat
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse, NoReverseMatch
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'social_network_backend.settings')
django.setup()


User = get_user_model()


def test_urls():
    print("🔗 Testing Chat URLs...")

    # URLs que deberían existir
    urls_to_test = [
        'chatroom-list',  # /api/v1/chat/rooms/
        'message-list',   # /api/v1/chat/messages/
        'onlinestatus-list',  # /api/v1/chat/online-status/
    ]

    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name}: {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name}: {e}")

    # Test específico para action endpoints
    try:
        # Necesitamos un ID de prueba para los detail endpoints
        print("\n🎯 Testing detail endpoints (need ID):")
        print("chatroom-join: Needs room ID")
        print("chatroom-leave: Needs room ID")
        print("chatroom-messages: Needs room ID")
        print("chatroom-direct-chat: Base URL + action")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    test_urls()
