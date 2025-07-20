#from django.apps import AppConfig
#class EquipamentosConfig(AppConfig):
#    name = 'backend.apps.equipamentos'
from django.apps import AppConfig

class EquipamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.equipamentos'

    def ready(self):
        import backend.apps.equipamentos.signals
