from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from utils import user_avatar_path, FileUploadHandler


class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    bio = models.TextField(max_length=500, blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Campos adicionales para estadísticas
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (@{self.username})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def avatar_url(self):
        """Obtiene la URL completa del avatar usando el FileUploadHandler"""
        return FileUploadHandler.get_file_url(self.avatar)

    def get_avatar_url(self):
        """Método alternativo para compatibilidad"""
        return self.avatar_url

    def delete_avatar(self):
        """Elimina el avatar del almacenamiento"""
        if self.avatar:
            FileUploadHandler.delete_file(self.avatar)
            self.avatar = None
            self.save()
