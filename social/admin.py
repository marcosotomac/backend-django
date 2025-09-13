from django.contrib import admin
from django.utils.html import format_html
from .models import Follow, Like, Comment, Notification


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Follow
    """
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = [
        'follower__username', 'follower__first_name', 'follower__last_name',
        'following__username', 'following__first_name', 'following__last_name'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        # Los follows se crean desde la API
        return False


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Like
    """
    list_display = ['user', 'like_type', 'get_target', 'created_at']
    list_filter = ['like_type', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

    def get_target(self, obj):
        if obj.like_type == 'post' and obj.post:
            return f"Post: {obj.post.content[:50]}..."
        elif obj.like_type == 'comment' and obj.comment:
            return f"Comentario: {obj.comment.content[:50]}..."
        return "Sin objetivo"
    get_target.short_description = 'Objetivo del like'

    def has_add_permission(self, request):
        # Los likes se crean desde la API
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Comment
    """
    list_display = [
        'content_preview', 'author', 'post_preview',
        'is_reply', 'likes_count', 'replies_count', 'created_at'
    ]
    list_filter = ['created_at', 'author__is_verified']
    search_fields = [
        'content', 'author__username', 'author__first_name',
        'author__last_name', 'post__content'
    ]
    readonly_fields = [
        'id', 'likes_count', 'replies_count',
        'created_at', 'updated_at'
    ]
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('post', 'author', 'content', 'parent')
        }),
        ('Estadísticas', {
            'fields': ('likes_count', 'replies_count'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Contenido'

    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = 'Post'

    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.short_description = 'Es respuesta'
    is_reply.boolean = True


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Notification
    """
    list_display = [
        'recipient', 'sender', 'notification_type',
        'message_preview', 'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = [
        'recipient__username', 'sender__username',
        'message', 'recipient__first_name', 'sender__first_name'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': (
                'recipient', 'sender', 'notification_type',
                'message', 'is_read'
            )
        }),
        ('Relacionados', {
            'fields': ('post', 'comment'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def message_preview(self, obj):
        return obj.message[:80] + "..." if len(obj.message) > 80 else obj.message
    message_preview.short_description = 'Mensaje'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f'{updated} notificaciones marcadas como leídas.'
        )
    mark_as_read.short_description = "Marcar como leídas"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            f'{updated} notificaciones marcadas como no leídas.'
        )
    mark_as_unread.short_description = "Marcar como no leídas"
