# backend/apps/bot_telegram/urls.py
from django.urls import path
from . import views

app_name = 'bot_telegram'

urlpatterns = [
    # Endpoint que o QR Code chama (usando UUID do checklist)
    path('qr/<uuid:uuid_checklist>/', views.qr_code_endpoint, name='qr_code'),
    
    # Endpoint para receber dados do bot
    path('api/checklist/submit/', views.ChecklistSubmitView.as_view(), name='checklist_submit'),
    
    # Endpoint para listar checklists
    path('api/checklist/', views.checklist_list, name='checklist_list'),
    
    # Endpoint para detalhes de um checklist
    path('api/checklist/<uuid:uuid_checklist>/', views.checklist_detail, name='checklist_detail'),
]