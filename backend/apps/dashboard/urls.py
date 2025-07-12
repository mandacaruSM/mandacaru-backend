# ================================================================
# ATUALIZAR backend/apps/dashboard/urls.py
# ================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_principal, name='principal'),
    path('completo/', views.dashboard_completo, name='completo'),
    
    # APIs para dados específicos
    path('api/kpis/', views.kpis_api, name='kpis_api'),
    path('api/equipamentos/', views.equipamentos_resumo, name='equipamentos_api'),
    path('api/checklists/', views.checklist_resumo, name='checklists_api'),
    path('api/financeiro/', views.financeiro_resumo, name='financeiro_api'),
    path('api/estoque/', views.estoque_resumo, name='estoque_api'),
    path('api/alertas/', views.alertas_dashboard, name='alertas_api'),
    
    # Ações
    path('api/recalcular-kpis/', views.recalcular_kpis, name='recalcular_kpis'),
    path('api/alertas/<int:alerta_id>/marcar-lido/', views.marcar_alerta_lido, name='marcar_alerta_lido'),
]