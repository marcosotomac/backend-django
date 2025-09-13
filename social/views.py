from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Follow, Like, Comment, Notification
from posts.models import Post
from .serializers import (
    FollowSerializer, CommentSerializer, CommentCreateSerializer,
    LikeSerializer, NotificationSerializer, FollowerSerializer,
    FollowingSerializer
)

User = get_user_model()


# Follow System Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    """
    Seguir a un usuario
    """
    user_to_follow = get_object_or_404(User, username=username)
    current_user = request.user

    if current_user == user_to_follow:
        return Response({
            'error': 'No puedes seguirte a ti mismo'
        }, status=status.HTTP_400_BAD_REQUEST)

    follow, created = Follow.objects.get_or_create(
        follower=current_user,
        following=user_to_follow
    )

    if created:
        # Crear notificación
        Notification.objects.create(
            recipient=user_to_follow,
            sender=current_user,
            notification_type='follow',
            message=f'{current_user.username} comenzó a seguirte'
        )

        return Response({
            'message': f'Ahora sigues a {user_to_follow.username}',
            'following': True
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'message': f'Ya sigues a {user_to_follow.username}',
            'following': True
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, username):
    """
    Dejar de seguir a un usuario
    """
    user_to_unfollow = get_object_or_404(User, username=username)
    current_user = request.user

    if current_user == user_to_unfollow:
        return Response({
            'error': 'No puedes dejar de seguirte a ti mismo'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        follow = Follow.objects.get(
            follower=current_user,
            following=user_to_unfollow
        )
        follow.delete()

        return Response({
            'message': f'Dejaste de seguir a {user_to_unfollow.username}',
            'following': False
        }, status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        return Response({
            'message': f'No seguías a {user_to_unfollow.username}',
            'following': False
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def followers_list(request, username):
    """
    Lista de seguidores de un usuario
    """
    user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(following=user).order_by('-created_at')

    # Paginación manual simple
    page_size = 20
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    paginated_follows = follows[start:end]
    serializer = FollowerSerializer(paginated_follows, many=True)

    return Response({
        'followers': serializer.data,
        'count': follows.count(),
        'page': page,
        'has_next': end < follows.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def following_list(request, username):
    """
    Lista de usuarios que sigue un usuario
    """
    user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(follower=user).order_by('-created_at')

    # Paginación manual simple
    page_size = 20
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    paginated_follows = follows[start:end]
    serializer = FollowingSerializer(paginated_follows, many=True)

    return Response({
        'following': serializer.data,
        'count': follows.count(),
        'page': page,
        'has_next': end < follows.count()
    })


# Like System Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    """
    Dar like a un post
    """
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    like, created = Like.objects.get_or_create(
        user=user,
        post=post,
        like_type='post'
    )

    if created:
        # Crear notificación si no es el propio post
        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                sender=user,
                notification_type='like_post',
                message=f'{user.username} le gustó tu post',
                post=post
            )

        return Response({
            'message': 'Like agregado',
            'liked': True,
            'likes_count': post.likes_count
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'message': 'Ya te gusta este post',
            'liked': True,
            'likes_count': post.likes_count
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlike_post(request, post_id):
    """
    Quitar like de un post
    """
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    try:
        like = Like.objects.get(
            user=user,
            post=post,
            like_type='post'
        )
        like.delete()

        return Response({
            'message': 'Like removido',
            'liked': False,
            'likes_count': post.likes_count
        }, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({
            'message': 'No habías dado like a este post',
            'liked': False,
            'likes_count': post.likes_count
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_comment(request, comment_id):
    """
    Dar like a un comentario
    """
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    like, created = Like.objects.get_or_create(
        user=user,
        comment=comment,
        like_type='comment'
    )

    if created:
        # Crear notificación si no es el propio comentario
        if comment.author != user:
            Notification.objects.create(
                recipient=comment.author,
                sender=user,
                notification_type='like_comment',
                message=f'{user.username} le gustó tu comentario',
                comment=comment,
                post=comment.post
            )

        return Response({
            'message': 'Like agregado al comentario',
            'liked': True,
            'likes_count': comment.likes_count
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'message': 'Ya te gusta este comentario',
            'liked': True,
            'likes_count': comment.likes_count
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlike_comment(request, comment_id):
    """
    Quitar like de un comentario
    """
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    try:
        like = Like.objects.get(
            user=user,
            comment=comment,
            like_type='comment'
        )
        like.delete()

        return Response({
            'message': 'Like removido del comentario',
            'liked': False,
            'likes_count': comment.likes_count
        }, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({
            'message': 'No habías dado like a este comentario',
            'liked': False,
            'likes_count': comment.likes_count
        }, status=status.HTTP_200_OK)


# Comment System Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_comment(request, post_id):
    """
    Crear un comentario en un post
    """
    post = get_object_or_404(Post, id=post_id)

    if not post.allow_comments:
        return Response({
            'error': 'Este post no permite comentarios'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = CommentCreateSerializer(
        data=request.data,
        context={'request': request, 'post': post}
    )

    if serializer.is_valid():
        comment = serializer.save(author=request.user, post=post)

        # Crear notificación si no es el propio post
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                message=f'{request.user.username} comentó tu post',
                comment=comment,
                post=post
            )

        return Response({
            'message': 'Comentario creado exitosamente',
            'comment': CommentSerializer(comment, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reply_comment(request, comment_id):
    """
    Responder a un comentario
    """
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post

    if not post.allow_comments:
        return Response({
            'error': 'Este post no permite comentarios'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = CommentCreateSerializer(
        data=request.data,
        context={'request': request, 'post': post}
    )

    if serializer.is_valid():
        comment = serializer.save(
            author=request.user,
            post=post,
            parent=parent_comment
        )

        # Crear notificación si no es el propio comentario
        if parent_comment.author != request.user:
            Notification.objects.create(
                recipient=parent_comment.author,
                sender=request.user,
                notification_type='comment',
                message=f'{request.user.username} respondió tu comentario',
                comment=comment,
                post=post
            )

        return Response({
            'message': 'Respuesta creada exitosamente',
            'comment': CommentSerializer(comment, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def comment_detail(request, comment_id):
    """
    Obtener detalles de un comentario específico
    """
    comment = get_object_or_404(Comment, id=comment_id)
    serializer = CommentSerializer(comment, context={'request': request})

    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_comment(request, comment_id):
    """
    Actualizar un comentario propio
    """
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    serializer = CommentCreateSerializer(
        comment,
        data=request.data,
        partial=True,
        context={'request': request, 'post': comment.post}
    )

    if serializer.is_valid():
        comment = serializer.save()

        return Response({
            'message': 'Comentario actualizado exitosamente',
            'comment': CommentSerializer(comment, context={'request': request}).data
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_comment(request, comment_id):
    """
    Eliminar un comentario propio
    """
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()

    return Response({
        'message': 'Comentario eliminado exitosamente'
    }, status=status.HTTP_200_OK)


# Notification Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notifications_list(request):
    """
    Lista de notificaciones del usuario
    """
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    # Paginación manual simple
    page_size = 20
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    paginated_notifications = notifications[start:end]
    serializer = NotificationSerializer(paginated_notifications, many=True)

    # Contar notificaciones no leídas
    unread_count = notifications.filter(is_read=False).count()

    return Response({
        'notifications': serializer.data,
        'count': notifications.count(),
        'unread_count': unread_count,
        'page': page,
        'has_next': end < notifications.count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """
    Marcar notificaciones como leídas
    """
    notification_ids = request.data.get('notification_ids', [])

    if notification_ids:
        # Marcar notificaciones específicas
        updated = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            'message': f'{updated} notificaciones marcadas como leídas'
        })
    else:
        # Marcar todas como leídas
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            'message': f'Todas las notificaciones ({updated}) marcadas como leídas'
        })


# Additional helper views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def post_comments(request, post_id):
    """
    Obtener comentarios de un post específico
    """
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(
        post=post,
        parent=None  # Solo comentarios principales
    ).order_by('-created_at')

    # Paginación manual simple
    page_size = 10
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    paginated_comments = comments[start:end]
    serializer = CommentSerializer(
        paginated_comments,
        many=True,
        context={'request': request}
    )

    return Response({
        'comments': serializer.data,
        'count': comments.count(),
        'page': page,
        'has_next': end < comments.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_follow_status(request, username):
    """
    Verificar si el usuario actual sigue a otro usuario
    """
    user_to_check = get_object_or_404(User, username=username)

    if request.user == user_to_check:
        return Response({
            'is_following': False,
            'is_self': True
        })

    is_following = Follow.objects.filter(
        follower=request.user,
        following=user_to_check
    ).exists()

    return Response({
        'is_following': is_following,
        'is_self': False
    })
