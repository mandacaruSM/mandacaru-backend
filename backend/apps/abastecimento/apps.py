# ----------------------------------------------------------------
# 6. APPS.PY CORRIGIDO PARA CARREGAR SIGNALS
# backend/apps/abastecimento/apps.py
# ----------------------------------------------------------------

from django.apps import AppConfig

class AbastecimentoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.abastecimento'
    verbose_name = 'Abastecimento'
    
    def ready(self):
        # Importar signals quando o app estiver pronto
        import backend.apps.abastecimento.signals