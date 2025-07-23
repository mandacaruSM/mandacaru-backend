# backend/apps/bot_telegram/config.py
from django.conf import settings
import os

# Token do bot
BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN'))

# URLs
API_BASE_URL = getattr(settings, 'API_BASE_URL', 'http://127.0.0.1:8000/api')
BASE_URL = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')

# Configurações de sessão
SESSION_TIMEOUT_HOURS = getattr(settings, 'SESSION_TIMEOUT_HOURS', 24)

# IDs de administradores
ADMIN_IDS = getattr(settings, 'ADMIN_IDS', [])
