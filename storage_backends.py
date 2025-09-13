"""
Backends de almacenamiento personalizados para AWS S3
Compatible con AWS Academy (session tokens)
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class S3Storage(S3Boto3Storage):
    """Clase base para almacenamiento S3 con soporte para AWS Academy"""

    def __init__(self, **settings_dict):
        # Configurar session token si está disponible (AWS Academy)
        if hasattr(settings, 'AWS_SESSION_TOKEN') and settings.AWS_SESSION_TOKEN:
            settings_dict['session_token'] = settings.AWS_SESSION_TOKEN
        super().__init__(**settings_dict)


class StaticStorage(S3Storage):
    """
    Almacenamiento para archivos estáticos en S3
    """
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True


class PublicMediaStorage(S3Storage):
    """
    Almacenamiento para archivos media públicos en S3
    """
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Storage):
    """
    Almacenamiento para archivos media privados en S3
    """
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False  # No usar CDN para archivos privados
