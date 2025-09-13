"""
Comando de gestión para limpiar stories expiradas
"""
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from stories.models import Story


class Command(BaseCommand):
    """Comando para limpiar stories expiradas y sus archivos asociados"""
    help = 'Elimina las stories expiradas y sus archivos asociados del sistema'

    def add_arguments(self, parser):
        """Argumentos del comando"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se eliminaría sin hacer cambios reales',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la eliminación sin confirmación',
        )

    def handle(self, *args, **options):
        """Ejecuta la limpieza de stories expiradas"""
        now = timezone.now()

        # Buscar stories expiradas
        expired_stories = Story.objects.filter(expires_at__lt=now)
        expired_count = expired_stories.count()

        if expired_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No hay stories expiradas para eliminar.')
            )
            return

        self.stdout.write(
            f'Se encontraron {expired_count} stories expiradas.'
        )

        # Modo dry-run
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    'MODO DRY-RUN: No se realizarán cambios reales.')
            )
            for story in expired_stories[:10]:  # Mostrar solo los primeros 10
                self.stdout.write(
                    f'  - Story {story.id} de {story.author.username} '
                    f'(expiró: {story.expires_at})'
                )
            if expired_count > 10:
                self.stdout.write(f'  ... y {expired_count - 10} más.')
            return

        # Confirmación para eliminación real
        if not options['force']:
            confirm = input(
                f'¿Estás seguro de que quieres eliminar {expired_count} '
                f'stories expiradas? (sí/no): '
            )
            if confirm.lower() not in ['sí', 'si', 'yes', 'y']:
                self.stdout.write(
                    self.style.ERROR('Operación cancelada.')
                )
                return

        # Recopilar archivos para eliminar
        files_to_delete = []
        for story in expired_stories:
            if story.media_file:
                files_to_delete.append(story.media_file.path)
            if story.thumbnail:
                files_to_delete.append(story.thumbnail.path)

        # Eliminar stories de la base de datos
        deleted_count, deleted_objects = expired_stories.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Se eliminaron {deleted_count} stories de la base de datos.'
            )
        )

        # Eliminar archivos del sistema de archivos
        files_deleted = 0
        files_not_found = 0

        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    files_deleted += 1
                else:
                    files_not_found += 1
            except OSError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error al eliminar archivo {file_path}: {e}'
                    )
                )

        # Reportar resultados
        self.stdout.write(
            self.style.SUCCESS(
                f'Limpieza completada:\n'
                f'  - Stories eliminadas: {deleted_count}\n'
                f'  - Archivos eliminados: {files_deleted}\n'
                f'  - Archivos no encontrados: {files_not_found}'
            )
        )

        # Limpiar directorios vacíos
        self._clean_empty_directories()

    def _clean_empty_directories(self):
        """Limpia directorios vacíos en el directorio de stories"""
        try:
            stories_dir = os.path.join(settings.MEDIA_ROOT, 'stories')
            if not os.path.exists(stories_dir):
                return

            empty_dirs = []
            for root, dirs, files in os.walk(stories_dir, topdown=False):
                if not dirs and not files:
                    empty_dirs.append(root)

            for directory in empty_dirs:
                try:
                    os.rmdir(directory)
                    self.stdout.write(
                        f'Directorio vacío eliminado: {directory}'
                    )
                except OSError:
                    pass  # El directorio no estaba vacío o no se pudo eliminar

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f'No se pudieron limpiar directorios vacíos: {e}'
                )
            )
