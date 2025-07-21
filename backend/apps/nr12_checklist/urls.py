# ================================================================
# ARQUIVO ATUALIZADO: backend/apps/nr12_checklist/urls.py
# ================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    TipoEquipamentoNR12ViewSet,
    ItemChecklistPadraoViewSet,
    ChecklistNR12ViewSet,
    ItemChecklistRealizadoViewSet,
    AlertaManutencaoViewSet,
)
from .bot_views.bot_api import (
    checklist_por_uuid,
    visualizar_checklist_html,
)

# ✅ IMPORTAR NOVOS ENDPOINTS DO BOT
from .bot_views.bot_telegram import (
    operador_login_qr,
    EquipamentoAcessoBotView,
    atualizar_item_checklist
)

# Configura os routers das APIs REST
router = DefaultRouter()
router.register(r'tipos-equipamento', TipoEquipamentoNR12ViewSet, basename='tipos-equipamento-nr12')
router.register(r'itens-padrao', ItemChecklistPadraoViewSet, basename='itens-padrao')
router.register(r'checklists', ChecklistNR12ViewSet, basename='checklists-nr12')
router.register(r'itens-checklist', ItemChecklistRealizadoViewSet, basename='itens-checklist')
router.register(r'alertas', AlertaManutencaoViewSet, basename='alertas-manutencao')

urlpatterns = [
    # ================================================================
    # ENDPOINTS PARA BOT TELEGRAM (URLs Padronizadas)
    # ================================================================
    
    # Login de operador via QR code
    path('bot/operador/login/', operador_login_qr, name='bot-operador-login'),
    
    # Acesso a equipamento via QR code (URL que o QR aponta)
    path('bot/equipamento/<int:equipamento_id>/', EquipamentoAcessoBotView.as_view(), name='bot-equipamento-acesso'),
    
    # Atualização de itens de checklist via bot
    path('bot/item-checklist/atualizar/', atualizar_item_checklist, name='bot-atualizar-item'),
    
    # ================================================================
    # ENDPOINTS EXISTENTES (Mantidos)
    # ================================================================
    
    # Acesso rápido via UUID (sem login) - para visualização web
    path('checklist/<uuid:checklist_uuid>/', checklist_por_uuid, name='checklist-uuid'),

    # Geração de PDF do checklist
    path('checklist/<int:pk>/pdf/', visualizar_checklist_html, name='checklist-nr12-html'),

    # APIs REST autenticadas
    path('', include(router.urls)),
]