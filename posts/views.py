from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Post, Hashtag, PostHashtag
from .serializers import (
    PostCreateSerializer, PostSerializer, PostUpdateSerializer,
    PostListSerializer, HashtagSerializer
)

User = get_user_model()


class PostCreateView(generics.CreateAPIView):
    """
    Vista para crear un nuevo post
    """
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response({
            'message': 'Post creado exitosamente',
            'post': PostSerializer(post, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener un post específico
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar posts públicos o del usuario actual
        user = self.request.user
        return queryset.filter(
            Q(is_public=True) | Q(author=user)
        )


class PostUpdateView(generics.UpdateAPIView):
    """
    Vista para actualizar un post
    """
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo permitir actualizar posts propios
        return super().get_queryset().filter(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response({
            'message': 'Post actualizado exitosamente',
            'post': PostSerializer(post, context={'request': request}).data
        })


class PostDeleteView(generics.DestroyAPIView):
    """
    Vista para eliminar un post
    """
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo permitir eliminar posts propios
        return super().get_queryset().filter(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Actualizar contador de posts del usuario
        request.user.posts_count -= 1
        request.user.save()

        self.perform_destroy(instance)

        return Response({
            'message': 'Post eliminado exitosamente'
        }, status=status.HTTP_200_OK)


class PostListView(generics.ListAPIView):
    """
    Vista para listar posts con paginación y filtros
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['content', 'author__username',
                     'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'likes_count', 'comments_count']
    ordering = ['-created_at']

    def get_queryset(self):
        # Mostrar posts públicos
        return Post.objects.filter(is_public=True).select_related('author')


class UserPostsView(generics.ListAPIView):
    """
    Vista para listar posts de un usuario específico
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)

        # Si es el propio usuario, mostrar todos sus posts
        if self.request.user == user:
            return Post.objects.filter(author=user).order_by('-created_at')

        # Si es otro usuario, solo mostrar posts públicos
        return Post.objects.filter(
            author=user,
            is_public=True
        ).order_by('-created_at')


class FeedView(generics.ListAPIView):
    """
    Vista para el feed personalizado del usuario
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Obtener IDs de usuarios que sigue
        from social.models import Follow
        following_users = Follow.objects.filter(
            follower=user
        ).values_list('following', flat=True)

        # Posts de usuarios que sigue + sus propios posts
        queryset = Post.objects.filter(
            Q(author__in=following_users) | Q(author=user),
            is_public=True
        ).select_related('author').order_by('-created_at')

        return queryset


class HashtagPostsView(generics.ListAPIView):
    """
    Vista para posts de un hashtag específico
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        hashtag_name = self.kwargs.get('hashtag_name')
        hashtag = get_object_or_404(Hashtag, name=hashtag_name.lower())

        return Post.objects.filter(
            posthashtag__hashtag=hashtag,
            is_public=True
        ).select_related('author').order_by('-created_at')


class TrendingHashtagsView(generics.ListAPIView):
    """
    Vista para hashtags en tendencia
    """
    queryset = Hashtag.objects.filter(
        posts_count__gt=0).order_by('-posts_count')[:20]
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_posts_view(request):
    """
    Vista para obtener todos los posts del usuario actual
    """
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    serializer = PostListSerializer(
        posts, many=True, context={'request': request})

    return Response({
        'posts': serializer.data,
        'count': posts.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def post_stats_view(request, pk):
    """
    Vista para obtener estadísticas detalladas de un post
    """
    post = get_object_or_404(Post, pk=pk)

    # Verificar permisos
    if not post.is_public and post.author != request.user:
        return Response({
            'error': 'No tienes permisos para ver este post'
        }, status=status.HTTP_403_FORBIDDEN)

    return Response({
        'likes_count': post.likes_count,
        'comments_count': post.comments_count,
        'shares_count': post.shares_count,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
    })
