# backend/apps/bot_telegram/handlers/photo.py
from telegram.ext import MessageHandler, filters, ContextTypes
from telegram import Update
from ..utils.sessions import get_session
from asgiref.sync import sync_to_async
from ...operadores.models import Operador

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Imagem recebida. Em breve a leitura de QR será processada.")

photo_handler = MessageHandler(filters.PHOTO, handle_photo)

