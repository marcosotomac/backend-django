"""
Modelos para el sistema de notificaciones
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

User = get_user_model()


class NotificationType(models.TextChoices):
    """Tipos de notificaciones disponibles"""
    LIKE = 'like', 'Like en post'
    COMMENT = 'comment', 'Comentario en post'
    FOLLOW = 'follow', 'Nuevo seguidor'
    MESSAGE = 'message', 'Nuevo mensaje'
    MENTION = 'mention', 'Mención en post/comentario'
    POST_UPLOAD = 'post_upload', 'Usuario seguido subió post'
    CHAT_INVITE = 'chat_invite', 'Invitación a chat grupal'
    SYSTEM = 'system', 'Notificación del sistema'


class UserNotification(models.Model):
    """
    Modelo principal para notificaciones
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Usuario que recibe la notificación
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_notifications'
    )

    # Usuario que generó la notificación (puede ser None para notificaciones del sistema)
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_user_notifications',
        null=True,
        blank=True
    )

    # Tipo de notificación
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )

    # Título y mensaje de la notificación
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Objeto relacionado (post, comentario, etc.) usando GenericForeignKey
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Estado de la notificación
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)  # Para push notifications

    # Metadatos adicionales (JSON)
    extra_data = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type} para {self.recipient.username}"

    def mark_as_read(self):
        """Marcar notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def get_absolute_url(self):
        """Obtener URL del objeto relacionado"""
        if self.content_object:
            if hasattr(self.content_object, 'get_absolute_url'):
                return self.content_object.get_absolute_url()
        return None


class NotificationSettings(models.Model):
    """
    Configuración de notificaciones por usuario
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )

    # Configuraciones por tipo de notificación
    likes_enabled = models.BooleanField(default=True)
    comments_enabled = models.BooleanField(default=True)
    follows_enabled = models.BooleanField(default=True)
    messages_enabled = models.BooleanField(default=True)
    mentions_enabled = models.BooleanField(default=True)
    posts_enabled = models.BooleanField(
        default=True)  # Posts de usuarios seguidos

    # Configuraciones de entrega
    push_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)
    in_app_notifications = models.BooleanField(default=True)

    # Configuraciones de horario
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)  # Ej: 22:00
    quiet_hours_end = models.TimeField(null=True, blank=True)    # Ej: 08:00

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración de {self.user.username}"

    def is_notification_enabled(self, notification_type):
        """Verificar si un tipo de notificación está habilitado"""
        mapping = {
            NotificationType.LIKE: self.likes_enabled,
            NotificationType.COMMENT: self.comments_enabled,
            NotificationType.FOLLOW: self.follows_enabled,
            NotificationType.MESSAGE: self.messages_enabled,
            NotificationType.MENTION: self.mentions_enabled,
            NotificationType.POST_UPLOAD: self.posts_enabled,
        }
        return mapping.get(notification_type, True)

    def is_quiet_time(self):
        """Verificar si estamos en horario silencioso"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        current_time = timezone.now().time()
        start = self.quiet_hours_start
        end = self.quiet_hours_end

        if start <= end:
            # Mismo día: 22:00 - 23:59
            return start <= current_time <= end
        else:
            # Cruza medianoche: 22:00 - 08:00
            return current_time >= start or current_time <= end


class DeviceToken(models.Model):
    """
    Tokens de dispositivos para push notifications
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='device_tokens'
    )

    # Token del dispositivo
    token = models.CharField(max_length=255, unique=True)

    # Plataforma del dispositivo
    platform = models.CharField(
        max_length=20,
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('web', 'Web'),
        ]
    )

    # Información adicional del dispositivo
    device_name = models.CharField(max_length=100, blank=True)
    app_version = models.CharField(max_length=20, blank=True)

    # Estado del token
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'token']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['platform', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.device_name})"


class NotificationBatch(models.Model):
    """
    Lotes de notificaciones para envío masivo
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información del lote
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )

    # Criterios de filtrado
    target_users = models.ManyToManyField(User, blank=True)
    filter_criteria = models.JSONField(
        default=dict, blank=True)  # Ej: {"verified": True}

    # Estado del envío
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('scheduled', 'Programado'),
            ('sending', 'Enviando'),
            ('sent', 'Enviado'),
            ('failed', 'Falló'),
        ],
        default='draft'
    )

    # Programación
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Estadísticas
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)

    # Metadatos
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_batches'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lote: {self.title} ({self.status})"
