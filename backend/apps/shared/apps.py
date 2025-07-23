# ================================================================
# ARQUIVO: backend/apps/shared/apps.py
# Configuração do app shared
# ================================================================

from django.apps import AppConfig

class SharedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.shared'
    verbose_name = 'Funcionalidades Compartilhadas'