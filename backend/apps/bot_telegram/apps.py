# backend/apps/bot_telegram/apps.py
from django.apps import AppConfig

class BotTelegramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.bot_telegram'
    verbose_name = 'Bot Telegram'