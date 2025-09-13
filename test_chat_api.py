"""
Test comprehensivo del sistema de chat para detectar y validar correcciones
"""
import os
import django
import json
import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from chat.models import ChatRoom, Message, OnlineStatus, MessageRead
from chat.serializers import ChatRoomSerializer, MessageSerializer

# Setup Django para tests fuera del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'social_network_backend.settings')
django.setup()

User = get_user_model()


class ChatAPITestCase(APITestCase):
    """Tests comprehensivos para todas las funcionalidades del chat"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(
            username='chatuser1',
            email='chatuser1@test.com',
            password='testpass123',
            first_name='Chat',
            last_name='User1'
        )

        self.user2 = User.objects.create_user(
            username='chatuser2',
            email='chatuser2@test.com',
            password='testpass123',
            first_name='Chat',
            last_name='User2'
        )

        self.user3 = User.objects.create_user(
            username='chatuser3',
            email='chatuser3@test.com',
            password='testpass123',
            first_name='Chat',
            last_name='User3'
        )

        # Crear tokens JWT
        self.token1 = str(RefreshToken.for_user(self.user1).access_token)
        self.token2 = str(RefreshToken.for_user(self.user2).access_token)
        self.token3 = str(RefreshToken.for_user(self.user3).access_token)

        # Configurar cliente API
        self.client = APIClient()

    def authenticate_user(self, token):
        """Autenticar usuario en el cliente API"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_01_create_group_chat_room(self):
        """Test: Crear sala de chat grupal"""
        self.authenticate_user(self.token1)

        data = {
            'name': 'Chat Grupal Test',
            'room_type': 'group',
            'description': 'Sala de prueba para testing',
            'participant_ids': [str(self.user2.id), str(self.user3.id)]
        }

        response = self.client.post('/api/v1/chat/rooms/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Chat Grupal Test')
        self.assertEqual(response.data['room_type'], 'group')
        # Creador + 2 participantes
        self.assertEqual(len(response.data['participants']), 3)

        print("✅ Test 1: Crear sala de chat grupal - PASÓ")

    def test_02_create_direct_chat(self):
        """Test: Crear chat directo entre dos usuarios"""
        self.authenticate_user(self.token1)

        data = {
            'user_id': str(self.user2.id)
        }

        response = self.client.post(
            '/api/v1/chat/rooms/direct_chat/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room_type'], 'direct')
        self.assertEqual(len(response.data['participants']), 2)

        print("✅ Test 2: Crear chat directo - PASÓ")

    def test_03_prevent_duplicate_direct_chat(self):
        """Test: Prevenir creación de chats directos duplicados"""
        self.authenticate_user(self.token1)

        # Crear primer chat directo
        data = {'user_id': str(self.user2.id)}
        response1 = self.client.post(
            '/api/v1/chat/rooms/direct_chat/', data, format='json')
        room_id_1 = response1.data['id']

        # Intentar crear otro chat directo con el mismo usuario
        response2 = self.client.post(
            '/api/v1/chat/rooms/direct_chat/', data, format='json')
        room_id_2 = response2.data['id']

        # Debe devolver la misma sala
        self.assertEqual(room_id_1, room_id_2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        print("✅ Test 3: Prevenir chats directos duplicados - PASÓ")

    def test_04_list_user_chat_rooms(self):
        """Test: Listar salas de chat del usuario"""
        self.authenticate_user(self.token1)

        # Crear algunas salas de chat
        room1 = ChatRoom.objects.create(
            name='Sala 1',
            room_type='group',
            created_by=self.user1
        )
        room1.participants.add(self.user1, self.user2)

        room2 = ChatRoom.objects.create(
            room_type='direct',
            created_by=self.user2
        )
        room2.participants.add(self.user1, self.user2)

        response = self.client.get('/api/v1/chat/rooms/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 2)

        print("✅ Test 4: Listar salas de chat del usuario - PASÓ")

    def test_05_send_message_to_room(self):
        """Test: Enviar mensaje a una sala de chat"""
        # Crear sala de chat
        room = ChatRoom.objects.create(
            name='Test Room',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        self.authenticate_user(self.token1)

        data = {
            'room': str(room.id),
            'content': 'Hola, este es un mensaje de prueba',
            'message_type': 'text'
        }

        response = self.client.post(
            '/api/v1/chat/messages/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'],
                         'Hola, este es un mensaje de prueba')
        self.assertEqual(response.data['sender']['username'], 'chatuser1')

        print("✅ Test 5: Enviar mensaje a sala - PASÓ")

    def test_06_get_room_messages(self):
        """Test: Obtener mensajes de una sala"""
        # Crear sala y mensajes
        room = ChatRoom.objects.create(
            name='Test Room',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        Message.objects.create(
            room=room,
            sender=self.user1,
            content='Mensaje 1',
            message_type='text'
        )

        Message.objects.create(
            room=room,
            sender=self.user2,
            content='Mensaje 2',
            message_type='text'
        )

        self.authenticate_user(self.token1)

        response = self.client.get(f'/api/v1/chat/rooms/{room.id}/messages/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 2)

        print("✅ Test 6: Obtener mensajes de sala - PASÓ")

    def test_07_mark_messages_as_read(self):
        """Test: Marcar mensajes como leídos"""
        # Crear sala y mensaje
        room = ChatRoom.objects.create(
            name='Test Room',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        message = Message.objects.create(
            room=room,
            sender=self.user1,
            content='Mensaje para marcar como leído',
            message_type='text'
        )

        self.authenticate_user(self.token2)

        data = {
            'message_ids': [str(message.id)]
        }

        response = self.client.post(
            '/api/v1/chat/messages/mark_read/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('marked_as_read' in response.data)

        print("✅ Test 7: Marcar mensajes como leídos - PASÓ")

    def test_08_join_group_chat(self):
        """Test: Unirse a un chat grupal"""
        # Crear sala grupal
        room = ChatRoom.objects.create(
            name='Chat Público',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        self.authenticate_user(self.token3)

        response = self.client.post(f'/api/v1/chat/rooms/{room.id}/join/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que el usuario se unió
        room.refresh_from_db()
        self.assertTrue(room.participants.filter(id=self.user3.id).exists())

        print("✅ Test 8: Unirse a chat grupal - PASÓ")

    def test_09_leave_group_chat(self):
        """Test: Salir de un chat grupal"""
        # Crear sala grupal con el usuario ya como participante
        room = ChatRoom.objects.create(
            name='Chat Para Salir',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2, self.user3)

        self.authenticate_user(self.token3)

        response = self.client.post(f'/api/v1/chat/rooms/{room.id}/leave/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que el usuario salió
        room.refresh_from_db()
        self.assertFalse(room.participants.filter(id=self.user3.id).exists())

        print("✅ Test 9: Salir de chat grupal - PASÓ")

    def test_10_search_messages(self):
        """Test: Buscar mensajes por contenido"""
        # Crear sala y mensajes
        room = ChatRoom.objects.create(
            name='Chat Búsqueda',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        Message.objects.create(
            room=room,
            sender=self.user1,
            content='Este mensaje contiene Python',
            message_type='text'
        )

        Message.objects.create(
            room=room,
            sender=self.user1,
            content='Este mensaje habla de Django',
            message_type='text'
        )

        self.authenticate_user(self.token1)

        response = self.client.get('/api/v1/chat/messages/search/?q=Python')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)
        self.assertIn('Python', response.data['results'][0]['content'])

        print("✅ Test 10: Buscar mensajes - PASÓ")

    def test_11_online_status_functionality(self):
        """Test: Funcionalidad de estado online"""
        # Crear estados online
        OnlineStatus.objects.get_or_create(
            user=self.user1,
            defaults={'is_online': True}
        )

        OnlineStatus.objects.get_or_create(
            user=self.user2,
            defaults={'is_online': False}
        )

        self.authenticate_user(self.token1)

        response = self.client.get('/api/v1/chat/online-status/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print("✅ Test 11: Funcionalidad estado online - PASÓ")

    def test_12_permission_restrictions(self):
        """Test: Verificar restricciones de permisos"""
        # Crear sala sin que user3 sea participante
        room = ChatRoom.objects.create(
            name='Chat Privado',
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        self.authenticate_user(self.token3)

        # Intentar enviar mensaje sin ser participante
        data = {
            'room': str(room.id),
            'content': 'No debería poder enviar esto',
            'message_type': 'text'
        }

        response = self.client.post(
            '/api/v1/chat/messages/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print("✅ Test 12: Restricciones de permisos - PASÓ")


def run_all_tests():
    """Ejecutar todos los tests del chat"""
    import sys
    from io import StringIO
    from django.test.utils import get_runner
    from django.conf import settings

    print("🚀 Iniciando tests comprehensivos del sistema de chat...")
    print("=" * 60)

    # Configurar test runner
    test_runner = get_runner(settings)()

    # Capturar output
    old_config = test_runner.setup_test_environment()
    old_db = test_runner.setup_databases()

    try:
        # Ejecutar tests
        suite = test_runner.build_suite(['test_chat_api'])
        result = test_runner.run_suite(suite)

        if result.wasSuccessful():
            print("\n" + "=" * 60)
            print("🎉 ¡TODOS LOS TESTS DEL CHAT PASARON EXITOSAMENTE!")
            print("✅ Sistema de chat completamente funcional")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ ALGUNOS TESTS FALLARON")
            print(f"Errores: {len(result.errors)}")
            print(f"Fallos: {len(result.failures)}")
            print("=" * 60)
            return False

    finally:
        # Limpiar
        test_runner.teardown_databases(old_db)
        test_runner.teardown_test_environment(old_config)


if __name__ == '__main__':
    run_all_tests()
