from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()


class Follow(models.Model):
    """
    Modelo para el sistema de seguimiento entre usuarios
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'following']
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['following', '-created_at']),
        ]

    def __str__(self):
        return f"{self.follower.username} sigue a {self.following.username}"

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Un usuario no puede seguirse a sí mismo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        # Actualizar contadores
        self.follower.following_count = self.follower.following.count()
        self.follower.save()

        self.following.followers_count = self.following.followers.count()
        self.following.save()

    def delete(self, *args, **kwargs):
        follower = self.follower
        following = self.following

        super().delete(*args, **kwargs)

        # Actualizar contadores
        follower.following_count = follower.following.count()
        follower.save()

        following.followers_count = following.followers.count()
        following.save()


class Like(models.Model):
    """
    Modelo para likes en posts y comentarios
    """
    LIKE_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comentario'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes')
    like_type = models.CharField(max_length=10, choices=LIKE_TYPES)

    # Relaciones opcionales según el tipo
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        'Comment',
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'likes'
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['comment', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(like_type='post'),
                name='unique_user_post_like'
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(like_type='comment'),
                name='unique_user_comment_like'
            ),
        ]

    def __str__(self):
        if self.like_type == 'post' and self.post:
            return f"{self.user.username} le gustó el post de {self.post.author.username}"
        elif self.like_type == 'comment' and self.comment:
            return f"{self.user.username} le gustó el comentario de {self.comment.author.username}"
        return f"Like de {self.user.username}"

    def clean(self):
        if self.like_type == 'post' and not self.post:
            raise ValidationError(
                "Debe especificar un post para el like de tipo 'post'.")
        if self.like_type == 'comment' and not self.comment:
            raise ValidationError(
                "Debe especificar un comentario para el like de tipo 'comment'.")
        if self.like_type == 'post' and self.comment:
            raise ValidationError(
                "No puede especificar un comentario para el like de tipo 'post'.")
        if self.like_type == 'comment' and self.post:
            raise ValidationError(
                "No puede especificar un post para el like de tipo 'comment'.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        # Actualizar contadores
        if self.like_type == 'post' and self.post:
            self.post.likes_count = self.post.likes.count()
            self.post.save()
        elif self.like_type == 'comment' and self.comment:
            self.comment.likes_count = self.comment.likes.count()
            self.comment.save()

    def delete(self, *args, **kwargs):
        post = self.post
        comment = self.comment

        super().delete(*args, **kwargs)

        # Actualizar contadores
        if post:
            post.likes_count = post.likes.count()
            post.save()
        elif comment:
            comment.likes_count = comment.likes.count()
            comment.save()


class Comment(models.Model):
    """
    Modelo para comentarios en posts
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)

    # Para comentarios anidados (respuestas)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True
    )

    # Estadísticas
    likes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
        ]

    def __str__(self):
        return f"Comentario de {self.author.username} en post de {self.post.author.username}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Actualizar contador de comentarios del post
            self.post.comments_count = self.post.comments.count()
            self.post.save()

            # Si es una respuesta, actualizar contador del comentario padre
            if self.parent:
                self.parent.replies_count = self.parent.replies.count()
                self.parent.save()

    def delete(self, *args, **kwargs):
        post = self.post
        parent = self.parent

        super().delete(*args, **kwargs)

        # Actualizar contadores
        post.comments_count = post.comments.count()
        post.save()

        if parent:
            parent.replies_count = parent.replies.count()
            parent.save()


class Notification(models.Model):
    """
    Modelo para notificaciones del usuario
    """
    NOTIFICATION_TYPES = [
        ('like_post', 'Like en Post'),
        ('like_comment', 'Like en Comentario'),
        ('comment', 'Comentario'),
        ('follow', 'Nuevo Seguidor'),
        ('mention', 'Mención'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)

    # Relaciones opcionales
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"Notificación para {self.recipient.username}: {self.message}"
