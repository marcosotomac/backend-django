from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, PostImage, Hashtag, PostHashtag
import re

User = get_user_model()


class PostImageSerializer(serializers.ModelSerializer):
    """
    Serializer para las imágenes de posts
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'order']

    def get_image_url(self, obj):
        return obj.get_image_url()


class HashtagSerializer(serializers.ModelSerializer):
    """
    Serializer para hashtags
    """
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'posts_count']


class PostAuthorSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para el autor de un post
    """
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'full_name', 'avatar_url', 'is_verified'
        ]

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear posts
    """
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
        max_length=5  # Máximo 5 imágenes por post
    )

    class Meta:
        model = Post
        fields = [
            'content', 'image', 'images', 'is_public', 'allow_comments'
        ]

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError(
                "El contenido no puede estar vacío.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        request = self.context.get('request')

        # Crear el post
        post = Post.objects.create(
            author=request.user,
            **validated_data
        )

        # Procesar hashtags
        self._process_hashtags(post)

        # Crear imágenes adicionales
        for i, image_data in enumerate(images_data):
            PostImage.objects.create(
                post=post,
                image=image_data,
                order=i + 1
            )

        # Actualizar contador de posts del usuario
        request.user.posts_count += 1
        request.user.save()

        return post

    def _process_hashtags(self, post):
        """
        Extraer y procesar hashtags del contenido
        """
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, post.content.lower())

        for hashtag_name in set(hashtags):  # Usar set para evitar duplicados
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            PostHashtag.objects.get_or_create(post=post, hashtag=hashtag)

            # Actualizar contador de posts del hashtag
            hashtag.posts_count = hashtag.posts.count()
            hashtag.save()


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer completo para posts
    """
    author = PostAuthorSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    hashtags = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image', 'image_url', 'images',
            'hashtags', 'likes_count', 'comments_count', 'shares_count',
            'is_public', 'allow_comments', 'is_liked', 'created_at',
            'updated_at', 'time_since_posted'
        ]

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_hashtags(self, obj):
        hashtags = Hashtag.objects.filter(posts__post=obj)
        return HashtagSerializer(hashtags, many=True).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Verificar si el usuario actual ha dado like al post
            from social.models import Like
            return Like.objects.filter(
                user=request.user,
                post=obj,
                like_type='post'
            ).exists()
        return False

    def get_time_since_posted(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 0:
            return f"hace {diff.days} días"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} horas"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minutos"
        else:
            return "hace unos segundos"


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar posts
    """
    class Meta:
        model = Post
        fields = ['content', 'is_public', 'allow_comments']

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError(
                "El contenido no puede estar vacío.")
        return value

    def update(self, instance, validated_data):
        # Actualizar hashtags si el contenido cambió
        old_content = instance.content
        instance = super().update(instance, validated_data)

        if 'content' in validated_data and old_content != instance.content:
            # Eliminar hashtags anteriores
            PostHashtag.objects.filter(post=instance).delete()
            # Procesar nuevos hashtags
            self._process_hashtags(instance)

        return instance

    def _process_hashtags(self, post):
        """
        Extraer y procesar hashtags del contenido
        """
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, post.content.lower())

        for hashtag_name in set(hashtags):
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            PostHashtag.objects.get_or_create(post=post, hashtag=hashtag)

            # Actualizar contador de posts del hashtag
            hashtag.posts_count = hashtag.posthashtag_set.count()
            hashtag.save()


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar posts
    """
    author = PostAuthorSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image_url', 'likes_count',
            'comments_count', 'is_liked', 'created_at', 'time_since_posted'
        ]

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from social.models import Like
            return Like.objects.filter(
                user=request.user,
                post=obj,
                like_type='post'
            ).exists()
        return False

    def get_time_since_posted(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 0:
            return f"hace {diff.days} días"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} horas"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minutos"
        else:
            return "hace unos segundos"
