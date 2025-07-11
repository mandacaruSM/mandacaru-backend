 # 3. ATUALIZAR backend/apps/nr12_checklist/urls.py
# ================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tipos-equipamento', views.TipoEquipamentoNR12ViewSet, basename='tipos-equipamento-nr12')
router.register(r'itens-padrao', views.ItemChecklistPadraoViewSet, basename='itens-padrao')
router.register(r'checklists', views.ChecklistNR12ViewSet, basename='checklists-nr12')
router.register(r'itens-checklist', views.ItemChecklistRealizadoViewSet, basename='itens-checklist')
router.register(r'alertas', views.AlertaManutencaoViewSet, basename='alertas-manutencao')

urlpatterns = [
    # Acesso via QR Code (sem autenticação)
    path('checklist/<uuid:checklist_uuid>/', views.checklist_por_uuid, name='checklist-uuid'),
    
    # APIs REST
    path('', include(router.urls)),
]
