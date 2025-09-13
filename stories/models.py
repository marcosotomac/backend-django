"""
Modelos para el sistema de Stories temporales
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid
from utils import story_media_path

User = get_user_model()


class StoryManager(models.Manager):
    """Manager personalizado para Stories"""

    def active(self):
        """Obtener stories activas (no expiradas)"""
        return self.filter(expires_at__gt=timezone.now())

    def expired(self):
        """Obtener stories expiradas"""
        return self.filter(expires_at__lte=timezone.now())

    def for_user(self, user):
        """Obtener stories visibles para un usuario"""
        # Por ahora, todas las stories públicas activas + las propias
        return self.active().filter(
            models.Q(is_public=True) | models.Q(author=user)
        )


class Story(models.Model):
    """
    Modelo para Stories temporales
    """
    STORY_TYPES = [
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('text', 'Texto'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='stories')
    story_type = models.CharField(
        max_length=10, choices=STORY_TYPES, default='image')

    # Contenido
    content = models.TextField(blank=True, null=True)  # Para stories de texto
    media_file = models.FileField(
        upload_to=story_media_path, blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to=story_media_path, blank=True, null=True)  # Para videos

    # Configuración
    is_public = models.BooleanField(default=True)
    allow_replies = models.BooleanField(default=True)
    background_color = models.CharField(
        max_length=7, default='#000000')  # Para stories de texto
    text_color = models.CharField(max_length=7, default='#FFFFFF')

    # Metadatos
    duration_hours = models.PositiveIntegerField(
        default=24)  # Duración en horas para expiración
    music_track = models.CharField(max_length=200, blank=True, null=True)

    # Estadísticas
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    objects = StoryManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]

    def __str__(self):
        return f"Story de {self.author.username} - {self.story_type}"

    def save(self, *args, **kwargs):
        """Configurar fecha de expiración automática si no se especifica"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=self.duration_hours)

        # Validaciones
        if self.story_type == 'text' and not self.content:
            raise ValueError("Las stories de texto requieren contenido")
        elif self.story_type in ['image', 'video'] and not self.media_file:
            raise ValueError(
                "Las stories de imagen/video requieren archivo multimedia")

        super().save(*args, **kwargs)

    def can_be_viewed_by(self, user):
        """Verificar si un usuario puede ver esta story"""

        if not user or not user.is_authenticated:
            return False

        # El autor siempre puede ver su propia story
        if self.author == user:
            return True

        # Stories públicas pueden ser vistas por cualquiera
        if self.is_public:
            return True

        # TODO: Implementar lógica de amigos/seguidores cuando exista el modelo
        # Por ahora, stories privadas solo las ve el autor
        return False

    def can_view(self, user):
        """Alias para can_be_viewed_by para compatibilidad con las vistas"""
        return self.can_be_viewed_by(user)

    @property
    def is_expired(self):
        """Verificar si la story está expirada"""
        return timezone.now() > self.expires_at

    @property
    def time_remaining(self):
        """Tiempo restante antes de expirar"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - timezone.now()

    @property
    def media_url(self):
        """URL del archivo de media"""
        if self.media_file:
            from utils import FileUploadHandler
            return FileUploadHandler.get_file_url(self.media_file)
        return None

    @property
    def thumbnail_url(self):
        """URL del thumbnail"""
        if self.thumbnail:
            from utils import FileUploadHandler
            return FileUploadHandler.get_file_url(self.thumbnail)
        return None


class StoryView(models.Model):
    """
    Modelo para registrar visualizaciones de stories
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='story_views')
    viewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='story_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    view_duration = models.PositiveIntegerField(
        default=0)  # Duración en segundos

    class Meta:
        unique_together = ['story', 'viewer']
        ordering = ['-viewed_at']
        verbose_name = 'Vista de Story'
        verbose_name_plural = 'Vistas de Stories'
        indexes = [
            models.Index(fields=['story', '-viewed_at']),
            models.Index(fields=['viewer', '-viewed_at']),
        ]

    def __str__(self):
        return f"{self.viewer.username} vio story de {self.story.author.username}"


class StoryLike(models.Model):
    """
    Modelo para likes en stories
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='story_likes')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='story_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['story', 'user']
        ordering = ['-created_at']
        verbose_name = 'Like de Story'
        verbose_name_plural = 'Likes de Stories'
        indexes = [
            models.Index(fields=['story', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} le gustó story de {self.story.author.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar contador
        self.story.likes_count = self.story.story_likes.count()
        self.story.save(update_fields=['likes_count'])

    def delete(self, *args, **kwargs):
        story = self.story
        super().delete(*args, **kwargs)
        # Actualizar contador
        story.likes_count = story.story_likes.count()
        story.save(update_fields=['likes_count'])


class StoryReply(models.Model):
    """
    Modelo para respuestas a stories (mensajes directos)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='story_replies')
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='story_replies_sent')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Respuesta a Story'
        verbose_name_plural = 'Respuestas a Stories'
        indexes = [
            models.Index(fields=['story', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"Respuesta de {self.sender.username} a story de {self.story.author.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar contador
        self.story.replies_count = self.story.story_replies.count()
        self.story.save(update_fields=['replies_count'])


class StoryHighlight(models.Model):
    """
    Modelo para highlights de stories (colecciones guardadas)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='story_highlights')
    title = models.CharField(max_length=100)
    cover_image = models.ImageField(
        upload_to=story_media_path, blank=True, null=True)
    stories = models.ManyToManyField(
        Story, through='StoryHighlightItem', related_name='highlights')

    # Configuración
    is_public = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Highlight'
        verbose_name_plural = 'Highlights'
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['is_public', '-updated_at']),
        ]

    def __str__(self):
        return f"Highlight '{self.title}' de {self.user.username}"

    @property
    def cover_url(self):
        """URL de la imagen de portada"""
        if self.cover_image:
            from utils import FileUploadHandler
            return FileUploadHandler.get_file_url(self.cover_image)
        # Si no hay cover, usar la primera story del highlight
        first_item = self.highlight_items.first()
        if first_item and first_item.story.thumbnail_url:
            return first_item.story.thumbnail_url
        elif first_item and first_item.story.media_url:
            return first_item.story.media_url
        return None

    @property
    def stories_count(self):
        """Número de stories en el highlight"""
        return self.stories.count()


class StoryHighlightItem(models.Model):
    """
    Modelo intermedio para stories en highlights
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    highlight = models.ForeignKey(
        StoryHighlight, on_delete=models.CASCADE, related_name='highlight_items')
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='highlight_items')
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['highlight', 'story']
        ordering = ['order', 'added_at']
        verbose_name = 'Item de Highlight'
        verbose_name_plural = 'Items de Highlights'
        indexes = [
            models.Index(fields=['highlight', 'order']),
        ]

    def __str__(self):
        return f"Story en highlight '{self.highlight.title}'"
