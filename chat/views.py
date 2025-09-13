"""
Vistas API para el sistema de chat
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import ChatRoom, Message, OnlineStatus
from .serializers import (
    ChatRoomSerializer, ChatRoomCreateSerializer, MessageSerializer,
    MessageCreateSerializer, OnlineStatusSerializer, DirectChatSerializer,
    MarkMessagesReadSerializer
)

User = get_user_model()


class MessagePagination(PageNumberPagination):
    """Paginación personalizada para mensajes"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet para salas de chat"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def get_queryset(self):
        """Obtener salas donde el usuario es participante"""
        # Para el action 'join', permitir acceso a salas donde no es participante
        if self.action == 'join':
            return ChatRoom.objects.filter(
                is_active=True,
                room_type='group'  # Solo salas grupales para join
            ).prefetch_related(
                'participants',
                'created_by',
            )

        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related(
            'participants',
            'created_by',
            Prefetch(
                'messages',
                queryset=Message.objects.select_related(
                    'sender').order_by('-created_at')[:1],
                to_attr='latest_messages'
            )
        ).order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        """Crear nueva sala de chat"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()

        # Serializar con el serializer de lectura
        read_serializer = ChatRoomSerializer(
            room, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def direct_chat(self, request):
        """Crear o encontrar chat directo con otro usuario"""
        serializer = DirectChatSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        room = serializer.save()

        room_serializer = ChatRoomSerializer(
            room, context={'request': request})
        return Response(room_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Unirse a una sala de chat"""
        room = self.get_object()

        if room.room_type == 'direct':
            return Response(
                {'error': 'No puedes unirte a un chat directo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        room.participants.add(request.user)
        return Response({'message': 'Te has unido a la sala'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Salir de una sala de chat"""
        room = self.get_object()

        if room.room_type == 'direct':
            return Response(
                {'error': 'No puedes salir de un chat directo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        room.participants.remove(request.user)

        # Si es el creador y queda solo 1 persona, desactivar la sala
        if room.created_by == request.user and room.participants.count() <= 1:
            room.is_active = False
            room.save()

        return Response({'message': 'Has salido de la sala'})

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Obtener mensajes de una sala"""
        room = self.get_object()

        messages = Message.objects.filter(
            room=room
        ).select_related(
            'sender', 'reply_to__sender'
        ).prefetch_related(
            'read_by'
        ).order_by('-created_at')

        # Paginación
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request)

        serializer = MessageSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_all_read(self, request, pk=None):
        """Marcar todos los mensajes de la sala como leídos"""
        room = self.get_object()

        serializer = MarkMessagesReadSerializer(
            data={'room_id': str(room.id)},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result)

    @action(detail=True, methods=['get'])
    def online_participants(self, request, pk=None):
        """Obtener participantes online de la sala"""
        room = self.get_object()

        online_statuses = OnlineStatus.objects.filter(
            user__in=room.participants.all(),
            is_online=True
        ).select_related('user')

        serializer = OnlineStatusSerializer(online_statuses, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet para mensajes"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        """Obtener mensajes donde el usuario es participante de la sala"""
        user_rooms = ChatRoom.objects.filter(participants=self.request.user)

        return Message.objects.filter(
            room__in=user_rooms
        ).select_related(
            'sender', 'room', 'reply_to__sender'
        ).prefetch_related(
            'read_by'
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Crear nuevo mensaje"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Serializar con el serializer de lectura
        read_serializer = MessageSerializer(
            message, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Editar mensaje (solo el autor puede editar)"""
        message = self.get_object()

        if message.sender != request.user:
            return Response(
                {'error': 'Solo puedes editar tus propios mensajes'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Eliminar mensaje (soft delete)"""
        message = self.get_object()

        if message.sender != request.user:
            return Response(
                {'error': 'Solo puedes eliminar tus propios mensajes'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Soft delete
        message.is_deleted = True
        message.content = "[Mensaje eliminado]"
        message.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Marcar mensajes específicos como leídos"""
        serializer = MarkMessagesReadSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Buscar mensajes por contenido"""
        query = request.query_params.get('q', '').strip()
        room_id = request.query_params.get('room_id')

        if not query:
            return Response(
                {'error': 'Parámetro de búsqueda requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        messages = self.get_queryset().filter(
            content__icontains=query,
            is_deleted=False
        )

        if room_id:
            messages = messages.filter(room_id=room_id)

        # Paginación
        page = self.paginate_queryset(messages)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class OnlineStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para estados online (solo lectura)"""
    serializer_class = OnlineStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Obtener estados online de usuarios relacionados"""
        # Obtener usuarios con los que el usuario actual tiene salas de chat
        user_rooms = ChatRoom.objects.filter(participants=self.request.user)
        related_users = User.objects.filter(
            chat_rooms__in=user_rooms
        ).exclude(id=self.request.user.id).distinct()

        return OnlineStatus.objects.filter(
            user__in=related_users
        ).select_related('user')

    @action(detail=False, methods=['get'])
    def my_status(self, request):
        """Obtener mi estado online"""
        try:
            status_obj = OnlineStatus.objects.get(user=request.user)
            serializer = self.get_serializer(status_obj)
            return Response(serializer.data)
        except OnlineStatus.DoesNotExist:
            return Response(
                {'is_online': False, 'last_seen': None},
                status=status.HTTP_404_NOT_FOUND
            )
