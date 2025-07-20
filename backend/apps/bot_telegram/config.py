### File: backend/apps/bot_telegram/config.py
import os
from django.conf import settings

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', settings.TELEGRAM_BOT_TOKEN)
ERP_BASE_URL = getattr(settings, 'ERP_BASE_URL', 'http://localhost:8000/api')
