"""
Modelos para el sistema de chat en tiempo real
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatRoom(models.Model):
    """
    Sala de chat entre dos o más usuarios
    """
    ROOM_TYPES = [
        ('direct', 'Mensaje Directo'),
        ('group', 'Grupo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True,
                            null=True)  # Solo para grupos
    room_type = models.CharField(
        max_length=10, choices=ROOM_TYPES, default='direct')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Configuraciones del chat
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)  # Para grupos

    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'
        ordering = ['-updated_at']

    def __str__(self):
        if self.room_type == 'direct':
            participants = self.participants.all()[:2]
            if len(participants) == 2:
                return f"Chat: {participants[0].username} ↔ {participants[1].username}"
            return f"Chat: {self.id}"
        return self.name or f"Grupo: {self.id}"

    @property
    def participant_count(self):
        return self.participants.count()

    def get_last_message(self):
        """Obtener el último mensaje de la sala"""
        return self.messages.first()

    def add_participant(self, user):
        """Agregar participante a la sala"""
        self.participants.add(user)
        self.updated_at = timezone.now()
        self.save()

    def remove_participant(self, user):
        """Remover participante de la sala"""
        self.participants.remove(user)
        self.updated_at = timezone.now()
        self.save()


class Message(models.Model):
    """
    Mensaje individual en una sala de chat
    """
    MESSAGE_TYPES = [
        ('text', 'Texto'),
        ('image', 'Imagen'),
        ('file', 'Archivo'),
        ('system', 'Sistema'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages')

    # Contenido del mensaje
    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    file = models.FileField(upload_to='chat/files/', blank=True, null=True)

    # Metadatos
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    # Estado del mensaje
    is_deleted = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        content_preview = self.content[:50] + \
            "..." if len(self.content) > 50 else self.content
        return f"{self.sender.username}: {content_preview}"

    def mark_as_edited(self):
        """Marcar mensaje como editado"""
        self.edited_at = timezone.now()
        self.save()

    def soft_delete(self):
        """Eliminación suave del mensaje"""
        self.is_deleted = True
        self.content = "Mensaje eliminado"
        self.save()


class MessageRead(models.Model):
    """
    Rastreo de mensajes leídos por usuario
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='read_messages')
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='read_by')
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'chat_message_reads'
        unique_together = ['user', 'message']
        verbose_name = 'Mensaje Leído'
        verbose_name_plural = 'Mensajes Leídos'

    def __str__(self):
        return f"{self.user.username} leyó mensaje {self.message.id}"


class OnlineStatus(models.Model):
    """
    Estado de conexión de usuarios
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='online_status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'chat_online_status'
        verbose_name = 'Estado Online'
        verbose_name_plural = 'Estados Online'

    def __str__(self):
        status = "online" if self.is_online else f"visto por última vez {self.last_seen}"
        return f"{self.user.username}: {status}"

    def set_online(self):
        """Marcar usuario como online"""
        self.is_online = True
        self.last_seen = timezone.now()
        self.save()

    def set_offline(self):
        """Marcar usuario como offline"""
        self.is_online = False
        self.last_seen = timezone.now()
        self.save()
