from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Comandos disponíveis:\n"
        "/start - Iniciar conversa\n"
        "/help - Ajuda\n"
        "/status - Ver status do operador\n"
        "/logout - Finalizar sessão"
    )

help_handler = CommandHandler("help", help_callback)
