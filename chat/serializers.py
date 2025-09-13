"""
Serializers para el sistema de chat
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, MessageRead, OnlineStatus
from users.serializers import UserBasicSerializer

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para mensajes de chat"""
    sender = UserBasicSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    read_by_count = serializers.SerializerMethodField()
    is_read_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'message_type', 'content',
            'image', 'file', 'created_at', 'updated_at', 'edited_at',
            'is_deleted', 'reply_to', 'read_by_count', 'is_read_by_me'
        ]
        read_only_fields = ['id', 'sender',
                            'created_at', 'updated_at', 'edited_at']

    def get_reply_to(self, obj):
        """Obtener información del mensaje al que se responde"""
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content[:100],
                'sender': obj.reply_to.sender.username,
                'message_type': obj.reply_to.message_type
            }
        return None

    def get_read_by_count(self, obj):
        """Número de usuarios que han leído el mensaje"""
        return obj.read_by.count()

    def get_is_read_by_me(self, obj):
        """Si el usuario actual ha leído el mensaje"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_by.filter(user=request.user).exists()
        return False


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para salas de chat"""
    participants = UserBasicSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    online_participants = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'participants', 'created_by',
            'created_at', 'updated_at', 'is_active', 'description',
            'participant_count', 'last_message', 'unread_count',
            'online_participants'
        ]
        read_only_fields = ['id', 'created_by',
                            'created_at', 'updated_at', 'participant_count']

    def get_last_message(self, obj):
        """Obtener el último mensaje de la sala"""
        last_message = obj.get_last_message()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

    def get_unread_count(self, obj):
        """Número de mensajes no leídos para el usuario actual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Obtener mensajes no leídos por el usuario
            unread_messages = obj.messages.exclude(
                read_by__user=request.user
            ).exclude(
                sender=request.user  # No contar mis propios mensajes
            )
            return unread_messages.count()
        return 0

    def get_online_participants(self, obj):
        """Lista de participantes que están online"""
        online_users = []
        for participant in obj.participants.all():
            try:
                if hasattr(participant, 'online_status') and participant.online_status.is_online:
                    online_users.append(participant.username)
            except:
                pass
        return online_users


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear salas de chat"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'description', 'participant_ids']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        request = self.context['request']

        # Crear la sala
        room = ChatRoom.objects.create(
            created_by=request.user,
            **validated_data
        )

        # Agregar participantes
        room.participants.add(request.user)  # Siempre incluir al creador

        if participant_ids:
            participants = User.objects.filter(id__in=participant_ids)
            room.participants.add(*participants)

        return room


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear mensajes"""

    class Meta:
        model = Message
        fields = ['room', 'content', 'message_type',
                  'image', 'file', 'reply_to']

    def create(self, validated_data):
        request = self.context['request']

        # Verificar que el usuario es participante de la sala
        room = validated_data['room']
        if not room.participants.filter(id=request.user.id).exists():
            raise serializers.ValidationError(
                "No eres participante de esta sala de chat")

        # Crear el mensaje
        message = Message.objects.create(
            sender=request.user,
            **validated_data
        )

        # Actualizar timestamp de la sala
        room.updated_at = message.created_at
        room.save()

        return message


class OnlineStatusSerializer(serializers.ModelSerializer):
    """Serializer para estado online de usuarios"""
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = OnlineStatus
        fields = ['user', 'is_online', 'last_seen']
        read_only_fields = ['user', 'last_seen']


class DirectChatSerializer(serializers.Serializer):
    """Serializer para iniciar un chat directo"""
    user_id = serializers.UUIDField()

    def validate_user_id(self, value):
        """Validar que el usuario existe"""
        try:
            user = User.objects.get(id=value)
            request_user = self.context['request'].user

            if user == request_user:
                raise serializers.ValidationError(
                    "No puedes chatear contigo mismo")

            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")

    def create(self, validated_data):
        """Crear o encontrar chat directo existente"""
        user_id = validated_data['user_id']
        request_user = self.context['request'].user
        other_user = User.objects.get(id=user_id)

        # Buscar chat directo existente
        existing_room = ChatRoom.objects.filter(
            room_type='direct',
            participants=request_user
        ).filter(
            participants=other_user
        ).first()

        if existing_room:
            return existing_room

        # Crear nueva sala de chat directo
        room = ChatRoom.objects.create(
            room_type='direct',
            created_by=request_user
        )
        room.participants.add(request_user, other_user)

        return room


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer para marcar mensajes como leídos"""
    message_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    room_id = serializers.UUIDField(required=False)

    def validate(self, data):
        """Validar que se proporcione message_ids o room_id"""
        if not data.get('message_ids') and not data.get('room_id'):
            raise serializers.ValidationError(
                "Debe proporcionar message_ids o room_id"
            )
        return data

    def create(self, validated_data):
        """Marcar mensajes como leídos"""
        request_user = self.context['request'].user
        message_ids = validated_data.get('message_ids')
        room_id = validated_data.get('room_id')

        if room_id:
            # Marcar todos los mensajes de la sala como leídos
            room = ChatRoom.objects.get(id=room_id)
            messages = room.messages.exclude(sender=request_user)
        else:
            # Marcar mensajes específicos como leídos
            messages = Message.objects.filter(id__in=message_ids)

        # Crear registros de lectura
        read_records = []
        for message in messages:
            read_record, created = MessageRead.objects.get_or_create(
                user=request_user,
                message=message
            )
            if created:
                read_records.append(read_record)

        return {'marked_as_read': len(read_records)}
