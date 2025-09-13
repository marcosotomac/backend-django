"""
URLs para las APIs del sistema de notificaciones
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet,
                basename='notification')
router.register(r'settings', views.NotificationSettingsViewSet,
                basename='notification-settings')
router.register(r'devices', views.DeviceTokenViewSet, basename='device-token')
router.register(r'batches', views.NotificationBatchViewSet,
                basename='notification-batch')

urlpatterns = [
    path('api/notifications/', include(router.urls)),
]
