# ===============================================
# backend/apps/operadores/urls_bot.py
# URLs específicas para Bot Telegram
# ===============================================

from django.urls import path
from . import views_bot

urlpatterns = [
    path('por-chat-id/', views_bot.operador_por_chat_id, name='operador-por-chat-id'),
    path('busca/', views_bot.operadores_busca, name='operadores-busca'),
    path('validar-login/', views_bot.validar_operador_login, name='validar-operador-login'),
    path('<int:operador_id>/', views_bot.atualizar_operador, name='atualizar-operador'),
]