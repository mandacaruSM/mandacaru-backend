# ================================================================
# ARQUIVO: backend/apps/nr12_checklist/urls.py
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

# Configura os routers das APIs REST
router = DefaultRouter()
router.register(r'tipos-equipamento', TipoEquipamentoNR12ViewSet, basename='tipos-equipamento-nr12')
router.register(r'itens-padrao', ItemChecklistPadraoViewSet, basename='itens-padrao')
router.register(r'checklists', ChecklistNR12ViewSet, basename='checklists-nr12')
router.register(r'itens-checklist', ItemChecklistRealizadoViewSet, basename='itens-checklist')
router.register(r'alertas', AlertaManutencaoViewSet, basename='alertas-manutencao')

urlpatterns = [
    # Acesso rápido via UUID (sem login)
    path('checklist/<uuid:checklist_uuid>/', checklist_por_uuid, name='checklist-uuid'),

    # Geração de PDF do checklist
    path('checklist/<int:pk>/pdf/', visualizar_checklist_html, name='checklist-nr12-html'),

    # APIs REST autenticadas
    path('', include(router.urls)),
]
