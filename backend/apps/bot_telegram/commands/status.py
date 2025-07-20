### File: backend/apps/bot_telegram/commands/status.py
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from datetime import datetime
from backend.apps.bot_telegram.utils.sessions import get_session

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    session = get_session(chat_id)
    operador = session.get('operador')
    equipamento = session.get('equipamento')

    texto = "📊 *Status da Sessão*\n\n"
    if operador:
        texto += f"👤 Operador: {operador['nome']} ({operador['codigo']})\n"
    else:
        texto += "❌ Nenhum operador identificado\n"

    if equipamento:
        texto += f"🔧 Equipamento: {equipamento['nome']} (ID {equipamento['id']})\n"
    else:
        texto += "❌ Nenhum equipamento selecionado\n"

    texto += f"🕐 Última atividade: {datetime.now().strftime('%H:%M:%S')}"
    await update.message.reply_text(texto, parse_mode='Markdown')

status_handler = CommandHandler('status', status_command)