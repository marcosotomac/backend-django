"""
Script de debugging para verificar endpoints del chat
"""
import os
import django
import requests
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'social_network_backend.settings')
django.setup()

User = get_user_model()


def debug_chat_endpoints():
    """Debug de endpoints del chat"""
    print("🔍 Debugeando endpoints del chat...")

    # Crear usuario de prueba
    user = User.objects.create_user(
        username='debuguser',
        email='debug@test.com',
        password='testpass123'
    )

    # Crear token
    token = str(RefreshToken.for_user(user).access_token)

    # Configurar cliente
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Probar endpoints básicos
    print("\n📋 Probando endpoints disponibles:")

    endpoints = [
        '/api/v1/chat/rooms/',
        '/api/v1/chat/messages/',
        '/api/v1/chat/online-status/',
    ]

    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            print(f"✅ GET {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ GET {endpoint} - Error: {e}")

    # Crear una sala para probar endpoints de detalle
    print("\n🏠 Creando sala de prueba...")

    room_data = {
        'name': 'Debug Room',
        'room_type': 'group',
        'description': 'Room for debugging'
    }

    response = client.post('/api/v1/chat/rooms/', room_data, format='json')
    print(f"Crear sala - Status: {response.status_code}")

    if response.status_code == 201:
        room_id = response.data['id']
        print(f"Room ID: {room_id}")

        # Probar endpoints específicos de la sala
        detail_endpoints = [
            f'/api/v1/chat/rooms/{room_id}/',
            f'/api/v1/chat/rooms/{room_id}/messages/',
            f'/api/v1/chat/rooms/{room_id}/join/',
            f'/api/v1/chat/rooms/{room_id}/leave/',
        ]

        for endpoint in detail_endpoints:
            try:
                # GET primero
                response = client.get(endpoint)
                print(f"✅ GET {endpoint} - Status: {response.status_code}")

                # POST para actions
                if 'join' in endpoint or 'leave' in endpoint:
                    response = client.post(endpoint)
                    print(
                        f"✅ POST {endpoint} - Status: {response.status_code}")

            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")

    print("\n" + "="*50)
    print("🎯 Debug completado")


if __name__ == '__main__':
    debug_chat_endpoints()
