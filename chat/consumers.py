"""
WebSocket consumers para el sistema de chat en tiempo real
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatRoom, Message, OnlineStatus, MessageRead
from .serializers import MessageSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer para manejar conexiones WebSocket del chat
    """

    async def connect(self):
        """Establecer conexión WebSocket"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

        # Verificar autenticación
        if not self.user.is_authenticated:
            await self.close()
            return

        # Verificar que el usuario es participante de la sala
        is_participant = await self.check_room_participant()
        if not is_participant:
            await self.close()
            return

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Aceptar conexión
        await self.accept()

        # Marcar usuario como online
        await self.set_user_online(True)

        # Notificar que el usuario se conectó
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'action': 'user_joined',
                'user_id': str(self.user.id),
                'username': self.user.username
            }
        )

        logger.info(
            f"Usuario {self.user.username} conectado a sala {self.room_id}")

    async def disconnect(self, close_code):
        """Cerrar conexión WebSocket"""
        if hasattr(self, 'room_group_name'):
            # Marcar usuario como offline
            await self.set_user_online(False)

            # Notificar que el usuario se desconectó
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'action': 'user_left',
                    'user_id': str(self.user.id),
                    'username': self.user.username
                }
            )

            # Salir del grupo
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(
            f"Usuario {self.user.username} desconectado de sala {self.room_id}")

    async def receive(self, text_data):
        """Recibir mensaje del WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'send_message':
                await self.handle_send_message(data)
            elif action == 'typing':
                await self.handle_typing(data)
            elif action == 'mark_read':
                await self.handle_mark_read(data)
            elif action == 'edit_message':
                await self.handle_edit_message(data)
            elif action == 'delete_message':
                await self.handle_delete_message(data)
            else:
                await self.send_error("Acción no válida")

        except json.JSONDecodeError:
            await self.send_error("Formato JSON inválido")
        except Exception as e:
            logger.error(f"Error en receive: {str(e)}")
            await self.send_error("Error interno del servidor")

    async def handle_send_message(self, data):
        """Manejar envío de mensaje"""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        reply_to_id = data.get('reply_to_id')

        if not content and message_type == 'text':
            await self.send_error("El contenido del mensaje no puede estar vacío")
            return

        # Crear mensaje en la base de datos
        message = await self.create_message(content, message_type, reply_to_id)
        if not message:
            await self.send_error("Error al crear el mensaje")
            return

        # Serializar mensaje
        message_data = await self.serialize_message(message)

        # Enviar mensaje a todos los participantes de la sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def handle_typing(self, data):
        """Manejar indicador de escritura"""
        is_typing = data.get('is_typing', False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    async def handle_mark_read(self, data):
        """Manejar marcar mensajes como leídos"""
        message_ids = data.get('message_ids', [])

        if message_ids:
            await self.mark_messages_read(message_ids)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': str(self.user.id),
                    'message_ids': message_ids
                }
            )

    async def handle_edit_message(self, data):
        """Manejar edición de mensaje"""
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()

        if not new_content:
            await self.send_error("El contenido del mensaje no puede estar vacío")
            return

        message = await self.edit_message(message_id, new_content)
        if not message:
            await self.send_error("No se pudo editar el mensaje")
            return

        message_data = await self.serialize_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_edited',
                'message': message_data
            }
        )

    async def handle_delete_message(self, data):
        """Manejar eliminación de mensaje"""
        message_id = data.get('message_id')

        success = await self.delete_message(message_id)
        if not success:
            await self.send_error("No se pudo eliminar el mensaje")
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_deleted',
                'message_id': message_id,
                'user_id': str(self.user.id)
            }
        )

    # Handlers para eventos del grupo

    async def chat_message(self, event):
        """Enviar mensaje de chat al WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message']
        }))

    async def typing_indicator(self, event):
        """Enviar indicador de escritura al WebSocket"""
        # No enviar la notificación al usuario que está escribiendo
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'data': {
                    'user_id': event['user_id'],
                    'username': event['username'],
                    'is_typing': event['is_typing']
                }
            }))

    async def user_status(self, event):
        """Enviar cambio de estado de usuario al WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'data': {
                'action': event['action'],
                'user_id': event['user_id'],
                'username': event['username']
            }
        }))

    async def messages_read(self, event):
        """Enviar notificación de mensajes leídos al WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'data': {
                'user_id': event['user_id'],
                'message_ids': event['message_ids']
            }
        }))

    async def message_edited(self, event):
        """Enviar mensaje editado al WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'data': event['message']
        }))

    async def message_deleted(self, event):
        """Enviar notificación de mensaje eliminado al WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'data': {
                'message_id': event['message_id'],
                'user_id': event['user_id']
            }
        }))

    # Métodos de utilidad

    async def send_error(self, message):
        """Enviar mensaje de error al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    @database_sync_to_async
    def check_room_participant(self):
        """Verificar si el usuario es participante de la sala"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, content, message_type, reply_to_id):
        """Crear mensaje en la base de datos"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)

            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id, room=room)
                except Message.DoesNotExist:
                    pass

            message = Message.objects.create(
                room=room,
                sender=self.user,
                content=content,
                message_type=message_type,
                reply_to=reply_to
            )

            # Actualizar timestamp de la sala
            room.updated_at = message.created_at
            room.save()

            return message
        except Exception as e:
            logger.error(f"Error creando mensaje: {str(e)}")
            return None

    @database_sync_to_async
    def serialize_message(self, message):
        """Serializar mensaje"""
        serializer = MessageSerializer(message)
        return serializer.data

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Marcar mensajes como leídos"""
        try:
            messages = Message.objects.filter(
                id__in=message_ids,
                room_id=self.room_id
            ).exclude(sender=self.user)

            for message in messages:
                MessageRead.objects.get_or_create(
                    user=self.user,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error marcando mensajes como leídos: {str(e)}")

    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        """Editar mensaje"""
        try:
            message = Message.objects.get(
                id=message_id,
                room_id=self.room_id,
                sender=self.user
            )
            message.content = new_content
            message.edited_at = timezone.now()
            message.save()
            return message
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def delete_message(self, message_id):
        """Eliminar mensaje (soft delete)"""
        try:
            message = Message.objects.get(
                id=message_id,
                room_id=self.room_id,
                sender=self.user
            )
            message.is_deleted = True
            message.content = "[Mensaje eliminado]"
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def set_user_online(self, is_online):
        """Establecer estado online del usuario"""
        try:
            status, created = OnlineStatus.objects.get_or_create(
                user=self.user,
                defaults={'is_online': is_online}
            )
            if not created:
                status.is_online = is_online
                if not is_online:
                    status.last_seen = timezone.now()
                status.save()
        except Exception as e:
            logger.error(f"Error actualizando estado online: {str(e)}")
