"""
Tests para el sistema de notificaciones
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from notifications.models import (
    UserNotification, NotificationSettings, DeviceToken,
    NotificationBatch, NotificationType
)
from notifications.services import notification_service
from social.models import Follow, Like, Comment
from posts.models import Post

User = get_user_model()


class NotificationModelTests(TestCase):
    """Tests para los modelos de notificaciones"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )

    def test_create_notification(self):
        """Test crear notificación básica"""
        notification = UserNotification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            title="Test notification",
            message="This is a test",
            notification_type=NotificationType.SYSTEM
        )

        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.actor, self.user2)
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)

    def test_mark_as_read(self):
        """Test marcar notificación como leída"""
        notification = UserNotification.objects.create(
            recipient=self.user1,
            title="Test",
            message="Test",
            notification_type=NotificationType.SYSTEM
        )

        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_notification_settings(self):
        """Test configuración de notificaciones"""
        settings = NotificationSettings.objects.create(user=self.user1)

        self.assertTrue(settings.likes_enabled)
        self.assertTrue(settings.comments_enabled)
        self.assertTrue(settings.follows_enabled)

        # Test verificar si está habilitado
        self.assertTrue(settings.is_notification_enabled(
            NotificationType.LIKE))

        settings.likes_enabled = False
        settings.save()
        self.assertFalse(
            settings.is_notification_enabled(NotificationType.LIKE))


class NotificationServiceTests(TestCase):
    """Tests para el servicio de notificaciones"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )

    def test_create_notification_via_service(self):
        """Test crear notificación usando el servicio"""
        notification = notification_service.create_notification(
            recipient=self.user1,
            actor=self.user2,
            notification_type=NotificationType.LIKE,
            title="New like",
            message="Someone liked your post",
            extra_data={'test': True}
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.extra_data['test'], True)

    def test_get_user_stats(self):
        """Test obtener estadísticas de usuario"""
        # Crear algunas notificaciones
        for i in range(3):
            notification_service.create_notification(
                recipient=self.user1,
                notification_type=NotificationType.LIKE,
                title=f"Like {i}",
                message=f"Like message {i}"
            )

        stats = notification_service.get_user_stats(self.user1)

        self.assertEqual(stats['total_notifications'], 3)
        self.assertEqual(stats['unread_notifications'], 3)
        self.assertEqual(stats['likes_count'], 3)

    def test_mark_notifications_read(self):
        """Test marcar notificaciones como leídas"""
        # Crear notificaciones
        notifications = []
        for i in range(3):
            notif = notification_service.create_notification(
                recipient=self.user1,
                notification_type=NotificationType.LIKE,
                title=f"Like {i}",
                message=f"Like message {i}"
            )
            notifications.append(notif)

        # Marcar algunas como leídas
        count = notification_service.mark_notifications_read(
            user=self.user1,
            notification_ids=[str(notifications[0].id),
                              str(notifications[1].id)]
        )

        self.assertEqual(count, 2)

        # Verificar estado
        notifications[0].refresh_from_db()
        notifications[1].refresh_from_db()
        notifications[2].refresh_from_db()

        self.assertTrue(notifications[0].is_read)
        self.assertTrue(notifications[1].is_read)
        self.assertFalse(notifications[2].is_read)


class NotificationSignalTests(TestCase):
    """Tests para las señales de notificaciones"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )

    def test_follow_notification_signal(self):
        """Test señal de notificación de seguimiento"""
        initial_count = UserNotification.objects.count()

        # Crear seguimiento
        Follow.objects.create(
            follower=self.user1,
            following=self.user2
        )

        # Verificar que se creó la notificación
        self.assertEqual(UserNotification.objects.count(), initial_count + 1)

        notification = UserNotification.objects.filter(
            recipient=self.user2,
            actor=self.user1,
            notification_type=NotificationType.FOLLOW
        ).first()

        self.assertIsNotNone(notification)
        self.assertIn("siguiendo", notification.message)

    def test_post_like_notification_signal(self):
        """Test señal de notificación de like en post"""
        # Crear un post
        post = Post.objects.create(
            author=self.user1,
            content="Test post"
        )

        initial_count = UserNotification.objects.count()

        # Crear like
        Like.objects.create(
            user=self.user2,
            post=post,
            like_type='post'
        )

        # Verificar que se creó la notificación
        self.assertEqual(UserNotification.objects.count(), initial_count + 1)

        notification = UserNotification.objects.filter(
            recipient=self.user1,
            actor=self.user2,
            notification_type=NotificationType.LIKE
        ).first()

        self.assertIsNotNone(notification)
        self.assertIn("like", notification.message)
