# ===============================================
# backend/apps/nr12_checklist/urls.py - COM VIEWS_BOT
# ===============================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    TipoEquipamentoNR12ViewSet,
    ItemChecklistPadraoViewSet,
    ChecklistNR12ViewSet,
    ItemChecklistRealizadoViewSet,
    AlertaManutencaoViewSet,
    ChecklistsAbertosPorChatView
)

# Tentar importar views_bot
try:
    from .views_bot import (
        checklists_bot,
        equipamentos_operador
    )
    BOT_VIEWS_AVAILABLE = True
except ImportError:
    BOT_VIEWS_AVAILABLE = False

# Configura os routers das APIs REST
router = DefaultRouter()
router.register(r'tipos-equipamento', TipoEquipamentoNR12ViewSet, basename='tipos-equipamento-nr12')
router.register(r'itens-padrao', ItemChecklistPadraoViewSet, basename='itens-padrao')
router.register(r'checklists', ChecklistNR12ViewSet, basename='checklists-nr12')
router.register(r'itens-checklist', ItemChecklistRealizadoViewSet, basename='itens-checklist')
router.register(r'alertas', AlertaManutencaoViewSet, basename='alertas-manutencao')

urlpatterns = [
    # APIs REST principais
    path('', include(router.urls)),
]

# Adicionar URLs do bot se views_bot existir
if BOT_VIEWS_AVAILABLE:
    urlpatterns += [
        # Endpoints específicos para o bot
        path('checklists/', checklists_bot, name='nr12-checklists-bot'),
        path('operadores/<int:operador_id>/equipamentos/', equipamentos_operador, name='nr12-equipamentos-operador'),
        path('checklists/abertos/', ChecklistsAbertosPorChatView.as_view(), name='checklists-abertos'),
    ]

# ================================================================
# ENDPOINTS DISPONÍVEIS:
# ================================================================
# 
# ViewSets (sempre disponíveis):
# GET  /api/nr12/checklists/                     - Lista checklists (autenticado)
# POST /api/nr12/checklists/                     - Cria checklist (autenticado)
# GET  /api/nr12/checklists/{id}/                - Detalha checklist (autenticado)
# POST /api/nr12/checklists/{id}/iniciar/        - Inicia checklist (autenticado)
# POST /api/nr12/checklists/{id}/finalizar/      - Finaliza checklist (autenticado)
# GET  /api/nr12/checklists/{id}/itens/          - Lista itens do checklist (autenticado)
# 
# Bot Views (se disponíveis):
# GET  /api/nr12/checklists/                     - Lista checklists para bot (público)
# GET  /api/nr12/operadores/{id}/equipamentos/   - Equipamentos do operador (público)