# backend/apps/operadores/urls_bot.py

from django.urls import path
from . import views_bot

urlpatterns = [
    path('operadores/<int:operador_id>/', views_bot.atualizar_operador, name='atualizar-operador-bot'),
]