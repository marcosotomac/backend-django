#!/usr/bin/env python3
"""
Test manual para verificar que los participantes se agregan correctamente
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'


def test_chat_participants():
    print("🧪 TESTING: Crear chat grupal con participantes")
    print("=" * 50)

    try:
        # 1. Crear usuarios de prueba
        print("1. Creando usuarios de prueba...")

        users_data = [
            {
                'username': 'testuser1',
                'email': 'testuser1@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User1'
            },
            {
                'username': 'testuser2',
                'email': 'testuser2@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User2'
            },
            {
                'username': 'testuser3',
                'email': 'testuser3@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User3'
            }
        ]

        tokens = []

        for user_data in users_data:
            # Registrar usuario
            response = requests.post(
                f'{BASE_URL}/api/v1/auth/register/', json=user_data)
            if response.status_code == 201:
                print(f"   ✅ Usuario {user_data['username']} registrado")
            else:
                print(
                    f"   ⚠️ Usuario {user_data['username']} ya existe o error: {response.status_code}")

            # Login para obtener token
            login_data = {
                'username': user_data['username'],
                'password': user_data['password']
            }
            response = requests.post(
                f'{BASE_URL}/api/v1/auth/login/', json=login_data)
            if response.status_code == 200:
                token = response.json()['access']
                tokens.append(token)
                print(f"   ✅ Token obtenido para {user_data['username']}")
            else:
                print(
                    f"   ❌ Error login {user_data['username']}: {response.text}")
                return

        # 2. Crear chat grupal con participantes (usando testuser1)
        print("\n2. Creando chat grupal con participantes...")

        headers = {'Authorization': f'Bearer {tokens[0]}'}

        chat_data = {
            "name": "Mi Grupo de Chat",
            "description": "Un grupo para hablar de todo",
            "room_type": "group",
            # Agregar testuser2 y testuser3
            "participants": ["testuser2", "testuser3"]
        }

        response = requests.post(
            f'{BASE_URL}/api/v1/chat/rooms/', json=chat_data, headers=headers)

        print(f"   Status Code: {response.status_code}")

        if response.status_code == 201:
            chat_response = response.json()
            print(f"   ✅ Chat creado exitosamente!")
            print(f"   Chat ID: {chat_response['id']}")
            print(f"   Nombre: {chat_response['name']}")
            print(f"   Participantes ({len(chat_response['participants'])}):")

            for participant in chat_response['participants']:
                print(
                    f"      - {participant['username']} ({participant['first_name']} {participant['last_name']})")

            # Verificar que se agregaron todos los participantes esperados
            usernames = [p['username'] for p in chat_response['participants']]
            expected_users = ['testuser1', 'testuser2', 'testuser3']

            missing_users = set(expected_users) - set(usernames)
            if missing_users:
                print(f"   ❌ Faltan participantes: {missing_users}")
            else:
                print(f"   ✅ Todos los participantes agregados correctamente!")

        else:
            print(f"   ❌ Error creando chat: {response.status_code}")
            print(f"   Response: {response.text}")

        # 3. Verificar desde otro usuario
        print("\n3. Verificando desde testuser2...")

        headers2 = {'Authorization': f'Bearer {tokens[1]}'}
        response = requests.get(
            f'{BASE_URL}/api/v1/chat/rooms/', headers=headers2)

        if response.status_code == 200:
            rooms = response.json()
            print(f"   ✅ testuser2 puede ver {len(rooms['results'])} sala(s)")

            if rooms['results']:
                room = rooms['results'][0]
                print(f"   Sala: {room['name']}")
                print(
                    f"   Participantes: {[p['username'] for p in room['participants']]}")
        else:
            print(
                f"   ❌ Error listando salas para testuser2: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_chat_participants()
