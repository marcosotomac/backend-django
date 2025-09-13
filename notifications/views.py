"""
Vistas API para el sistema de notificaciones
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import (
    UserNotification, NotificationSettings, DeviceToken,
    NotificationBatch, NotificationType
)
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer,
    NotificationSettingsSerializer, DeviceTokenSerializer,
    NotificationBatchSerializer, NotificationStatsSerializer,
    MarkNotificationsReadSerializer, NotificationPreferencesSerializer
)
from .services import notification_service


class NotificationPagination(PageNumberPagination):
    """Paginación personalizada para notificaciones"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet para notificaciones"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    def get_queryset(self):
        """Obtener notificaciones del usuario actual"""
        queryset = UserNotification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'actor', 'content_type'
        ).order_by('-created_at')

        # Filtros opcionales
        notification_type = self.request.query_params.get('type')
        is_read = self.request.query_params.get('is_read')

        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        if is_read is not None:
            is_read_bool = is_read.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_read=is_read_bool)

        return queryset

    def create(self, request, *args, **kwargs):
        """Crear nueva notificación (solo para admin/sistema)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para crear notificaciones'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Crear usando el servicio
        notification = notification_service.create_notification(
            recipient=serializer.validated_data['recipient'],
            notification_type=serializer.validated_data['notification_type'],
            title=serializer.validated_data['title'],
            message=serializer.validated_data['message'],
            actor=serializer.validated_data.get('actor'),
            extra_data=serializer.validated_data.get('extra_data', {})
        )

        if notification:
            read_serializer = NotificationSerializer(notification)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'No se pudo crear la notificación'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marcar notificación específica como leída"""
        notification = self.get_object()
        notification.mark_as_read()

        return Response({'message': 'Notificación marcada como leída'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marcar todas las notificaciones como leídas"""
        count = notification_service.mark_notifications_read(
            user=request.user,
            mark_all=True
        )

        return Response({
            'message': f'{count} notificaciones marcadas como leídas'
        })

    @action(detail=False, methods=['post'])
    def mark_selected_read(self, request):
        """Marcar notificaciones seleccionadas como leídas"""
        serializer = MarkNotificationsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        count = notification_service.mark_notifications_read(
            user=request.user,
            notification_ids=serializer.validated_data.get('notification_ids'),
            mark_all=serializer.validated_data.get('mark_all', False)
        )

        return Response({
            'marked_count': count,
            'message': f'{count} notificaciones marcadas como leídas'
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obtener conteo de notificaciones no leídas"""
        count = UserNotification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({'unread_count': count})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas de notificaciones"""
        stats = notification_service.get_user_stats(request.user)
        serializer = NotificationStatsSerializer(data=stats)
        serializer.is_valid()

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def types(self, request):
        """Obtener tipos de notificaciones disponibles"""
        serializer = NotificationPreferencesSerializer(data={})
        serializer.is_valid()

        return Response(serializer.to_representation(None))

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Eliminar todas las notificaciones leídas"""
        if not request.user.is_staff:
            # Solo usuarios normales pueden eliminar sus propias notificaciones leídas
            count = UserNotification.objects.filter(
                recipient=request.user,
                is_read=True
            ).count()

            UserNotification.objects.filter(
                recipient=request.user,
                is_read=True
            ).delete()
        else:
            # Staff puede especificar días
            days = request.query_params.get('days', 30)
            count = notification_service.cleanup_old_notifications(int(days))

        return Response({
            'deleted_count': count,
            'message': f'{count} notificaciones eliminadas'
        })


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet para configuración de notificaciones"""
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']  # No permitir POST/DELETE

    def get_object(self):
        """Obtener configuración del usuario actual"""
        return notification_service.get_user_settings(self.request.user)

    def get_queryset(self):
        """Queryset dummy ya que trabajamos con un objeto único"""
        return NotificationSettings.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Obtener configuración actual"""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Actualizar configuración"""
        settings = self.get_object()
        serializer = self.get_serializer(
            settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """ViewSet para tokens de dispositivos"""
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Obtener tokens del usuario actual"""
        return DeviceToken.objects.filter(
            user=self.request.user
        ).order_by('-last_used')

    def create(self, request, *args, **kwargs):
        """Registrar token de dispositivo"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_token = serializer.save()

        return Response(
            DeviceTokenSerializer(device_token).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactivar token de dispositivo"""
        device_token = self.get_object()
        device_token.is_active = False
        device_token.save()

        return Response({'message': 'Token desactivado'})

    @action(detail=False, methods=['post'])
    def cleanup_inactive(self, request):
        """Limpiar tokens inactivos antiguos"""
        from django.utils import timezone
        from datetime import timedelta

        # Eliminar tokens inactivos de más de 30 días
        threshold = timezone.now() - timedelta(days=30)
        count = DeviceToken.objects.filter(
            user=request.user,
            is_active=False,
            last_used__lt=threshold
        ).count()

        DeviceToken.objects.filter(
            user=request.user,
            is_active=False,
            last_used__lt=threshold
        ).delete()

        return Response({
            'deleted_count': count,
            'message': f'{count} tokens eliminados'
        })


class NotificationBatchViewSet(viewsets.ModelViewSet):
    """ViewSet para lotes de notificaciones (solo staff)"""
    serializer_class = NotificationBatchSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        """Obtener lotes del usuario actual (si es staff)"""
        return NotificationBatch.objects.filter(
            created_by=self.request.user
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Enviar lote de notificaciones"""
        batch = self.get_object()

        if batch.status != 'draft':
            return Response(
                {'error': 'El lote no está en estado borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = notification_service.send_batch_notification(batch)

        if success:
            return Response({'message': 'Lote enviado exitosamente'})
        else:
            return Response(
                {'error': 'Error enviando el lote'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
