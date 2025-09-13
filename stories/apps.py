from django.apps import AppConfig


class StoriesConfig(AppConfig):
    """Configuración de la app Stories"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stories'
    verbose_name = 'Stories'

    def ready(self):
        """Importar señales cuando la app esté lista"""
        import stories.signals
