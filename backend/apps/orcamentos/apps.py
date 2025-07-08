# apps/orcamentos/apps.py
from django.apps import AppConfig

class OrcamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.orcamentos'

    def ready(self):
        import backend.apps.orcamentos.signals