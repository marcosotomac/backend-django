"""
Servicio para manejar notificaciones
"""
import logging
from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import (
    UserNotification, NotificationSettings, DeviceToken,
    NotificationBatch, NotificationType
)

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Servicio principal para manejar notificaciones"""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def create_notification(
        self,
        recipient,
        notification_type,
        title,
        message,
        actor=None,
        content_object=None,
        extra_data=None
    ):
        """
        Crear una nueva notificación
        """
        try:
            # Verificar configuración del usuario
            settings = self.get_user_settings(recipient)
            if not settings.is_notification_enabled(notification_type):
                logger.info(
                    f"Notificación {notification_type} deshabilitada para {recipient.username}")
                return None

            # Verificar horario silencioso
            if settings.is_quiet_time():
                logger.info(
                    f"Horario silencioso activo para {recipient.username}")
                return None

            # Evitar duplicados recientes (últimos 5 minutos)
            recent_threshold = timezone.now() - timezone.timedelta(minutes=5)
            similar_notification = UserNotification.objects.filter(
                recipient=recipient,
                actor=actor,
                notification_type=notification_type,
                created_at__gte=recent_threshold
            ).first()

            if similar_notification and content_object:
                # Si es el mismo objeto, no crear duplicado
                similar_content_type = ContentType.objects.get_for_model(
                    content_object)
                if (similar_notification.content_type == similar_content_type and
                        str(similar_notification.object_id) == str(content_object.id)):
                    logger.info(
                        f"Notificación duplicada evitada para {recipient.username}")
                    return similar_notification

            # Crear la notificación
            notification_data = {
                'recipient': recipient,
                'actor': actor,
                'notification_type': notification_type,
                'title': title,
                'message': message,
                'extra_data': extra_data or {}
            }

            if content_object:
                notification_data['content_type'] = ContentType.objects.get_for_model(
                    content_object)
                notification_data['object_id'] = content_object.id

            notification = UserNotification.objects.create(**notification_data)

            # Enviar en tiempo real si está habilitado
            if settings.in_app_notifications:
                self.send_realtime_notification(notification)

            # Programar push notification si está habilitado
            if settings.push_notifications:
                self.schedule_push_notification(notification)

            logger.info(
                f"Notificación creada: {notification.id} para {recipient.username}")
            return notification

        except Exception as e:
            logger.error(f"Error creando notificación: {str(e)}")
            return None

    def send_realtime_notification(self, notification):
        """Enviar notificación en tiempo real via WebSocket"""
        try:
            if not self.channel_layer:
                logger.warning(
                    "Channel layer no disponible para notificación en tiempo real")
                return

            # Crear grupo de usuario para notificaciones
            user_group = f"user_{notification.recipient.id}_notifications"

            # Serializar notificación
            from .serializers import NotificationSerializer
            notification_data = NotificationSerializer(notification).data

            # Enviar via WebSocket
            async_to_sync(self.channel_layer.group_send)(
                user_group,
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )

            logger.info(
                f"Notificación en tiempo real enviada a {notification.recipient.username}")

        except Exception as e:
            logger.error(
                f"Error enviando notificación en tiempo real: {str(e)}")

    def schedule_push_notification(self, notification):
        """Programar push notification"""
        try:
            # Obtener tokens de dispositivos activos
            device_tokens = DeviceToken.objects.filter(
                user=notification.recipient,
                is_active=True
            )

            if not device_tokens.exists():
                logger.info(
                    f"No hay tokens de dispositivo para {notification.recipient.username}")
                return

            # Aquí integrarías con servicios como FCM, APNs, etc.
            # Por ahora, solo registramos la intención
            for device_token in device_tokens:
                logger.info(
                    f"Push notification programada para {device_token.platform}: {device_token.token[:10]}...")
                # TODO: Implementar envío real de push notifications

        except Exception as e:
            logger.error(f"Error programando push notification: {str(e)}")

    def get_user_settings(self, user):
        """Obtener configuración de notificaciones del usuario"""
        settings, created = NotificationSettings.objects.get_or_create(
            user=user,
            defaults={
                'likes_enabled': True,
                'comments_enabled': True,
                'follows_enabled': True,
                'messages_enabled': True,
                'mentions_enabled': True,
                'posts_enabled': True,
                'push_notifications': True,
                'email_notifications': False,
                'in_app_notifications': True,
            }
        )
        return settings

    def mark_notifications_read(
        self,
        user,
        notification_ids=None,
        mark_all=False
    ):
        """Marcar notificaciones como leídas"""
        try:
            queryset = UserNotification.objects.filter(
                recipient=user, is_read=False)

            if mark_all:
                count = queryset.count()
                queryset.update(
                    is_read=True,
                    read_at=timezone.now()
                )
            elif notification_ids:
                queryset = queryset.filter(id__in=notification_ids)
                count = queryset.count()
                queryset.update(
                    is_read=True,
                    read_at=timezone.now()
                )
            else:
                return 0

            logger.info(
                f"Marcadas {count} notificaciones como leídas para {user.username}")
            return count

        except Exception as e:
            logger.error(
                f"Error marcando notificaciones como leídas: {str(e)}")
            return 0

    def get_user_stats(self, user):
        """Obtener estadísticas de notificaciones del usuario"""
        try:
            notifications = UserNotification.objects.filter(recipient=user)

            stats = {
                'total_notifications': notifications.count(),
                'unread_notifications': notifications.filter(is_read=False).count(),
                'recent_notifications': notifications.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=7)
                ).count(),
            }

            # Estadísticas por tipo
            by_type = notifications.values('notification_type').annotate(
                count=Count('id')
            )

            stats['notifications_by_type'] = {
                item['notification_type']: item['count']
                for item in by_type
            }

            # Contadores específicos
            stats.update({
                'likes_count': notifications.filter(notification_type=NotificationType.LIKE).count(),
                'comments_count': notifications.filter(notification_type=NotificationType.COMMENT).count(),
                'follows_count': notifications.filter(notification_type=NotificationType.FOLLOW).count(),
                'messages_count': notifications.filter(notification_type=NotificationType.MESSAGE).count(),
                'mentions_count': notifications.filter(notification_type=NotificationType.MENTION).count(),
            })

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}

    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Limpiar notificaciones antiguas"""
        try:
            threshold = timezone.now() - timezone.timedelta(days=days)
            old_notifications = UserNotification.objects.filter(
                created_at__lt=threshold,
                is_read=True
            )

            count = old_notifications.count()
            old_notifications.delete()

            logger.info(f"Eliminadas {count} notificaciones antiguas")
            return count

        except Exception as e:
            logger.error(f"Error limpiando notificaciones: {str(e)}")
            return 0

    def send_batch_notification(self, batch: NotificationBatch) -> bool:
        """Enviar lote de notificaciones"""
        try:
            if batch.status != 'draft':
                logger.warning(f"Lote {batch.id} no está en estado draft")
                return False

            # Actualizar estado
            batch.status = 'sending'
            batch.save()

            # Obtener usuarios objetivo
            target_users = batch.target_users.all()
            if not target_users.exists():
                # Aplicar filtros si no hay usuarios específicos
                target_users = User.objects.filter(**batch.filter_criteria)

            batch.total_recipients = target_users.count()
            batch.save()

            sent_count = 0
            failed_count = 0

            # Crear notificaciones individuales
            for user in target_users:
                notification = self.create_notification(
                    recipient=user,
                    notification_type=batch.notification_type,
                    title=batch.title,
                    message=batch.message,
                    extra_data={'batch_id': str(batch.id)}
                )

                if notification:
                    sent_count += 1
                else:
                    failed_count += 1

            # Actualizar estadísticas
            batch.sent_count = sent_count
            batch.failed_count = failed_count
            batch.status = 'sent'
            batch.sent_at = timezone.now()
            batch.save()

            logger.info(
                f"Lote {batch.id} enviado: {sent_count} éxitos, {failed_count} fallos")
            return True

        except Exception as e:
            logger.error(f"Error enviando lote de notificaciones: {str(e)}")
            batch.status = 'failed'
            batch.save()
            return False


# Instancia global del servicio
notification_service = NotificationService()
