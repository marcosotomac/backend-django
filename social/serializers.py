from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow, Like, Comment, Notification
from users.serializers import UserListSerializer

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Follow
    """
    follower = UserListSerializer(read_only=True)
    following = UserListSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer para comentarios
    """
    author = UserListSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'content', 'parent',
            'likes_count', 'replies_count', 'is_liked',
            'replies', 'created_at', 'updated_at', 'time_since_posted'
        ]
        read_only_fields = ['id', 'author',
                            'post', 'likes_count', 'replies_count']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                comment=obj,
                like_type='comment'
            ).exists()
        return False

    def get_replies(self, obj):
        if obj.parent is None:  # Solo mostrar respuestas en comentarios principales
            replies = obj.replies.all()[:3]  # Limitar a 3 respuestas iniciales
            return CommentSerializer(replies, many=True, context=self.context).data
        return []

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


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear comentarios
    """
    class Meta:
        model = Comment
        fields = ['content', 'parent']

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError(
                "El contenido no puede estar vacío.")
        return value

    def validate_parent(self, value):
        if value and value.post != self.context.get('post'):
            raise serializers.ValidationError(
                "El comentario padre debe pertenecer al mismo post."
            )
        return value


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer para likes
    """
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'like_type', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para notificaciones
    """
    sender = UserListSerializer(read_only=True)
    time_since_created = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'message',
            'post', 'comment', 'is_read', 'created_at', 'time_since_created'
        ]

    def get_time_since_created(self, obj):
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


class FollowerSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para seguidores
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['id', 'user', 'created_at']

    def get_user(self, obj):
        # Devolver el seguidor
        return UserListSerializer(obj.follower).data


class FollowingSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para seguidos
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['id', 'user', 'created_at']

    def get_user(self, obj):
        # Devolver el usuario seguido
        return UserListSerializer(obj.following).data
