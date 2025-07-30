# ===============================================
# CORREÇÃO 2: backend/apps/nr12_checklist/urls_bot_corrigido.py
# ===============================================

from django.urls import path
from . import bot_checklists

app_name = 'nr12_bot'

urlpatterns = [
    # Endpoints públicos para o bot
    path('checklists/', 
         bot_checklists.checklists_bot_list, 
         name='checklists-bot-list'),
    
    path('checklists/criar/', 
         bot_checklists.criar_checklist_bot, 
         name='checklist-bot-criar'),
    
    path('operadores/<int:operador_id>/equipamentos/', 
         bot_checklists.equipamentos_operador_bot, 
         name='equipamentos-operador-bot'),
]

