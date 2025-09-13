"""
Configuración del panel de administración para el sistema de chat
"""
from django.contrib import admin
from .models import ChatRoom, Message, MessageRead, OnlineStatus


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """Admin para salas de chat"""
    list_display = ['name', 'room_type', 'created_by',
                    'participant_count', 'is_active', 'created_at']
    list_filter = ['room_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at', 'participant_count']

    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'description', 'is_active')
        }),
        ('Participantes', {
            'fields': ('created_by', 'participants', 'participant_count')
        }),
        ('Información de fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin para mensajes"""
    list_display = ['content_preview', 'sender', 'room',
                    'message_type', 'created_at', 'is_deleted']
    list_filter = ['message_type', 'is_deleted',
                   'created_at', 'room__room_type']
    search_fields = ['content', 'sender__username', 'room__name']
    readonly_fields = ['created_at', 'updated_at', 'edited_at']
    raw_id_fields = ['sender', 'room', 'reply_to']

    fieldsets = (
        (None, {
            'fields': ('room', 'sender', 'message_type', 'content')
        }),
        ('Archivos', {
            'fields': ('image', 'file'),
            'classes': ('collapse',)
        }),
        ('Respuesta', {
            'fields': ('reply_to',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_deleted',)
        }),
        ('Información de fechas', {
            'fields': ('created_at', 'updated_at', 'edited_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        """Mostrar preview del contenido"""
        if obj.is_deleted:
            return "[Mensaje eliminado]"
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Contenido"


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    """Admin para registros de lectura de mensajes"""
    list_display = ['user', 'message_preview', 'message_room', 'read_at']
    list_filter = ['read_at', 'message__room']
    search_fields = ['user__username', 'message__content']
    raw_id_fields = ['user', 'message']

    def message_preview(self, obj):
        """Preview del mensaje"""
        content = obj.message.content
        return content[:30] + "..." if len(content) > 30 else content
    message_preview.short_description = "Mensaje"

    def message_room(self, obj):
        """Sala del mensaje"""
        return obj.message.room.name or f"Chat #{obj.message.room.id}"
    message_room.short_description = "Sala"


@admin.register(OnlineStatus)
class OnlineStatusAdmin(admin.ModelAdmin):
    """Admin para estados online"""
    list_display = ['user', 'is_online', 'last_seen']
    list_filter = ['is_online', 'last_seen']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_seen']
