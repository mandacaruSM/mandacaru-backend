# backend/apps/orcamentos/apps.py
from django.apps import AppConfig

class OrcamentosConfig(AppConfig):
    name = 'backend.apps.orcamentos'

    def ready(self):
        import backend.apps.orcamentos.signals  # ativa signals
