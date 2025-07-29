# backend/apps/nr12_checklist/urls_bot.py

from django.urls import path
from backend.apps.nr12_checklist.bot_views import bot_api, bot_telegram

urlpatterns = [
    # ================================================================
    # ENDPOINTS DO BOT - SEM O PREFIXO /bot/ (será adicionado no urls.py principal)
    # ================================================================
    
    # Login de operador via QR code
    path('operador/login/', 
         bot_telegram.operador_login_qr, 
         name='bot-operador-login'),
    
    # Acesso a equipamento via QR code
    path('equipamento/<int:equipamento_id>/', 
         bot_telegram.EquipamentoAcessoBotView.as_view(), 
         name='bot-equipamento-acesso'),
    
    # Atualização de itens de checklist via bot
    path('item-checklist/atualizar/', 
         bot_telegram.atualizar_item_checklist, 
         name='bot-atualizar-item'),
    
    # ================================================================
    # ENDPOINTS WEB (Visualização) - mantém o prefixo checklist/
    # ================================================================
    
    # Acesso rápido via UUID (sem login) - para visualização web
    path('checklist/<uuid:checklist_uuid>/', 
         bot_api.checklist_por_uuid, 
         name='checklist-uuid'),

    # HTML de visualização do checklist
    path('checklist/<int:pk>/pdf/', 
         bot_api.visualizar_checklist_html, 
         name='checklist-nr12-html'),
]