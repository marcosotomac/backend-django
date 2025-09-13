"""
Configuración del panel de administración para notificaciones
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserNotification, NotificationSettings, DeviceToken,
    NotificationBatch, NotificationType
)


@admin.register(UserNotification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin para notificaciones"""
    list_display = [
        'title_preview', 'recipient', 'actor', 'notification_type',
        'is_read', 'created_at', 'read_status'
    ]
    list_filter = [
        'notification_type', 'is_read', 'is_sent', 'created_at',
        'content_type'
    ]
    search_fields = [
        'title', 'message', 'recipient__username', 'actor__username'
    ]
    readonly_fields = ['id', 'created_at', 'read_at']
    raw_id_fields = ['recipient', 'actor']

    fieldsets = (
        (None, {
            'fields': ('recipient', 'actor', 'notification_type')
        }),
        ('Contenido', {
            'fields': ('title', 'message', 'content_type', 'object_id')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at', 'is_sent')
        }),
        ('Metadatos', {
            'fields': ('extra_data', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def title_preview(self, obj):
        """Preview del título"""
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_preview.short_description = "Título"

    def read_status(self, obj):
        """Estado de lectura visual"""
        if obj.is_read:
            return format_html(
                '<span style="color: green;">✓ Leída</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ No leída</span>'
            )
    read_status.short_description = "Estado"

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Marcar notificaciones como leídas"""
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1

        self.message_user(
            request,
            f"{count} notificaciones marcadas como leídas."
        )
    mark_as_read.short_description = "Marcar como leídas"

    def mark_as_unread(self, request, queryset):
        """Marcar notificaciones como no leídas"""
        count = queryset.filter(is_read=True).update(
            is_read=False,
            read_at=None
        )
        self.message_user(
            request,
            f"{count} notificaciones marcadas como no leídas."
        )
    mark_as_unread.short_description = "Marcar como no leídas"


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    """Admin para configuración de notificaciones"""
    list_display = [
        'user', 'push_notifications', 'email_notifications',
        'in_app_notifications', 'quiet_hours_enabled'
    ]
    list_filter = [
        'push_notifications', 'email_notifications', 'in_app_notifications',
        'quiet_hours_enabled', 'likes_enabled', 'comments_enabled'
    ]
    search_fields = ['user__username', 'user__email']

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Tipos de Notificaciones', {
            'fields': (
                'likes_enabled', 'comments_enabled', 'follows_enabled',
                'messages_enabled', 'mentions_enabled', 'posts_enabled'
            )
        }),
        ('Canales de Entrega', {
            'fields': (
                'push_notifications', 'email_notifications',
                'in_app_notifications'
            )
        }),
        ('Horario Silencioso', {
            'fields': (
                'quiet_hours_enabled', 'quiet_hours_start',
                'quiet_hours_end'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """Admin para tokens de dispositivos"""
    list_display = [
        'user', 'platform', 'device_name', 'is_active',
        'created_at', 'last_used'
    ]
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__username', 'device_name', 'token']
    readonly_fields = ['id', 'created_at', 'last_used']

    fieldsets = (
        (None, {
            'fields': ('user', 'token', 'platform')
        }),
        ('Información del Dispositivo', {
            'fields': ('device_name', 'app_version', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used'),
            'classes': ('collapse',)
        }),
    )

    actions = ['deactivate_tokens', 'activate_tokens']

    def deactivate_tokens(self, request, queryset):
        """Desactivar tokens seleccionados"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} tokens desactivados.")
    deactivate_tokens.short_description = "Desactivar tokens"

    def activate_tokens(self, request, queryset):
        """Activar tokens seleccionados"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} tokens activados.")
    activate_tokens.short_description = "Activar tokens"


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    """Admin para lotes de notificaciones"""
    list_display = [
        'title', 'status', 'total_recipients', 'sent_count',
        'failed_count', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'notification_type', 'created_at']
    search_fields = ['title', 'message', 'created_by__username']
    readonly_fields = [
        'id', 'total_recipients', 'sent_count', 'failed_count',
        'sent_at', 'created_at'
    ]
    filter_horizontal = ['target_users']

    fieldsets = (
        (None, {
            'fields': ('title', 'message', 'notification_type')
        }),
        ('Destinatarios', {
            'fields': ('target_users', 'filter_criteria')
        }),
        ('Programación', {
            'fields': ('scheduled_at',)
        }),
        ('Estado', {
            'fields': (
                'status', 'total_recipients', 'sent_count',
                'failed_count', 'sent_at'
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['send_batches']

    def send_batches(self, request, queryset):
        """Enviar lotes seleccionados"""
        from .services import notification_service

        sent_count = 0
        for batch in queryset.filter(status='draft'):
            if notification_service.send_batch_notification(batch):
                sent_count += 1

        self.message_user(
            request,
            f"{sent_count} lotes enviados exitosamente."
        )
    send_batches.short_description = "Enviar lotes"


# Configuración personalizada del admin
admin.site.site_header = "Social Network - Administración"
admin.site.site_title = "Social Network Admin"
admin.site.index_title = "Panel de Administración"
