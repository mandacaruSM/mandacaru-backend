# apps/ordens_servico/apps.py
from django.apps import AppConfig

class OrdensServicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.ordens_servico'

    def ready(self):
        import backend.apps.ordens_servico.signals
