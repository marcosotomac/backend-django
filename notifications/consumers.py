"""
WebSocket consumer para notificaciones en tiempo real
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer para manejar notificaciones en tiempo real
    """

    async def connect(self):
        """Establecer conexión WebSocket para notificaciones"""
        self.user = self.scope["user"]

        # Verificar autenticación
        if not self.user.is_authenticated:
            await self.close()
            return

        # Crear grupo único para el usuario
        self.user_group_name = f'user_{self.user.id}_notifications'

        # Unirse al grupo de notificaciones del usuario
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Aceptar conexión
        await self.accept()

        # Enviar notificaciones no leídas al conectarse
        await self.send_unread_notifications()

        logger.info(f"Usuario {self.user.username} conectado a notificaciones")

    async def disconnect(self, close_code):
        """Cerrar conexión WebSocket"""
        if hasattr(self, 'user_group_name'):
            # Salir del grupo
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

        logger.info(
            f"Usuario {self.user.username} desconectado de notificaciones")

    async def receive(self, text_data):
        """Recibir mensaje del WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'mark_read':
                await self.handle_mark_read(data)
            elif action == 'get_unread_count':
                await self.handle_get_unread_count()
            elif action == 'get_notifications':
                await self.handle_get_notifications(data)
            else:
                await self.send_error("Acción no válida")

        except json.JSONDecodeError:
            await self.send_error("Formato JSON inválido")
        except Exception as e:
            logger.error(f"Error en receive: {str(e)}")
            await self.send_error("Error interno del servidor")

    async def handle_mark_read(self, data):
        """Manejar marcado de notificaciones como leídas"""
        notification_ids = data.get('notification_ids', [])
        mark_all = data.get('mark_all', False)

        try:
            count = await self.mark_notifications_read(notification_ids, mark_all)

            await self.send(text_data=json.dumps({
                'type': 'mark_read_response',
                'data': {
                    'marked_count': count,
                    'success': True
                }
            }))

            # Enviar conteo actualizado
            await self.send_unread_count()

        except Exception as e:
            logger.error(f"Error marcando notificaciones: {str(e)}")
            await self.send_error("Error marcando notificaciones como leídas")

    async def handle_get_unread_count(self):
        """Obtener conteo de notificaciones no leídas"""
        await self.send_unread_count()

    async def handle_get_notifications(self, data):
        """Obtener lista de notificaciones"""
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        try:
            notifications_data = await self.get_notifications_page(page, page_size)

            await self.send(text_data=json.dumps({
                'type': 'notifications_list',
                'data': notifications_data
            }))

        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {str(e)}")
            await self.send_error("Error obteniendo notificaciones")

    # Handlers para eventos del grupo

    async def notification_message(self, event):
        """Enviar nueva notificación al WebSocket"""
        notification = event['notification']

        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'data': notification
        }))

        # También enviar conteo actualizado
        await self.send_unread_count()

    # Métodos de utilidad

    async def send_error(self, message):
        """Enviar mensaje de error al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    async def send_unread_notifications(self):
        """Enviar notificaciones no leídas al conectarse"""
        try:
            notifications_data = await self.get_unread_notifications()

            if notifications_data:
                await self.send(text_data=json.dumps({
                    'type': 'unread_notifications',
                    'data': notifications_data
                }))

            # También enviar conteo
            await self.send_unread_count()

        except Exception as e:
            logger.error(f"Error enviando notificaciones no leídas: {str(e)}")

    async def send_unread_count(self):
        """Enviar conteo de notificaciones no leídas"""
        try:
            count = await self.get_unread_count()

            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'data': {'count': count}
            }))

        except Exception as e:
            logger.error(f"Error enviando conteo no leído: {str(e)}")

    # Métodos de base de datos

    @database_sync_to_async
    def get_unread_notifications(self):
        """Obtener notificaciones no leídas"""
        from .models import UserNotification
        from .serializers import NotificationSerializer

        notifications = UserNotification.objects.filter(
            recipient=self.user,
            is_read=False
        ).select_related(
            'actor', 'content_type'
        ).order_by('-created_at')[:10]  # Últimas 10

        serializer = NotificationSerializer(notifications, many=True)
        return serializer.data

    @database_sync_to_async
    def get_unread_count(self):
        """Obtener conteo de notificaciones no leídas"""
        from .models import UserNotification

        return UserNotification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()

    @database_sync_to_async
    def mark_notifications_read(self, notification_ids, mark_all):
        """Marcar notificaciones como leídas"""
        from .services import notification_service

        return notification_service.mark_notifications_read(
            user=self.user,
            notification_ids=notification_ids,
            mark_all=mark_all
        )

    @database_sync_to_async
    def get_notifications_page(self, page, page_size):
        """Obtener página de notificaciones"""
        from django.core.paginator import Paginator
        from .models import UserNotification
        from .serializers import NotificationSerializer

        notifications = UserNotification.objects.filter(
            recipient=self.user
        ).select_related(
            'actor', 'content_type'
        ).order_by('-created_at')

        paginator = Paginator(notifications, page_size)
        page_obj = paginator.get_page(page)

        serializer = NotificationSerializer(page_obj.object_list, many=True)

        return {
            'notifications': serializer.data,
            'page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
