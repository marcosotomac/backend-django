from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'Sistema de Chat'

    def ready(self):
        """Importar señales cuando la app esté lista"""
        import chat.signals
