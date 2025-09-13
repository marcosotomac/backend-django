"""
Views para el sistema de Stories
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Max, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from .models import (
    Story, StoryView, StoryLike, StoryReply,
    StoryHighlight, StoryHighlightItem
)
from .serializers import (
    StorySerializer, StoryCreateSerializer, StoryListSerializer,
    StoryViewSerializer, StoryLikeSerializer, StoryReplySerializer,
    StoryHighlightSerializer, StoryHighlightCreateSerializer,
    UserStoriesSerializer, StoryStatsSerializer,
    StoryViewCreateSerializer, StoryReplyCreateSerializer
)


class StoryPagination(PageNumberPagination):
    """Paginación personalizada para stories"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class StoryViewSet(viewsets.ModelViewSet):
    """ViewSet para Stories"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StoryPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return StoryCreateSerializer
        elif self.action == 'list':
            return StoryListSerializer
        return StorySerializer

    def get_queryset(self):
        """Obtener stories del usuario actual o visibles para él"""
        user = self.request.user

        # Filtro por usuario específico
        username = self.request.query_params.get('username')
        if username:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                target_user = User.objects.get(username=username)
                if target_user == user:
                    # Propias stories (incluyendo expiradas)
                    return Story.objects.filter(author=user).order_by('-created_at')
                else:
                    # Stories públicas activas del usuario objetivo
                    return Story.objects.active().filter(
                        author=target_user,
                        is_public=True
                    ).order_by('-created_at')
            except:
                return Story.objects.none()

        # Stories del feed (usuarios que sigue + propias)
        return Story.objects.for_user(user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Crear nueva story"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        story = serializer.save()

        # Enviar notificación a seguidores (opcional)
        self._notify_followers(story)

        # Respuesta con serializer completo
        response_serializer = StorySerializer(
            story, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Eliminar story (solo el autor)"""
        story = self.get_object()

        if story.author != request.user:
            return Response(
                {'error': 'No tienes permisos para eliminar esta story'},
                status=status.HTTP_403_FORBIDDEN
            )

        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Registrar visualización de story"""
        story = self.get_object()

        # Verificar permisos
        if not story.can_view(request.user):
            return Response(
                {'error': 'No tienes permisos para ver esta story'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StoryViewCreateSerializer(
            data=request.data,
            context={'story': story, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        view = serializer.save()

        return Response(StoryViewSerializer(view).data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Dar like a una story"""
        story = self.get_object()

        if not story.can_view(request.user):
            return Response(
                {'error': 'No tienes permisos para interactuar con esta story'},
                status=status.HTTP_403_FORBIDDEN
            )

        like, created = StoryLike.objects.get_or_create(
            story=story,
            user=request.user
        )

        if created:
            # Crear notificación si no es el autor
            if story.author != request.user:
                self._create_like_notification(story, request.user)

            return Response({
                'message': 'Like agregado',
                'liked': True,
                'likes_count': story.likes_count
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Ya te gusta esta story',
                'liked': True,
                'likes_count': story.likes_count
            }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """Quitar like de una story"""
        story = self.get_object()

        try:
            like = StoryLike.objects.get(story=story, user=request.user)
            like.delete()

            return Response({
                'message': 'Like removido',
                'liked': False,
                'likes_count': story.likes_count
            }, status=status.HTTP_200_OK)
        except StoryLike.DoesNotExist:
            return Response({
                'message': 'No habías dado like a esta story',
                'liked': False,
                'likes_count': story.likes_count
            }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Responder a una story"""
        story = self.get_object()

        if not story.allow_replies:
            return Response(
                {'error': 'Esta story no permite respuestas'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not story.can_view(request.user):
            return Response(
                {'error': 'No tienes permisos para responder esta story'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StoryReplyCreateSerializer(
            data=request.data,
            context={'story': story, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        reply = serializer.save()

        # Crear notificación al autor
        if story.author != request.user:
            self._create_reply_notification(story, request.user, reply)

        return Response(
            StoryReplySerializer(reply).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Obtener stories agrupadas por usuario para el feed"""
        user = request.user

        # Obtener stories activas de usuarios que sigue + propias
        stories = Story.objects.for_user(user).select_related('author')

        # Agrupar por usuario
        users_stories = {}
        for story in stories:
            author_id = story.author.id
            if author_id not in users_stories:
                users_stories[author_id] = {
                    'user': story.author,
                    'stories': [],
                    'unviewed_count': 0,
                    'latest_story_time': story.created_at
                }

            users_stories[author_id]['stories'].append(story)

            # Contar no vistas
            if not StoryView.objects.filter(story=story, viewer=user).exists():
                users_stories[author_id]['unviewed_count'] += 1

        # Convertir a lista y ordenar por actividad
        result = list(users_stories.values())
        result.sort(key=lambda x: x['latest_story_time'], reverse=True)

        # Serializar
        serializer = UserStoriesSerializer(
            result, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Obtener estadísticas de una story"""
        story = self.get_object()

        # Solo el autor puede ver las estadísticas
        if story.author != request.user:
            return Response(
                {'error': 'Solo el autor puede ver las estadísticas'},
                status=status.HTTP_403_FORBIDDEN
            )

        stats = {
            'views_count': story.views_count,
            'likes_count': story.likes_count,
            'replies_count': story.replies_count,
            'recent_viewers': []
        }

        # Agregar visualizadores recientes (últimos 10)
        recent_views = StoryView.objects.filter(
            story=story).order_by('-viewed_at')[:10]
        for view in recent_views:
            stats['recent_viewers'].append({
                'user': {
                    'id': str(view.viewer.id),
                    'username': view.viewer.username,
                    'full_name': view.viewer.get_full_name(),
                    'avatar': view.viewer.avatar_url if view.viewer.avatar else None
                },
                'viewed_at': view.viewed_at,
                'view_duration': view.view_duration
            })

        return Response(stats)

    def _notify_followers(self, story):
        """Enviar notificación a seguidores sobre nueva story"""
        # Implementar notificación (opcional)
        pass

    def _create_like_notification(self, story, user):
        """Crear notificación de like en story"""
        from notifications.services import notification_service
        from notifications.models import NotificationType

        notification_service.create_notification(
            recipient=story.author,
            actor=user,
            notification_type=NotificationType.LIKE,
            title="Like en story",
            message=f"{user.get_full_name() or user.username} le gustó tu story",
            content_object=story,
            extra_data={
                'story_id': str(story.id),
                'story_type': story.story_type
            }
        )

    def _create_reply_notification(self, story, user, reply):
        """Crear notificación de respuesta a story"""
        from notifications.services import notification_service
        from notifications.models import NotificationType

        notification_service.create_notification(
            recipient=story.author,
            actor=user,
            notification_type=NotificationType.MESSAGE,
            title="Respuesta a story",
            message=f"{user.get_full_name() or user.username} respondió a tu story",
            content_object=story,
            extra_data={
                'story_id': str(story.id),
                'reply_id': str(reply.id),
                'reply_content': reply.content[:50]
            }
        )


class StoryHighlightViewSet(viewsets.ModelViewSet):
    """ViewSet para Highlights de Stories"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return StoryHighlightCreateSerializer
        return StoryHighlightSerializer

    def get_queryset(self):
        """Obtener highlights del usuario actual o públicos"""
        user = self.request.user

        # Filtro por usuario específico
        username = self.request.query_params.get('username')
        if username:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                target_user = User.objects.get(username=username)

                if target_user == user:
                    # Propios highlights
                    return StoryHighlight.objects.filter(user=user).order_by('-updated_at')
                else:
                    # Highlights públicos del usuario objetivo
                    return StoryHighlight.objects.filter(
                        user=target_user,
                        is_public=True
                    ).order_by('-updated_at')
            except:
                return StoryHighlight.objects.none()

        # Propios highlights por defecto
        return StoryHighlight.objects.filter(user=user).order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        """Crear nuevo highlight"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        highlight = serializer.save()

        response_serializer = StoryHighlightSerializer(
            highlight, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_story(self, request, pk=None):
        """Agregar story a highlight"""
        highlight = self.get_object()

        # Solo el propietario puede agregar stories
        if highlight.user != request.user:
            return Response(
                {'error': 'No tienes permisos para modificar este highlight'},
                status=status.HTTP_403_FORBIDDEN
            )

        story_id = request.data.get('story_id')
        if not story_id:
            return Response(
                {'error': 'story_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            story = Story.objects.get(id=story_id, author=request.user)
        except Story.DoesNotExist:
            return Response(
                {'error': 'Story no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar si ya está en el highlight
        if StoryHighlightItem.objects.filter(highlight=highlight, story=story).exists():
            return Response(
                {'error': 'La story ya está en este highlight'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Agregar story al highlight
        StoryHighlightItem.objects.create(
            highlight=highlight,
            story=story,
            order=highlight.highlight_items.count() + 1
        )

        return Response({
            'message': 'Story agregada al highlight',
            'stories_count': highlight.stories_count
        }, status=status.HTTP_200_OK)
