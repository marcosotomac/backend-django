"""
Views adicionales para manejo de archivos y uploads
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image
import uuid
import io
from django.core.files.base import ContentFile
from utils import FileUploadHandler, compress_image
import json


class ImageUploadView(APIView):
    """
    Vista para subir imágenes de forma optimizada
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Sube una imagen y la optimiza automáticamente
        """
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response(
                    {'error': 'No se proporcionó ninguna imagen'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar el archivo
            is_valid, message = FileUploadHandler.validate_image_file(
                image_file)
            if not is_valid:
                return Response(
                    {'error': message},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Comprimir la imagen
            compressed_image = compress_image(image_file)

            # Generar nombre único
            file_extension = image_file.name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg']:
                file_extension = 'jpg'  # Forzar JPG después de la compresión

            unique_filename = f"{uuid.uuid4()}.{file_extension}"

            # Guardar en el almacenamiento
            file_path = f"temp-uploads/{request.user.username}/{unique_filename}"
            saved_path = default_storage.save(file_path, compressed_image)

            # Obtener URL
            file_url = FileUploadHandler.get_file_url(
                default_storage.open(saved_path))

            return Response({
                'success': True,
                'file_path': saved_path,
                'file_url': file_url,
                'file_size': compressed_image.size if hasattr(compressed_image, 'size') else FileUploadHandler.get_file_size(compressed_image),
                'message': 'Imagen subida y optimizada correctamente'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error al procesar la imagen: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request):
    """
    Elimina una imagen del almacenamiento
    """
    try:
        file_path = request.data.get('file_path')
        if not file_path:
            return Response(
                {'error': 'No se proporcionó la ruta del archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que el usuario tenga permisos para eliminar el archivo
        if not file_path.startswith(f"temp-uploads/{request.user.username}/") and \
           not file_path.startswith(f"avatars/{request.user.username}/") and \
           not file_path.startswith(f"posts/{request.user.username}/"):
            return Response(
                {'error': 'No tienes permisos para eliminar este archivo'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Eliminar el archivo
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            return Response({
                'success': True,
                'message': 'Archivo eliminado correctamente'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'El archivo no existe'},
                status=status.HTTP_404_NOT_FOUND
            )

    except Exception as e:
        return Response(
            {'error': f'Error al eliminar la imagen: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def storage_info(request):
    """
    Información sobre la configuración de almacenamiento
    """
    return Response({
        'storage_type': 'S3' if settings.USE_S3 else 'Local',
        'bucket_name': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None) if settings.USE_S3 else None,
        'region': getattr(settings, 'AWS_S3_REGION_NAME', None) if settings.USE_S3 else None,
        'custom_domain': getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None) if settings.USE_S3 else None,
        'max_file_size': '5MB',
        'allowed_formats': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'compression_enabled': True
    })


class BatchImageUploadView(APIView):
    """
    Vista para subir múltiples imágenes a la vez
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Sube múltiples imágenes optimizadas
        """
        try:
            images = request.FILES.getlist('images')
            if not images:
                return Response(
                    {'error': 'No se proporcionaron imágenes'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(images) > 10:  # Límite de 10 imágenes por batch
                return Response(
                    {'error': 'Máximo 10 imágenes por lote'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            uploaded_files = []
            errors = []

            for i, image_file in enumerate(images):
                try:
                    # Validar el archivo
                    is_valid, message = FileUploadHandler.validate_image_file(
                        image_file)
                    if not is_valid:
                        errors.append(f"Imagen {i+1}: {message}")
                        continue

                    # Comprimir la imagen
                    compressed_image = compress_image(image_file)

                    # Generar nombre único
                    file_extension = image_file.name.split('.')[-1].lower()
                    if file_extension not in ['jpg', 'jpeg']:
                        file_extension = 'jpg'

                    unique_filename = f"{uuid.uuid4()}.{file_extension}"
                    file_path = f"temp-uploads/{request.user.username}/{unique_filename}"

                    # Guardar
                    saved_path = default_storage.save(
                        file_path, compressed_image)
                    file_url = FileUploadHandler.get_file_url(
                        default_storage.open(saved_path))

                    uploaded_files.append({
                        'index': i,
                        'original_name': image_file.name,
                        'file_path': saved_path,
                        'file_url': file_url,
                        'file_size': compressed_image.size if hasattr(compressed_image, 'size') else 0
                    })

                except Exception as e:
                    errors.append(
                        f"Imagen {i+1}: Error al procesar - {str(e)}")

            return Response({
                'success': len(uploaded_files) > 0,
                'uploaded_files': uploaded_files,
                'errors': errors,
                'total_uploaded': len(uploaded_files),
                'total_errors': len(errors)
            }, status=status.HTTP_201_CREATED if uploaded_files else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': f'Error al procesar las imágenes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
