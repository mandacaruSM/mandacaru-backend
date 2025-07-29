from django.urls import path
from . import views_bot

app_name = 'equipamentos_bot'

urlpatterns = [
    path('equipamento/<int:equipamento_id>/', views_bot.equipamento_action_bot, name='equipamento_action_bot'),
]
