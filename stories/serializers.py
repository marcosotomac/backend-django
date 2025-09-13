"""
Serializers para el sistema de Stories
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Story, StoryView, StoryLike, StoryReply,
    StoryHighlight, StoryHighlightItem
)
from users.serializers import UserListSerializer

User = get_user_model()


class StoryAuthorSerializer(serializers.ModelSerializer):
    """Serializer para el autor de una story"""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url']

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class StoryViewSerializer(serializers.ModelSerializer):
    """Serializer para visualizaciones de stories"""
    viewer = UserListSerializer(read_only=True)

    class Meta:
        model = StoryView
        fields = ['id', 'viewer', 'viewed_at', 'view_duration']


class StoryLikeSerializer(serializers.ModelSerializer):
    """Serializer para likes de stories"""
    user = UserListSerializer(read_only=True)

    class Meta:
        model = StoryLike
        fields = ['id', 'user', 'created_at']


class StoryReplySerializer(serializers.ModelSerializer):
    """Serializer para respuestas a stories"""
    sender = UserListSerializer(read_only=True)

    class Meta:
        model = StoryReply
        fields = ['id', 'sender', 'content', 'created_at', 'is_read']


class StoryCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear stories"""

    class Meta:
        model = Story
        fields = [
            'story_type', 'content', 'media_file', 'thumbnail',
            'is_public', 'allow_replies', 'background_color',
            'text_color', 'duration_hours', 'music_track'
        ]

    def validate(self, data):
        story_type = data.get('story_type')
        content = data.get('content')
        media_file = data.get('media_file')

        if story_type == 'text' and not content:
            raise serializers.ValidationError(
                "Las stories de texto requieren contenido."
            )

        if story_type in ['image', 'video'] and not media_file:
            raise serializers.ValidationError(
                f"Las stories de {story_type} requieren un archivo multimedia."
            )

        return data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class StorySerializer(serializers.ModelSerializer):
    """Serializer completo para stories"""
    author = StoryAuthorSerializer(read_only=True)
    media_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    can_view = serializers.SerializerMethodField()
    viewers_preview = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            'id', 'author', 'story_type', 'content', 'media_url',
            'thumbnail_url', 'is_public', 'allow_replies',
            'background_color', 'text_color', 'duration_hours', 'music_track',
            'views_count', 'likes_count', 'replies_count',
            'created_at', 'expires_at', 'is_liked', 'is_viewed',
            'time_remaining', 'can_view', 'viewers_preview'
        ]

    def get_media_url(self, obj):
        return obj.media_url

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoryLike.objects.filter(
                story=obj,
                user=request.user
            ).exists()
        return False

    def get_is_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoryView.objects.filter(
                story=obj,
                viewer=request.user
            ).exists()
        return False

    def get_time_remaining(self, obj):
        """Tiempo restante en segundos"""
        remaining = obj.time_remaining
        return int(remaining.total_seconds()) if remaining else 0

    def get_can_view(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_view(request.user)
        return False

    def get_viewers_preview(self, obj):
        """Primeros 3 usuarios que vieron la story"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.author == request.user:
            recent_views = StoryView.objects.filter(
                story=obj).select_related('viewer')[:3]
            return UserListSerializer([view.viewer for view in recent_views], many=True).data
        return []


class StoryListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar stories"""
    author = StoryAuthorSerializer(read_only=True)
    media_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            'id', 'author', 'story_type', 'media_url', 'thumbnail_url',
            'views_count', 'created_at', 'expires_at', 'is_viewed'
        ]

    def get_media_url(self, obj):
        return obj.media_url

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url

    def get_is_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoryView.objects.filter(
                story=obj,
                viewer=request.user
            ).exists()
        return False


class UserStoriesSerializer(serializers.Serializer):
    """Serializer para stories agrupadas por usuario"""
    user = StoryAuthorSerializer(read_only=True)
    stories = StoryListSerializer(many=True, read_only=True)
    unviewed_count = serializers.IntegerField(read_only=True)
    latest_story_time = serializers.DateTimeField(read_only=True)


class StoryHighlightItemSerializer(serializers.ModelSerializer):
    """Serializer para items de highlights"""
    story = StoryListSerializer(read_only=True)

    class Meta:
        model = StoryHighlightItem
        fields = ['id', 'story', 'order', 'added_at']


class StoryHighlightSerializer(serializers.ModelSerializer):
    """Serializer para highlights de stories"""
    user = StoryAuthorSerializer(read_only=True)
    cover_url = serializers.SerializerMethodField()
    stories_count = serializers.SerializerMethodField()
    highlight_items = StoryHighlightItemSerializer(many=True, read_only=True)

    class Meta:
        model = StoryHighlight
        fields = [
            'id', 'user', 'title', 'cover_url', 'is_public',
            'stories_count', 'created_at', 'updated_at', 'highlight_items'
        ]

    def get_cover_url(self, obj):
        return obj.cover_url

    def get_stories_count(self, obj):
        return obj.stories_count


class StoryHighlightCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear highlights"""
    story_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = StoryHighlight
        fields = ['title', 'cover_image', 'is_public', 'story_ids']

    def create(self, validated_data):
        story_ids = validated_data.pop('story_ids', [])
        validated_data['user'] = self.context['request'].user

        highlight = super().create(validated_data)

        # Agregar stories al highlight
        if story_ids:
            user = self.context['request'].user
            stories = Story.objects.filter(
                id__in=story_ids,
                author=user  # Solo sus propias stories
            )

            for order, story in enumerate(stories):
                StoryHighlightItem.objects.create(
                    highlight=highlight,
                    story=story,
                    order=order
                )

        return highlight


class StoryStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de stories"""
    total_stories = serializers.IntegerField()
    active_stories = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_replies = serializers.IntegerField()
    highlights_count = serializers.IntegerField()
    average_views_per_story = serializers.FloatField()

    # Estadísticas por tipo
    image_stories = serializers.IntegerField()
    video_stories = serializers.IntegerField()
    text_stories = serializers.IntegerField()

    # Última actividad
    last_story_date = serializers.DateTimeField()
    most_viewed_story_views = serializers.IntegerField()


class StoryViewCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear visualizaciones"""

    class Meta:
        model = StoryView
        fields = ['view_duration']

    def create(self, validated_data):
        validated_data['story'] = self.context['story']
        validated_data['viewer'] = self.context['request'].user

        # Usar get_or_create para evitar duplicados
        view, created = StoryView.objects.get_or_create(
            story=validated_data['story'],
            viewer=validated_data['viewer'],
            defaults={'view_duration': validated_data.get('view_duration', 0)}
        )

        if not created:
            # Actualizar duración si ya existe
            view.view_duration = max(
                view.view_duration, validated_data.get('view_duration', 0))
            view.save()

        # Actualizar contador de vistas en la story
        story = validated_data['story']
        story.views_count = story.story_views.count()
        story.save(update_fields=['views_count'])

        return view


class StoryReplyCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear respuestas a stories"""

    class Meta:
        model = StoryReply
        fields = ['content']

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError(
                "El contenido no puede estar vacío.")
        return value

    def create(self, validated_data):
        validated_data['story'] = self.context['story']
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
