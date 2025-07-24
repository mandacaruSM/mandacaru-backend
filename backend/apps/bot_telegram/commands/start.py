from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    try:
        user_name = update.effective_user.first_name or "Usuário"
        
        await update.message.reply_text(
            f"👋 **Bem-vindo ao Mandacaru ERP, {user_name}!**\n\n"
            f"🤖 **Sou o assistente virtual que vai ajudá-lo com:**\n"
            f"• ✅ Checklists NR12\n"
            f"• ⛽ Registro de abastecimentos\n"
            f"• ⚠️ Reporte de anomalias\n"
            f"• 📊 Consulta de históricos\n\n"
            f"🔐 **Para começar:**\n"
            f"Digite seu código de operador (ex: `OP0001`)\n"
            f"Ou envie uma foto do QR Code do seu cartão.\n\n"
            f"❓ **Precisa de ajuda?** Digite `/help`",
            parse_mode='Markdown'
        )
        
        logger.info(f"Comando /start executado por {user_name} (ID: {update.effective_user.id})")
        
    except Exception as e:
        logger.error(f"Erro no comando /start: {e}")
        await update.message.reply_text(
            "❌ Erro ao inicializar.\n"
            "Tente novamente."
        )

start_handler = CommandHandler('start', start_command)