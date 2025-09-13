"""
Serializers para el sistema de notificaciones
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import (
    UserNotification, NotificationSettings, DeviceToken,
    NotificationBatch, NotificationType
)
from users.serializers import UserListSerializer

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    actor = UserListSerializer(read_only=True)
    content_object_data = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = [
            'id', 'notification_type', 'title', 'message', 'actor',
            'is_read', 'created_at', 'read_at', 'extra_data',
            'content_object_data', 'time_since'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

    def get_content_object_data(self, obj):
        """Obtener datos del objeto relacionado"""
        if not obj.content_object:
            return None

        content_obj = obj.content_object

        # Para posts
        if hasattr(content_obj, 'content') and hasattr(content_obj, 'author'):
            return {
                'type': 'post',
                'id': str(content_obj.id),
                'content': content_obj.content[:100] + '...' if len(content_obj.content) > 100 else content_obj.content,
                'author': content_obj.author.username,
                'created_at': content_obj.created_at
            }

        # Para comentarios
        elif hasattr(content_obj, 'content') and hasattr(content_obj, 'post'):
            return {
                'type': 'comment',
                'id': str(content_obj.id),
                'content': content_obj.content[:100] + '...' if len(content_obj.content) > 100 else content_obj.content,
                'post_id': str(content_obj.post.id),
                'created_at': content_obj.created_at
            }

        # Para salas de chat
        elif hasattr(content_obj, 'name') and hasattr(content_obj, 'room_type'):
            return {
                'type': 'chat_room',
                'id': str(content_obj.id),
                'name': content_obj.name or f"Chat {content_obj.room_type}",
                'room_type': content_obj.room_type,
                'participant_count': content_obj.participant_count
            }

        # Para usuarios (follows)
        elif hasattr(content_obj, 'username'):
            return {
                'type': 'user',
                'id': str(content_obj.id),
                'username': content_obj.username,
                'full_name': content_obj.get_full_name(),
                'avatar_url': content_obj.get_avatar_url()
            }

        return {'type': 'unknown', 'id': str(content_obj.id) if hasattr(content_obj, 'id') else None}

    def get_time_since(self, obj):
        """Tiempo transcurrido desde la creación"""
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones"""

    class Meta:
        model = UserNotification
        fields = [
            'recipient', 'actor', 'notification_type', 'title',
            'message', 'content_type', 'object_id', 'extra_data'
        ]

    def validate(self, data):
        """Validaciones personalizadas"""
        notification_type = data.get('notification_type')
        recipient = data.get('recipient')
        actor = data.get('actor')

        # No permitir auto-notificaciones (excepto sistema)
        if actor and recipient and actor == recipient and notification_type != NotificationType.SYSTEM:
            raise serializers.ValidationError(
                "No puedes enviarte notificaciones a ti mismo")

        return data


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer para configuración de notificaciones"""

    class Meta:
        model = NotificationSettings
        fields = [
            'likes_enabled', 'comments_enabled', 'follows_enabled',
            'messages_enabled', 'mentions_enabled', 'posts_enabled',
            'push_notifications', 'email_notifications', 'in_app_notifications',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]

    def validate(self, data):
        """Validar horarios silenciosos"""
        quiet_enabled = data.get('quiet_hours_enabled')
        quiet_start = data.get('quiet_hours_start')
        quiet_end = data.get('quiet_hours_end')

        if quiet_enabled and (not quiet_start or not quiet_end):
            raise serializers.ValidationError(
                "Debes especificar hora de inicio y fin para el modo silencioso"
            )

        return data


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer para tokens de dispositivos"""

    class Meta:
        model = DeviceToken
        fields = [
            'id', 'token', 'platform', 'device_name',
            'app_version', 'is_active', 'created_at', 'last_used'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']

    def create(self, validated_data):
        """Crear o actualizar token de dispositivo"""
        user = self.context['request'].user
        token = validated_data['token']

        # Buscar token existente
        device_token, created = DeviceToken.objects.get_or_create(
            user=user,
            token=token,
            defaults=validated_data
        )

        if not created:
            # Actualizar token existente
            for attr, value in validated_data.items():
                setattr(device_token, attr, value)
            device_token.save()

        return device_token


class NotificationBatchSerializer(serializers.ModelSerializer):
    """Serializer para lotes de notificaciones"""
    created_by = UserListSerializer(read_only=True)
    target_users_count = serializers.SerializerMethodField()

    class Meta:
        model = NotificationBatch
        fields = [
            'id', 'title', 'message', 'notification_type',
            'status', 'scheduled_at', 'sent_at', 'created_by',
            'total_recipients', 'sent_count', 'failed_count',
            'target_users_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'sent_at', 'total_recipients',
            'sent_count', 'failed_count', 'created_at'
        ]

    def get_target_users_count(self, obj):
        """Número de usuarios objetivo"""
        return obj.target_users.count()

    def create(self, validated_data):
        """Crear lote de notificaciones"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de notificaciones"""
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = serializers.IntegerField()

    # Estadísticas por tipo
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    follows_count = serializers.IntegerField()
    messages_count = serializers.IntegerField()
    mentions_count = serializers.IntegerField()


class MarkNotificationsReadSerializer(serializers.Serializer):
    """Serializer para marcar notificaciones como leídas"""
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)

    def validate(self, data):
        """Validar que se proporcione al menos una opción"""
        if not data.get('notification_ids') and not data.get('mark_all'):
            raise serializers.ValidationError(
                "Debe proporcionar notification_ids o mark_all=True"
            )
        return data


class NotificationPreferencesSerializer(serializers.Serializer):
    """Serializer para obtener tipos de notificaciones disponibles"""
    notification_types = serializers.ListField(
        child=serializers.DictField()
    )

    def to_representation(self, instance):
        """Representar tipos de notificaciones disponibles"""
        types = []
        for choice in NotificationType.choices:
            types.append({
                'value': choice[0],
                'label': choice[1],
                'description': self.get_type_description(choice[0])
            })

        return {'notification_types': types}

    def get_type_description(self, notification_type):
        """Descripción detallada de cada tipo"""
        descriptions = {
            NotificationType.LIKE: "Cuando alguien da like a tus posts",
            NotificationType.COMMENT: "Cuando alguien comenta en tus posts",
            NotificationType.FOLLOW: "Cuando alguien te sigue",
            NotificationType.MESSAGE: "Cuando recibes mensajes de chat",
            NotificationType.MENTION: "Cuando alguien te menciona",
            NotificationType.POST_UPLOAD: "Cuando usuarios que sigues suben contenido",
            NotificationType.CHAT_INVITE: "Cuando te invitan a un chat grupal",
            NotificationType.SYSTEM: "Notificaciones importantes del sistema"
        }
        return descriptions.get(notification_type, "Notificación del sistema")
