from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from posts.models import Post, Hashtag, PostHashtag
import json

User = get_user_model()


class PostsAPITestCase(TestCase):
    """Test case para verificar la funcionalidad de Posts"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear segundo usuario para tests
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)
    
    def test_create_post(self):
        """Test creación de post"""
        data = {
            'content': 'Este es un post de prueba con #testing',
            'is_public': True,
            'allow_comments': True
        }
        
        response = self.client.post('/api/v1/posts/create/', data)
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el post se creó
        self.assertTrue(Post.objects.filter(content__contains='post de prueba').exists())
        
        # Verificar que se extrajo el hashtag
        self.assertTrue(Hashtag.objects.filter(name='testing').exists())
    
    def test_list_posts(self):
        """Test listar posts"""
        # Crear post de prueba
        Post.objects.create(
            author=self.user,
            content='Post público de prueba',
            is_public=True
        )
        
        response = self.client.get('/api/v1/posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_post_detail(self):
        """Test obtener detalle de post"""
        post = Post.objects.create(
            author=self.user,
            content='Post de detalle',
            is_public=True
        )
        
        response = self.client.get(f'/api/v1/posts/{post.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Post de detalle')
    
    def test_update_own_post(self):
        """Test actualizar post propio"""
        post = Post.objects.create(
            author=self.user,
            content='Post original',
            is_public=True
        )
        
        data = {
            'content': 'Post actualizado',
            'is_public': False
        }
        
        response = self.client.put(f'/api/v1/posts/{post.id}/update/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó
        post.refresh_from_db()
        self.assertEqual(post.content, 'Post actualizado')
        self.assertFalse(post.is_public)
    
    def test_delete_own_post(self):
        """Test eliminar post propio"""
        post = Post.objects.create(
            author=self.user,
            content='Post a eliminar',
            is_public=True
        )
        
        response = self.client.delete(f'/api/v1/posts/{post.id}/delete/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se eliminó
        self.assertFalse(Post.objects.filter(id=post.id).exists())
    
    def test_cannot_update_others_post(self):
        """Test que no se puede actualizar post de otro usuario"""
        post = Post.objects.create(
            author=self.user2,
            content='Post de otro usuario',
            is_public=True
        )
        
        data = {'content': 'Intento de hack'}
        
        response = self.client.put(f'/api/v1/posts/{post.id}/update/', data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_my_posts(self):
        """Test obtener mis posts"""
        # Crear posts del usuario
        Post.objects.create(
            author=self.user,
            content='Mi post 1',
            is_public=True
        )
        Post.objects.create(
            author=self.user,
            content='Mi post 2',
            is_public=False
        )
        
        # Crear post de otro usuario
        Post.objects.create(
            author=self.user2,
            content='Post de otro',
            is_public=True
        )
        
        response = self.client.get('/api/v1/posts/my-posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_user_posts(self):
        """Test obtener posts de usuario específico"""
        # Crear posts del usuario2
        Post.objects.create(
            author=self.user2,
            content='Post público de user2',
            is_public=True
        )
        Post.objects.create(
            author=self.user2,
            content='Post privado de user2',
            is_public=False
        )
        
        response = self.client.get('/api/v1/posts/user/testuser2/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe mostrar post público
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Post público de user2')
    
    def test_hashtag_posts(self):
        """Test obtener posts por hashtag"""
        # Crear posts con hashtag
        post1 = Post.objects.create(
            author=self.user,
            content='Post con #python',
            is_public=True
        )
        post2 = Post.objects.create(
            author=self.user2,
            content='Otro post con #python y #django',
            is_public=True
        )
        
        # Los hashtags se crean automáticamente al guardar el post
        # Obtener el hashtag creado automáticamente
        hashtag = Hashtag.objects.get(name='python')
        
        response = self.client.get('/api/v1/posts/hashtag/python/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_trending_hashtags(self):
        """Test obtener hashtags en tendencia"""
        # Crear hashtags con diferentes conteos
        Hashtag.objects.create(name='trending', posts_count=10)
        Hashtag.objects.create(name='popular', posts_count=5)
        Hashtag.objects.create(name='new', posts_count=1)
        
        response = self.client.get('/api/v1/posts/hashtags/trending/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # Verificar orden por posts_count
        if len(response.data['results']) > 1:
            first_count = response.data['results'][0]['posts_count']
            second_count = response.data['results'][1]['posts_count']
            self.assertGreaterEqual(first_count, second_count)
    
    def test_post_stats(self):
        """Test obtener estadísticas de post"""
        post = Post.objects.create(
            author=self.user,
            content='Post con stats',
            is_public=True,
            likes_count=5,
            comments_count=3
        )
        
        response = self.client.get(f'/api/v1/posts/{post.id}/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 5)
        self.assertEqual(response.data['comments_count'], 3)
    
    def test_feed_view(self):
        """Test feed personalizado"""
        # Crear post del usuario
        Post.objects.create(
            author=self.user,
            content='Mi post en feed',
            is_public=True
        )
        
        response = self.client.get('/api/v1/posts/feed/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe mostrar al menos el post del usuario
        self.assertGreater(len(response.data['results']), 0)