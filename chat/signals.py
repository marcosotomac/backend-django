"""
Señales para el sistema de chat
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import OnlineStatus, Message

User = get_user_model()


@receiver(post_save, sender=User)
def create_online_status(sender, instance, created, **kwargs):
    """
    Crear estado online cuando se crea un nuevo usuario
    """
    if created:
        OnlineStatus.objects.create(user=instance, is_online=False)


@receiver(post_save, sender=Message)
def update_room_timestamp(sender, instance, created, **kwargs):
    """
    Actualizar timestamp de la sala cuando se crea un mensaje
    """
    if created:
        # Actualizar el updated_at de la sala para reflejar actividad reciente
        room = instance.room
        room.updated_at = instance.created_at
        room.save(update_fields=['updated_at'])
