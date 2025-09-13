from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import re
from utils import post_image_path, post_multiple_images_path, FileUploadHandler

User = get_user_model()


class Post(models.Model):
    """
    Modelo para los posts de la red social
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to=post_image_path, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos para estadísticas
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    # Configuraciones del post
    is_public = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)

    class Meta:
        db_table = 'posts'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f"Post by {self.author.username} - {self.content[:50]}..."

    @property
    def image_url(self):
        """Obtiene la URL completa de la imagen usando el FileUploadHandler"""
        return FileUploadHandler.get_file_url(self.image)

    def get_image_url(self):
        """Método alternativo para compatibilidad"""
        return self.image_url

    def extract_hashtags(self):
        """Extrae hashtags del contenido del post"""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, self.content)
        return [tag.lower() for tag in hashtags]

    def save(self, *args, **kwargs):
        """Override del save para extraer hashtags automáticamente"""
        super().save(*args, **kwargs)

        # Extraer y crear hashtags solo si no existen
        hashtags = self.extract_hashtags()
        for hashtag_name in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            # Usar get_or_create para evitar duplicados
            post_hashtag, created = PostHashtag.objects.get_or_create(
                post=self,
                hashtag=hashtag
            )

            # Actualizar contador solo si es necesario
            current_count = hashtag.posts.count()
            if hashtag.posts_count != current_count:
                hashtag.posts_count = current_count
                hashtag.save()

    def delete_image(self):
        """Elimina la imagen del almacenamiento"""
        if self.image:
            FileUploadHandler.delete_file(self.image)
            self.image = None
            self.save()


class PostImage(models.Model):
    """
    Modelo para múltiples imágenes en un post
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_multiple_images_path)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'post_images'
        verbose_name = 'Imagen de Post'
        verbose_name_plural = 'Imágenes de Posts'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Imagen {self.order} del post {self.post.id}"

    @property
    def image_url(self):
        """Obtiene la URL completa de la imagen usando el FileUploadHandler"""
        return FileUploadHandler.get_file_url(self.image)

    def get_image_url(self):
        """Método alternativo para compatibilidad"""
        return self.image_url

    def delete_image(self):
        """Elimina la imagen del almacenamiento"""
        if self.image:
            FileUploadHandler.delete_file(self.image)
            self.image = None
            self.save()


class Hashtag(models.Model):
    """
    Modelo para hashtags
    """
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    posts_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'hashtags'
        verbose_name = 'Hashtag'
        verbose_name_plural = 'Hashtags'
        ordering = ['-posts_count', 'name']

    def __str__(self):
        return f"#{self.name}"


class PostHashtag(models.Model):
    """
    Modelo intermedio para la relación Post-Hashtag
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_hashtags')
    hashtag = models.ForeignKey(
        Hashtag, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'post_hashtags'
        unique_together = ['post', 'hashtag']
        verbose_name = 'Post Hashtag'
        verbose_name_plural = 'Posts Hashtags'
