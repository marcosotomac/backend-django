from django.contrib import admin
from django.utils.html import format_html
from .models import Post, PostImage, Hashtag, PostHashtag


class PostImageInline(admin.TabularInline):
    """
    Inline para imágenes de posts
    """
    model = PostImage
    extra = 0
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista previa'


class PostHashtagInline(admin.TabularInline):
    """
    Inline para hashtags de posts
    """
    model = PostHashtag
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin para posts
    """
    list_display = [
        'content_preview', 'author', 'likes_count', 'comments_count',
        'is_public', 'allow_comments', 'created_at'
    ]
    list_filter = [
        'is_public', 'allow_comments', 'created_at', 'author__is_verified'
    ]
    search_fields = ['content', 'author__username',
                     'author__first_name', 'author__last_name']
    readonly_fields = [
        'id', 'likes_count', 'comments_count', 'shares_count',
        'created_at', 'updated_at', 'image_preview'
    ]
    ordering = ['-created_at']
    inlines = [PostImageInline, PostHashtagInline]

    fieldsets = (
        (None, {
            'fields': ('author', 'content')
        }),
        ('Imagen', {
            'fields': ('image', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('is_public', 'allow_comments')
        }),
        ('Estadísticas', {
            'fields': ('likes_count', 'comments_count', 'shares_count'),
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

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" style="max-height: 200px; object-fit: cover;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista previa de imagen'


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """
    Admin para imágenes de posts
    """
    list_display = ['post', 'order', 'alt_text', 'created_at', 'image_preview']
    list_filter = ['created_at']
    search_fields = ['post__content', 'alt_text']
    readonly_fields = ['id', 'created_at', 'image_preview']
    ordering = ['post', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista previa'


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    """
    Admin para hashtags
    """
    list_display = ['name', 'posts_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'posts_count']
    ordering = ['-posts_count', 'name']

    def has_add_permission(self, request):
        # Los hashtags se crean automáticamente
        return False


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    """
    Admin para relaciones Post-Hashtag
    """
    list_display = ['post', 'hashtag', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__content', 'hashtag__name']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        # Las relaciones se crean automáticamente
        return False
