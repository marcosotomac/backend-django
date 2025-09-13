"""
Tests básicos para la API de la red social
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserAuthenticationTest(APITestCase):
    """
    Tests para autenticación de usuarios
    """

    def setUp(self):
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }

    def test_user_registration(self):
        """Test de registro de usuario"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_user_login(self):
        """Test de login de usuario"""
        # Primero crear un usuario
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)


class PostAPITest(APITestCase):
    """
    Tests para la API de posts
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.post_create_url = reverse('posts:post_create')
        self.post_list_url = reverse('posts:post_list')

    def test_create_post(self):
        """Test de creación de post"""
        post_data = {
            'content': 'Este es un post de prueba #test',
            'is_public': True,
            'allow_comments': True
        }

        response = self.client.post(self.post_create_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('post', response.data)

    def test_list_posts(self):
        """Test de listado de posts"""
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SocialAPITest(APITestCase):
    """
    Tests para funcionalidades sociales
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user1)

    def test_follow_user(self):
        """Test de seguimiento de usuario"""
        follow_url = reverse('social:follow_user',
                             kwargs={'username': 'user2'})
        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['following'])

    def test_unfollow_user(self):
        """Test de dejar de seguir usuario"""
        # Primero seguir al usuario
        follow_url = reverse('social:follow_user',
                             kwargs={'username': 'user2'})
        self.client.post(follow_url)

        # Luego dejar de seguir
        unfollow_url = reverse('social:unfollow_user',
                               kwargs={'username': 'user2'})
        response = self.client.post(unfollow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['following'])


class UserModelTest(TestCase):
    """
    Tests para el modelo de usuario
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_user_creation(self):
        """Test de creación de usuario"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_full_name(self):
        """Test de nombre completo"""
        self.assertEqual(self.user.full_name, 'Test User')

    def test_user_str(self):
        """Test de representación string"""
        expected = 'Test User (@testuser)'
        self.assertEqual(str(self.user), expected)
