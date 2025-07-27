# backend/apps/nr12_checklist/urls_bot.py
# VERSÃO MÍNIMA PARA FUNCIONAR SEM ERROS

from django.urls import path, include
from backend.apps.nr12_checklist.bot_views import bot_api, bot_telegram

urlpatterns = [
    # ================================================================
    # ENDPOINTS BÁSICOS (SEM AS VIEWS QUEBRADAS)
    # ================================================================
    
    # Acesso rápido via QR Code UUID (visualização web)
    path('checklist/<uuid:checklist_uuid>/', 
         bot_api.checklist_por_uuid, 
         name='checklist-uuid'),

    # HTML de visualização do checklist
    path('checklist/<int:pk>/pdf/', 
         bot_api.visualizar_checklist_html, 
         name='checklist-nr12-html'),
    
    # ================================================================
    # ENDPOINTS PARA AUTENTICAÇÃO/LOGIN BOT
    # ================================================================
    
    # Login de operador via QR code
    path('bot/operador/login/', 
         bot_telegram.operador_login_qr, 
         name='bot-operador-login'),
    
    # Acesso a equipamento via QR code (telegram)
    path('bot/equipamento/<int:equipamento_id>/', 
         bot_telegram.EquipamentoAcessoBotView.as_view(), 
         name='bot-equipamento-acesso'),
    
    # Atualização de itens de checklist via bot
    path('bot/item-checklist/atualizar/', 
         bot_telegram.atualizar_item_checklist, 
         name='bot-atualizar-item'),
]

# ================================================================
# NOTA: AS VIEWS DE bot_qrcode_views FORAM TEMPORARIAMENTE REMOVIDAS
# PARA EVITAR ERROS DE IMPORTAÇÃO. ELAS SERÃO REATIVADAS DEPOIS.
# ================================================================