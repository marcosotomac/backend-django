"""
Configuración del admin para Stories
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Story, StoryView, StoryLike, StoryReply,
    StoryHighlight, StoryHighlightItem
)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    """Admin para Stories"""
    list_display = [
        'author', 'story_type', 'content_preview', 'is_public',
        'views_count', 'likes_count', 'is_expired_status',
        'created_at', 'expires_at'
    ]
    list_filter = [
        'story_type', 'is_public', 'allow_replies', 'created_at'
    ]
    search_fields = ['author__username', 'content']
    readonly_fields = ['id', 'created_at',
                       'views_count', 'likes_count', 'replies_count']
    raw_id_fields = ['author']

    fieldsets = (
        (None, {
            'fields': ('author', 'story_type', 'content')
        }),
        ('Media', {
            'fields': ('media_file', 'thumbnail'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('is_public', 'allow_replies', 'background_color', 'text_color', 'duration')
        }),
        ('Metadatos', {
            'fields': ('music_track', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('views_count', 'likes_count', 'replies_count'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        """Preview del contenido"""
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        elif obj.media_file:
            return format_html('<span style="color: green;">📁 Archivo multimedia</span>')
        return "-"
    content_preview.short_description = "Contenido"

    def is_expired_status(self, obj):
        """Estado de expiración"""
        if obj.is_expired:
            return format_html('<span style="color: red;">❌ Expirada</span>')
        else:
            return format_html('<span style="color: green;">✅ Activa</span>')
    is_expired_status.short_description = "Estado"


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    """Admin para visualizaciones de stories"""
    list_display = ['story_preview', 'viewer', 'view_duration', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['story__author__username', 'viewer__username']
    readonly_fields = ['id', 'viewed_at']
    raw_id_fields = ['story', 'viewer']

    def story_preview(self, obj):
        return f"Story de {obj.story.author.username}"
    story_preview.short_description = "Story"


@admin.register(StoryLike)
class StoryLikeAdmin(admin.ModelAdmin):
    """Admin para likes de stories"""
    list_display = ['story_preview', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['story__author__username', 'user__username']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['story', 'user']

    def story_preview(self, obj):
        return f"Story de {obj.story.author.username}"
    story_preview.short_description = "Story"


@admin.register(StoryReply)
class StoryReplyAdmin(admin.ModelAdmin):
    """Admin para respuestas a stories"""
    list_display = ['story_preview', 'sender',
                    'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['story__author__username', 'sender__username', 'content']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['story', 'sender']

    def story_preview(self, obj):
        return f"Story de {obj.story.author.username}"
    story_preview.short_description = "Story"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Contenido"


class StoryHighlightItemInline(admin.TabularInline):
    """Inline para items de highlights"""
    model = StoryHighlightItem
    extra = 0
    raw_id_fields = ['story']
    fields = ['story', 'order']
    ordering = ['order']


@admin.register(StoryHighlight)
class StoryHighlightAdmin(admin.ModelAdmin):
    """Admin para highlights"""
    list_display = ['user', 'title',
                    'stories_count_display', 'is_public', 'updated_at']
    list_filter = ['is_public', 'created_at', 'updated_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']
    inlines = [StoryHighlightItemInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'cover_image')
        }),
        ('Configuración', {
            'fields': ('is_public',)
        }),
        ('Sistema', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def stories_count_display(self, obj):
        count = obj.stories_count
        return format_html(f'<span style="font-weight: bold;">{count} stories</span>')
    stories_count_display.short_description = "Stories"


@admin.register(StoryHighlightItem)
class StoryHighlightItemAdmin(admin.ModelAdmin):
    """Admin para items de highlights"""
    list_display = ['highlight', 'story_preview', 'order', 'added_at']
    list_filter = ['added_at']
    search_fields = ['highlight__title', 'story__author__username']
    readonly_fields = ['id', 'added_at']
    raw_id_fields = ['highlight', 'story']
    ordering = ['highlight', 'order']

    def story_preview(self, obj):
        return f"Story de {obj.story.author.username} ({obj.story.story_type})"
    story_preview.short_description = "Story"
