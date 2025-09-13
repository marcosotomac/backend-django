"""
Señales para generar notificaciones automáticamente
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .services import notification_service
from .models import NotificationType

User = get_user_model()


@receiver(post_save, sender='social.Like')
def create_like_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando alguien da like a un post"""
    if (created and instance.like_type == 'post' and
            instance.user != instance.post.author):
        notification_service.create_notification(
            recipient=instance.post.author,
            actor=instance.user,
            notification_type=NotificationType.LIKE,
            title="Nuevo like",
            message=f"{instance.user.get_full_name() or instance.user.username} le dio like a tu post",
            content_object=instance.post,
            extra_data={
                'post_id': str(instance.post.id),
                'post_content': instance.post.content[:100]
            }
        )


@receiver(post_save, sender='social.Comment')
def create_comment_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando alguien comenta un post"""
    if created and instance.author != instance.post.author:
        notification_service.create_notification(
            recipient=instance.post.author,
            actor=instance.author,
            notification_type=NotificationType.COMMENT,
            title="Nuevo comentario",
            message=f"{instance.author.get_full_name() or instance.author.username} comentó en tu post",
            content_object=instance.post,
            extra_data={
                'post_id': str(instance.post.id),
                'comment_id': str(instance.id),
                'comment_content': instance.content[:100]
            }
        )


@receiver(post_save, sender='social.Follow')
def create_follow_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando alguien sigue a un usuario"""
    if created:
        notification_service.create_notification(
            recipient=instance.following,
            actor=instance.follower,
            notification_type=NotificationType.FOLLOW,
            title="Nuevo seguidor",
            message=f"{instance.follower.get_full_name() or instance.follower.username} te está siguiendo",
            content_object=instance.follower,
            extra_data={
                'follower_id': str(instance.follower.id),
                'follower_username': instance.follower.username
            }
        )


@receiver(post_save, sender='chat.Message')
def create_message_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando llega un nuevo mensaje de chat"""
    if created:
        # Notificar a todos los participantes excepto al emisor
        participants = instance.room.participants.exclude(
            id=instance.sender.id)

        for participant in participants:
            # Determinar el título según el tipo de chat
            if instance.room.room_type == 'direct':
                title = "Nuevo mensaje"
                message = f"{instance.sender.get_full_name() or instance.sender.username} te envió un mensaje"
            else:
                room_name = instance.room.name or "Chat grupal"
                title = f"Mensaje en {room_name}"
                message = f"{instance.sender.get_full_name() or instance.sender.username} escribió en {room_name}"

            notification_service.create_notification(
                recipient=participant,
                actor=instance.sender,
                notification_type=NotificationType.MESSAGE,
                title=title,
                message=message,
                content_object=instance.room,
                extra_data={
                    'room_id': str(instance.room.id),
                    'room_type': instance.room.room_type,
                    'message_id': str(instance.id),
                    'message_preview': instance.content[:50] if instance.message_type == 'text' else f"[{instance.message_type}]"
                }
            )


@receiver(post_save, sender='posts.Post')
def create_post_upload_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando un usuario seguido sube un post"""
    if created:
        # Obtener seguidores del autor
        from social.models import Follow

        followers = Follow.objects.filter(
            following=instance.author).select_related('follower')

        # Crear notificaciones para máximo 50 seguidores por vez (para evitar spam)
        for follow in followers[:50]:
            notification_service.create_notification(
                recipient=follow.follower,
                actor=instance.author,
                notification_type=NotificationType.POST_UPLOAD,
                title="Nuevo post",
                message=f"{instance.author.get_full_name() or instance.author.username} subió un nuevo post",
                content_object=instance,
                extra_data={
                    'post_id': str(instance.id),
                    'post_content': instance.content[:100],
                    'author_username': instance.author.username
                }
            )


@receiver(post_save, sender='chat.ChatRoom')
def create_chat_invite_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando se invita a usuarios a un chat grupal"""
    if created and instance.room_type == 'group':
        # Notificar a participantes excepto el creador
        participants = instance.participants.exclude(id=instance.created_by.id)

        for participant in participants:
            room_name = instance.name or "Chat grupal"
            notification_service.create_notification(
                recipient=participant,
                actor=instance.created_by,
                notification_type=NotificationType.CHAT_INVITE,
                title="Invitación a chat",
                message=f"{instance.created_by.get_full_name() or instance.created_by.username} te agregó a {room_name}",
                content_object=instance,
                extra_data={
                    'room_id': str(instance.id),
                    'room_name': room_name,
                    'inviter_username': instance.created_by.username
                }
            )


# Señales para manejar menciones en posts y comentarios
@receiver(post_save, sender='posts.Post')
def create_mention_notification_post(sender, instance, created, **kwargs):
    """Crear notificación para menciones en posts"""
    if created:
        _process_mentions(instance.content, instance.author, instance, 'post')


@receiver(post_save, sender='social.Comment')
def create_mention_notification_comment(sender, instance, created, **kwargs):
    """Crear notificación para menciones en comentarios"""
    if created:
        _process_mentions(instance.content, instance.author,
                          instance, 'comment')


def _process_mentions(content, author, content_object, content_type):
    """Procesar menciones en el contenido y crear notificaciones"""
    import re

    # Buscar menciones @username
    mentions = re.findall(r'@(\w+)', content)

    for username in mentions:
        try:
            mentioned_user = User.objects.get(username=username)
            if mentioned_user != author:  # No notificar al autor

                if content_type == 'post':
                    title = "Te mencionaron"
                    message = f"{author.get_full_name() or author.username} te mencionó en un post"
                    obj = content_object
                else:  # comment
                    title = "Te mencionaron"
                    message = f"{author.get_full_name() or author.username} te mencionó en un comentario"
                    obj = content_object.post  # Para comentarios, usar el post

                notification_service.create_notification(
                    recipient=mentioned_user,
                    actor=author,
                    notification_type=NotificationType.MENTION,
                    title=title,
                    message=message,
                    content_object=obj,
                    extra_data={
                        'mention_context': content_type,
                        'mentioned_in': content[:100],
                        'author_username': author.username
                    }
                )

        except User.DoesNotExist:
            continue  # Usuario mencionado no existe


# Señal para limpiar notificaciones cuando se elimina el objeto relacionado
@receiver(post_delete, sender='posts.Post')
def cleanup_post_notifications(sender, instance, **kwargs):
    """Limpiar notificaciones relacionadas cuando se elimina un post"""
    from django.contrib.contenttypes.models import ContentType
    from .models import UserNotification

    content_type = ContentType.objects.get_for_model(instance)
    UserNotification.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()


@receiver(post_delete, sender='chat.ChatRoom')
def cleanup_chat_notifications(sender, instance, **kwargs):
    """Limpiar notificaciones relacionadas cuando se elimina un chat"""
    from django.contrib.contenttypes.models import ContentType
    from .models import UserNotification

    content_type = ContentType.objects.get_for_model(instance)
    UserNotification.objects.filter(
        content_type=content_type,
        object_id=instance.id
    ).delete()
