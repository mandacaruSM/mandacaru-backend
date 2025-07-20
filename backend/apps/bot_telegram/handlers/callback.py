### File: backend/apps/bot_telegram/handlers/callback.py
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
import logging
from backend.apps.bot_telegram.utils.sessions import get_session
from backend.apps.bot_telegram.handlers.qr import handle_qr_text

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa callbacks de botões inline"""
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    session = get_session(chat_id)
    if not session:
        await query.edit_message_text(
            "❌ Sessão expirada. Use /start para reiniciar."
        )
        return

    data = query.data
    logging.info(f"Callback recebido: {data}")

    # TODO: Roteamento de callbacks para as funções correspondentes
    await query.edit_message_text(
        "🔀 Callback recebido, lógica em desenvolvimento."
    )

# Handler para registrar no dispatcher
callback_handler = CallbackQueryHandler(handle_callback)