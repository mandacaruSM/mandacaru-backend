# backend/apps/nr12_checklist/urls.py

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
    # ENDPOINTS PARA BOT TELEGRAM
    # ================================================================
    
    # Login de operador via QR code
    path('bot/operador/login/', operador_login_qr, name='bot-operador-login'),
    
    # Acesso a equipamento via QR code
    path('bot/equipamento/<int:equipamento_id>/', EquipamentoAcessoBotView.as_view(), name='bot-equipamento-acesso'),
    
    # Atualização de itens de checklist via bot
    path('bot/item-checklist/atualizar/', atualizar_item_checklist, name='bot-atualizar-item'),
    
    # ================================================================
    # ENDPOINTS WEB (Visualização)
    # ================================================================
    
    # Acesso rápido via UUID (sem login) - para visualização web
    path('checklist/<uuid:checklist_uuid>/', checklist_por_uuid, name='checklist-uuid'),

    # Geração de PDF do checklist
    path('checklist/<int:pk>/pdf/', visualizar_checklist_html, name='checklist-nr12-pdf'),

    # ================================================================
    # APIs REST (Autenticadas)
    # ================================================================
    
    # APIs REST autenticadas
    path('', include(router.urls)),
]

# URL patterns disponíveis:
# /api/nr12/bot/operador/login/ - POST - Login do operador
# /api/nr12/bot/equipamento/{id}/ - GET/POST - Acesso ao equipamento
# /api/nr12/bot/item-checklist/atualizar/ - POST - Atualizar item
# /api/nr12/checklist/{uuid}/ - GET - Visualizar checklist por UUID
# /api/nr12/checklist/{id}/pdf/ - GET - Gerar PDF do checklist
# /api/nr12/tipos-equipamento/ - CRUD - Tipos de equipamento NR12
# /api/nr12/itens-padrao/ - CRUD - Itens padrão de checklist
# /api/nr12/checklists/ - CRUD - Checklists realizados
# /api/nr12/itens-checklist/ - CRUD - Itens de checklist
# /api/nr12/alertas/ - CRUD - Alertas de manutenção