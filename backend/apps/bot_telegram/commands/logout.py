### File: backend/apps/bot_telegram/commands/logout.py
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from backend.apps.bot_telegram.utils.sessions import clear_session, get_session

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    session = get_session(chat_id)
    nome = session.get('operador', {}).get('nome', 'Usuário')
    clear_session(chat_id)
    await update.message.reply_text(
        f"👋 Logout realizado com sucesso! Até logo, {nome}! Use /start para recomeçar."
    )

logout_handler = CommandHandler('logout', logout)