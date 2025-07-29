from django.urls import path
from . import views_bot

app_name = 'operadores_bot'

urlpatterns = [
    path('operador/login/', views_bot.operador_login_bot, name='operador_login_bot'),
    path('operador/<int:operador_id>/validar/', views_bot.validar_operador_bot, name='validar_operador_bot'),
    path('operadores/', views_bot.listar_operadores_bot, name='listar_operadores_bot'),
]
