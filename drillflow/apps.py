from django.apps import AppConfig

class DrillflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drillflow'

    def ready(self):
        """
        Импортируем сигналы при запуске приложения
        """
        import drillflow.signals  # noqa 