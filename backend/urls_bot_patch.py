# ===============================================
# PATCH PARA backend/urls.py
# ADICIONE ESTAS LINHAS AO SEU ARQUIVO backend/urls.py
# ===============================================

# Adicione estes imports no topo do arquivo backend/urls.py:
from backend.apps.nr12_checklist.views_bot import checklists_bot, equipamentos_operador
from backend.apps.equipamentos.views_bot import equipamentos_publicos, checklists_equipamento  
from backend.apps.operadores.views_bot import atualizar_operador

# Adicione estas URLs ao final de urlpatterns (antes das URLs de arquivos estáticos):
urlpatterns += [
    # ENDPOINTS PÚBLICOS PARA O BOT TELEGRAM
    path('api/checklists/', checklists_bot, name='checklists-bot'),
    path('api/nr12/checklists/', checklists_bot, name='nr12-checklists-bot'),
    path('api/equipamentos/', equipamentos_publicos, name='equipamentos-publicos'),
    path('api/operadores/<int:operador_id>/equipamentos/', equipamentos_operador, name='operador-equipamentos'),
    path('api/equipamentos/<int:equipamento_id>/checklists/', checklists_equipamento, name='equipamento-checklists'),
    path('api/operadores/<int:operador_id>/', atualizar_operador, name='atualizar-operador'),
]
