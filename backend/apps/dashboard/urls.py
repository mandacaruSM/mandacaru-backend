# backend/apps/dashboard/urls.py
# ================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_principal, name='principal'),
    
    # APIs para dados
    path('api/kpis/', views.kpis_api, name='kpis_api'),
    path('api/equipamentos/', views.equipamentos_resumo, name='equipamentos_api'),
    path('api/checklists/', views.checklist_resumo, name='checklists_api'),
]

