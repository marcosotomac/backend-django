"""
Señales para el sistema de Stories
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from notifications.models import UserNotification
from .models import Story, StoryLike, StoryReply, StoryView


@receiver(post_save, sender=StoryLike)
def create_story_like_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando alguien da like a una story"""
    if created and instance.story.author != instance.user:
        UserNotification.objects.create(
            recipient=instance.story.author,
            actor=instance.user,
            notification_type='like',  # Usando tipo existente
            title='Nueva reacción en tu story',
            message=f'{instance.user.get_full_name() or instance.user.username} reaccionó a tu story',
            content_object=instance.story,
            extra_data={
                'story_id': str(instance.story.id),
                'liker_id': str(instance.user.id),
                'liker_username': instance.user.username,
                'story_type': instance.story.story_type
            }
        )


@receiver(post_save, sender=StoryReply)
def create_story_reply_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando alguien responde a una story"""
    if created and instance.story.author != instance.sender:
        UserNotification.objects.create(
            recipient=instance.story.author,
            actor=instance.sender,
            notification_type='comment',  # Usando tipo existente
            title='Nueva respuesta a tu story',
            message=f'{instance.sender.get_full_name() or instance.sender.username} respondió a tu story',
            content_object=instance.story,
            extra_data={
                'story_id': str(instance.story.id),
                'reply_id': str(instance.id),
                'sender_id': str(instance.sender.id),
                'sender_username': instance.sender.username,
                'reply_content': instance.content[:100],
                'story_type': instance.story.story_type
            }
        )


@receiver(post_save, sender=StoryView)
def create_story_view_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando alguien ve una story (solo para el primer view del día)"""
    if created and instance.story.author != instance.viewer:
        # Solo notificar si es la primera visualización del día de este usuario
        today = timezone.now().date()
        previous_views_today = StoryView.objects.filter(
            story__author=instance.story.author,
            viewer=instance.viewer,
            viewed_at__date=today
        ).exclude(id=instance.id).exists()

        if not previous_views_today:
            # Contar total de visualizaciones del usuario hoy
            total_views_today = StoryView.objects.filter(
                story__author=instance.story.author,
                viewer=instance.viewer,
                viewed_at__date=today
            ).count()

            UserNotification.objects.create(
                recipient=instance.story.author,
                actor=instance.viewer,
                notification_type='system',  # Usando tipo existente
                title='Alguien vio tus stories',
                message=f'{instance.viewer.get_full_name() or instance.viewer.username} vio tus stories',
                content_object=instance.story,
                extra_data={
                    'viewer_id': str(instance.viewer.id),
                    'viewer_username': instance.viewer.username,
                    'total_views_today': total_views_today,
                    'story_id': str(instance.story.id)
                }
            )


@receiver(post_save, sender=Story)
def story_created_notification(sender, instance, created, **kwargs):
    """Notificar a seguidores cercanos cuando se crea una nueva story"""
    if created and instance.is_public:
        # TODO: Implementar notificaciones a seguidores cuando exista el modelo Follow
        # Por ahora comentado hasta que se implemente el sistema de seguimiento

        # # Obtener seguidores que han tenido interacciones recientes
        # from users.models import Follow
        # from django.db.models import Q

        # recent_followers = Follow.objects.filter(
        #     following=instance.author,
        #     created_at__gte=timezone.now() - timezone.timedelta(days=7)
        # ).select_related('follower')

        # # Limitar a los primeros 50 seguidores para evitar spam
        # for follow in recent_followers[:50]:
        #     UserNotification.objects.create(
        #         user=follow.follower,
        #         notification_type='story_posted',
        #         title='Nueva story disponible',
        #         message=f'{instance.author.get_full_name() or instance.author.username} publicó una nueva story',
        #         metadata={
        #             'story_id': str(instance.id),
        #             'author_id': str(instance.author.id),
        #             'author_username': instance.author.username,
        #             'story_type': instance.story_type
        #         }
        #     )
        pass


@receiver(post_delete, sender=Story)
def cleanup_story_files(sender, instance, **kwargs):
    """Limpiar archivos cuando se elimina una story"""
    if instance.media_file:
        try:
            instance.media_file.delete(save=False)
        except:
            pass

    if instance.thumbnail:
        try:
            instance.thumbnail.delete(save=False)
        except:
            pass
