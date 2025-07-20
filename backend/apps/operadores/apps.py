from django.apps import AppConfig

class OperadoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.operadores'  # ✅ caminho real do app
    verbose_name = 'Operadores'
