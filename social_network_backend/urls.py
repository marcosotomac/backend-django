"""
URL configuration for social_network_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from upload_views import ImageUploadView, BatchImageUploadView, delete_image, storage_info

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Social Network API",
        default_version='v1',
        description="API completa para red social desarrollada con Django REST Framework",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@socialnetwork.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),

    # API Endpoints
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/social/', include('social.urls')),
    path('api/v1/', include('chat.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('stories.urls')),

    # Upload Endpoints
    path('api/v1/upload/image/', ImageUploadView.as_view(), name='upload-image'),
    path('api/v1/upload/batch/', BatchImageUploadView.as_view(), name='upload-batch'),
    path('api/v1/upload/delete/', delete_image, name='delete-image'),
    path('api/v1/upload/info/', storage_info, name='storage-info'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
