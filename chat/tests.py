"""
Tests para el sistema de chat
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import ChatRoom, Message, OnlineStatus

User = get_user_model()


class ChatRoomModelTest(TestCase):
    """Tests para el modelo ChatRoom"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )

    def test_create_group_chat(self):
        """Test crear chat grupal"""
        room = ChatRoom.objects.create(
            name="Test Group",
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        self.assertEqual(room.name, "Test Group")
        self.assertEqual(room.room_type, 'group')
        self.assertEqual(room.participant_count, 2)
        self.assertTrue(room.is_active)

    def test_create_direct_chat(self):
        """Test crear chat directo"""
        room = ChatRoom.objects.create(
            room_type='direct',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        self.assertEqual(room.room_type, 'direct')
        self.assertEqual(room.participant_count, 2)
        self.assertIsNone(room.name)


class MessageModelTest(TestCase):
    """Tests para el modelo Message"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )
        self.room = ChatRoom.objects.create(
            name="Test Room",
            room_type='group',
            created_by=self.user1
        )
        self.room.participants.add(self.user1, self.user2)

    def test_create_message(self):
        """Test crear mensaje"""
        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content="Hello world!",
            message_type='text'
        )

        self.assertEqual(message.content, "Hello world!")
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.room, self.room)
        self.assertFalse(message.is_deleted)

    def test_reply_to_message(self):
        """Test responder a un mensaje"""
        original_message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content="Original message",
            message_type='text'
        )

        reply = Message.objects.create(
            room=self.room,
            sender=self.user2,
            content="Reply to original",
            message_type='text',
            reply_to=original_message
        )

        self.assertEqual(reply.reply_to, original_message)


class ChatAPITest(APITestCase):
    """Tests para las APIs de chat"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )

        # Autenticación
        self.client.force_authenticate(user=self.user1)

    def test_create_group_chat(self):
        """Test crear chat grupal via API"""
        url = reverse('chatroom-list')
        data = {
            'name': 'Test Group API',
            'room_type': 'group',
            'description': 'Test description',
            'participant_ids': [str(self.user2.id)]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Group API')
        # user1 + user2
        self.assertEqual(len(response.data['participants']), 2)

    def test_create_direct_chat(self):
        """Test crear chat directo via API"""
        url = reverse('chatroom-direct-chat')
        data = {'user_id': str(self.user2.id)}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room_type'], 'direct')

    def test_send_message(self):
        """Test enviar mensaje via API"""
        # Crear sala primero
        room = ChatRoom.objects.create(
            name="Test Room",
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        # Enviar mensaje
        url = reverse('message-list')
        data = {
            'room': str(room.id),
            'content': 'Test message via API',
            'message_type': 'text'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test message via API')

    def test_get_room_messages(self):
        """Test obtener mensajes de una sala"""
        # Crear sala y mensaje
        room = ChatRoom.objects.create(
            name="Test Room",
            room_type='group',
            created_by=self.user1
        )
        room.participants.add(self.user1, self.user2)

        Message.objects.create(
            room=room,
            sender=self.user1,
            content="Test message",
            message_type='text'
        )

        # Obtener mensajes
        url = reverse('chatroom-messages', kwargs={'pk': room.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results']
                         [0]['content'], 'Test message')


class OnlineStatusTest(TestCase):
    """Tests para el sistema de estado online"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_create_online_status(self):
        """Test crear estado online"""
        # El OnlineStatus se crea automáticamente por la señal
        # Solo verificamos que existe y podemos modificarlo
        status = OnlineStatus.objects.get(user=self.user)

        # Verificar estado inicial
        self.assertFalse(status.is_online)  # Por defecto es False
        self.assertEqual(status.user, self.user)
        self.assertIsNotNone(status.last_seen)

        # Actualizar estado
        status.is_online = True
        status.save()

        # Verificar actualización
        status.refresh_from_db()
        self.assertTrue(status.is_online)
