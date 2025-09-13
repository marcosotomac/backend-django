"""
Utilidades para manejo de archivos y almacenamiento
"""
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage


def user_avatar_path(instance, filename):
    """
    Genera la ruta para avatares de usuarios
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'avatars/{instance.username}/{filename}'


def post_image_path(instance, filename):
    """
    Genera la ruta para imágenes de posts
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'posts/{instance.author.username}/{filename}'


def post_multiple_images_path(instance, filename):
    """
    Genera la ruta para múltiples imágenes de posts
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'posts/{instance.post.author.username}/images/{filename}'


def story_media_path(instance, filename):
    """
    Genera la ruta para archivos de stories
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'stories/{instance.author.username}/{filename}'


class FileUploadHandler:
    """
    Manejador para subida de archivos que funciona tanto con S3 como local
    """

    @staticmethod
    def get_file_url(file_field):
        """
        Obtiene la URL completa del archivo
        """
        if not file_field:
            return None

        if settings.USE_S3:
            return file_field.url
        else:
            # Para desarrollo local
            return f"{settings.MEDIA_URL}{file_field.name}"

    @staticmethod
    def delete_file(file_field):
        """
        Elimina un archivo del almacenamiento
        """
        if file_field:
            try:
                default_storage.delete(file_field.name)
                return True
            except Exception as e:
                print(f"Error deleting file: {e}")
                return False
        return False

    @staticmethod
    def get_file_size(file_field):
        """
        Obtiene el tamaño del archivo en bytes
        """
        if file_field:
            try:
                return file_field.size
            except Exception:
                return 0
        return 0

    @staticmethod
    def validate_image_file(file):
        """
        Valida que el archivo sea una imagen válida
        """
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        max_size = 5 * 1024 * 1024  # 5MB

        # Verificar extensión
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            return False, f"Formato de archivo no válido. Use: {', '.join(valid_extensions)}"

        # Verificar tamaño
        if file.size > max_size:
            return False, "El archivo es demasiado grande. Máximo 5MB."

        return True, "Archivo válido"


# Configuración de compresión de imágenes (opcional)
IMAGE_QUALITY = 85
IMAGE_MAX_WIDTH = 1920
IMAGE_MAX_HEIGHT = 1080


def compress_image(image_field):
    """
    Comprime una imagen para optimizar el almacenamiento
    """
    try:
        from PIL import Image
        import io
        from django.core.files.base import ContentFile

        # Abrir la imagen
        img = Image.open(image_field)

        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Redimensionar si es muy grande
        if img.width > IMAGE_MAX_WIDTH or img.height > IMAGE_MAX_HEIGHT:
            img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT),
                          Image.Resampling.LANCZOS)

        # Guardar con compresión
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
        output.seek(0)

        # Crear nuevo archivo
        compressed_file = ContentFile(output.read())
        return compressed_file

    except Exception as e:
        print(f"Error compressing image: {e}")
        return image_field
