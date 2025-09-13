from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de usuarios
    """
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'password', 'password_confirm', 'birth_date', 'bio'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Los campos de contraseña no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuarios
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    'Credenciales inválidas. Verifica tu email y contraseña.'
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    'La cuenta está desactivada.'
                )
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Email y contraseña son requeridos.'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil de usuario
    """
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'avatar', 'avatar_url', 'birth_date',
            'age', 'location', 'website', 'phone_number', 'is_verified',
            'is_private', 'followers_count', 'following_count',
            'posts_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'is_verified', 'followers_count',
            'following_count', 'posts_count', 'created_at', 'updated_at'
        ]

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar perfil de usuario
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'bio', 'avatar', 'birth_date',
            'location', 'website', 'phone_number', 'is_private'
        ]


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para usuario (para referencias en otras apps)
    """
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'avatar_url', 'is_verified']

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar usuarios (versión simplificada)
    """
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'avatar_url', 'bio', 'is_verified', 'followers_count',
            'following_count', 'posts_count'
        ]

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Los campos de nueva contraseña no coinciden."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "La contraseña actual es incorrecta."
            )
        return value
