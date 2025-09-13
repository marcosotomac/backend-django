from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para el modelo User
    """
    list_display = [
        'username', 'email', 'full_name', 'is_verified',
        'is_private', 'followers_count', 'following_count',
        'posts_count', 'created_at', 'is_active'
    ]
    list_filter = [
        'is_active', 'is_verified', 'is_private', 'is_staff',
        'is_superuser', 'created_at'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'last_login',
        'date_joined', 'followers_count', 'following_count',
        'posts_count'
    ]

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'bio',
                'avatar', 'birth_date', 'location', 'website',
                'phone_number'
            )
        }),
        ('Configuración de Cuenta', {
            'fields': ('is_verified', 'is_private')
        }),
        ('Estadísticas', {
            'fields': (
                'followers_count', 'following_count', 'posts_count'
            ),
            'classes': ('collapse',)
        }),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nombre Completo'
