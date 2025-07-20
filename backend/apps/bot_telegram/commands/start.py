### File: backend/apps/bot_telegram/commands/start.py
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from backend.apps.bot_telegram.utils.sessions import init_session
from backend.apps.bot_telegram.utils.keyboards import main_menu_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    init_session(chat_id, {
        'step': 'menu_principal',
        'operador': None,
        'equipamento': None,
        'data': {}
    })

    welcome = (
        f"🤖 *Bem-vindo ao Bot Mandacaru ERP*\n\n"
        f"Olá, {user.first_name}!\n\n"
        "Use o menu abaixo para navegar pelas funções."
    )
    await update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=main_menu_keyboard()
    )

start_handler = CommandHandler('start', start)