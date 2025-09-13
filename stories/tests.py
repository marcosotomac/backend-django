"""
Tests para el sistema de Stories
"""
import tempfile
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    Story, StoryView, StoryLike, StoryReply,
    StoryHighlight, StoryHighlightItem
)

User = get_user_model()


class StoryModelTest(TestCase):
    """Tests para el modelo Story"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_story_creation(self):
        """Test creación básica de story"""
        story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Test story content'
        )

        self.assertEqual(story.author, self.user)
        self.assertEqual(story.story_type, 'text')
        self.assertEqual(story.content, 'Test story content')
        self.assertTrue(story.is_public)
        self.assertFalse(story.is_expired)

        # Verificar que expire en 24 horas por defecto
        expected_expiry = timezone.now() + timedelta(hours=24)
        self.assertAlmostEqual(
            story.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=60  # 1 minuto de tolerancia
        )

    def test_story_expiration(self):
        """Test lógica de expiración de stories"""
        # Story no expirada
        story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Test story',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        self.assertFalse(story.is_expired)

        # Story expirada
        expired_story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Expired story',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        self.assertTrue(expired_story.is_expired)

    def test_story_permissions(self):
        """Test permisos de visualización de stories"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Story pública
        public_story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Public story',
            is_public=True
        )
        self.assertTrue(public_story.can_be_viewed_by(other_user))

        # Story privada
        private_story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Private story',
            is_public=False
        )
        self.assertFalse(private_story.can_be_viewed_by(other_user))
        self.assertTrue(private_story.can_be_viewed_by(self.user))


class StoryViewSetTest(APITestCase):
    """Tests para las vistas de Stories"""

    def setUp(self):
        """Configuración inicial para tests de API"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Obtener token JWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Crear algunas stories para tests
        self.story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Test story content'
        )

        self.other_story = Story.objects.create(
            author=self.other_user,
            story_type='text',
            content='Other user story'
        )

    def authenticate(self):
        """Autenticar cliente de test"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_text_story(self):
        """Test creación de story de texto"""
        self.authenticate()

        data = {
            'story_type': 'text',
            'content': 'Nueva story de texto',
            'background_color': '#FF5733',
            'text_color': '#FFFFFF'
        }

        response = self.client.post(reverse('story-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        story = Story.objects.get(id=response.data['id'])
        self.assertEqual(story.author, self.user)
        self.assertEqual(story.content, 'Nueva story de texto')
        self.assertEqual(story.background_color, '#FF5733')

    def test_story_feed(self):
        """Test feed de stories"""
        self.authenticate()

        response = self.client.get(reverse('story-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que es una lista
        self.assertIsInstance(response.data, list)

        # Si hay datos, verificar estructura
        if response.data:
            user_stories = response.data[0]
            self.assertIn('user', user_stories)
            self.assertIn('stories', user_stories)

    def test_like_story(self):
        """Test dar like a una story"""
        self.authenticate()

        response = self.client.post(
            reverse('story-like', args=[self.other_story.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se creó el like
        self.assertTrue(
            StoryLike.objects.filter(
                story=self.other_story,
                user=self.user
            ).exists()
        )

        # Verificar que se actualizó el contador
        self.other_story.refresh_from_db()
        self.assertEqual(self.other_story.likes_count, 1)

    def test_unlike_story(self):
        """Test quitar like a una story"""
        self.authenticate()

        # Crear like primero
        StoryLike.objects.create(story=self.other_story, user=self.user)
        self.other_story.likes_count = 1
        self.other_story.save()

        response = self.client.post(
            reverse('story-unlike', args=[self.other_story.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se eliminó el like
        self.assertFalse(
            StoryLike.objects.filter(
                story=self.other_story,
                user=self.user
            ).exists()
        )

        # Verificar que se actualizó el contador
        self.other_story.refresh_from_db()
        self.assertEqual(self.other_story.likes_count, 0)

    def test_reply_to_story(self):
        """Test responder a una story"""
        self.authenticate()

        data = {'content': 'Esta es mi respuesta a tu story'}
        response = self.client.post(
            reverse('story-reply', args=[self.other_story.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se creó la respuesta
        reply = StoryReply.objects.get(id=response.data['id'])
        self.assertEqual(reply.story, self.other_story)
        self.assertEqual(reply.sender, self.user)
        self.assertEqual(reply.content, 'Esta es mi respuesta a tu story')

    def test_view_story(self):
        """Test marcar story como vista"""
        self.authenticate()

        data = {'view_duration': 5}
        response = self.client.post(
            reverse('story-view', args=[self.other_story.id]),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se registró la visualización
        self.assertTrue(
            StoryView.objects.filter(
                story=self.other_story,
                viewer=self.user
            ).exists()
        )

        # Verificar que se actualizó el contador
        self.other_story.refresh_from_db()
        self.assertEqual(self.other_story.views_count, 1)

    def test_story_stats(self):
        """Test estadísticas de una story"""
        self.authenticate()

        # Crear algunas interacciones
        StoryView.objects.create(story=self.story, viewer=self.other_user)
        StoryLike.objects.create(story=self.story, user=self.other_user)

        # Actualizar contadores manualmente (normalmente se haría con signals)
        self.story.views_count = 1
        self.story.likes_count = 1
        self.story.save()

        response = self.client.get(
            reverse('story-stats', args=[self.story.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        stats = response.data
        self.assertEqual(stats['views_count'], 1)
        self.assertEqual(stats['likes_count'], 1)
        self.assertEqual(stats['replies_count'], 0)

    def test_unauthorized_access(self):
        """Test acceso sin autenticación"""
        response = self.client.get(reverse('story-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StoryHighlightTest(APITestCase):
    """Tests para highlights de stories"""

    def setUp(self):
        """Configuración inicial para tests de highlights"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Crear algunas stories
        self.story1 = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Story 1'
        )
        self.story2 = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Story 2'
        )

    def authenticate(self):
        """Autenticar cliente de test"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_highlight(self):
        """Test creación de highlight"""
        self.authenticate()

        data = {
            'title': 'Mi highlight',
            'story_ids': [str(self.story1.id), str(self.story2.id)]
        }

        response = self.client.post(reverse('storyhighlight-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        highlight = StoryHighlight.objects.get(id=response.data['id'])
        self.assertEqual(highlight.title, 'Mi highlight')
        self.assertEqual(highlight.stories_count, 2)

    def test_add_story_to_highlight(self):
        """Test agregar story a highlight existente"""
        self.authenticate()

        highlight = StoryHighlight.objects.create(
            user=self.user,
            title='Test highlight'
        )

        data = {'story_id': str(self.story1.id)}
        response = self.client.post(
            reverse('storyhighlight-add-story', args=[highlight.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se agregó la story
        self.assertTrue(
            StoryHighlightItem.objects.filter(
                highlight=highlight,
                story=self.story1
            ).exists()
        )


class StoryExpirationTest(TestCase):
    """Tests para funcionalidad de expiración"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_expired_story_cleanup(self):
        """Test limpieza de stories expiradas"""
        # Crear story expirada
        expired_story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Expired story',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        # Crear story activa
        active_story = Story.objects.create(
            author=self.user,
            story_type='text',
            content='Active story',
            expires_at=timezone.now() + timedelta(hours=23)
        )

        # Verificar que existen ambas
        self.assertEqual(Story.objects.count(), 2)

        # Simular comando de limpieza
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command('cleanup_expired_stories', '--force', stdout=out)

        # Verificar que solo queda la story activa
        self.assertEqual(Story.objects.count(), 1)
        self.assertTrue(Story.objects.filter(id=active_story.id).exists())
        self.assertFalse(Story.objects.filter(id=expired_story.id).exists())
