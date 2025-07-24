from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import logging

logger = logging.getLogger(__name__)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    try:
        await update.message.reply_text(
            "❓ **AJUDA - MANDACARU ERP BOT**\n\n"
            "🔧 **Como usar:**\n"
            "1. Faça login com seu código (ex: `OP0001`)\n"
            "2. Use os botões do menu principal\n"
            "3. Digite códigos de equipamento diretamente\n"
            "4. Ou envie fotos de QR Codes\n\n"
            "📱 **Comandos disponíveis:**\n"
            "• `/start` - Iniciar/reiniciar bot\n"
            "• `/help` - Esta ajuda\n"
            "• `/status` - Ver seu status\n"
            "• `/logout` - Sair do sistema\n\n"
            "🔧 **Códigos aceitos:**\n"
            "• **Operador:** `OP0001`, `op0001`, `0001`\n"
            "• **Equipamento:** `EQ0001`, `eq0001`, `123`\n\n"
            "📷 **QR Codes:**\n"
            "• Envie foto do QR Code\n"
            "• Sistema tentará ler automaticamente\n"
            "• Se falhar, digite o código manualmente\n\n"
            "🆘 **Suporte:**\n"
            "Em caso de problemas, contate o suporte técnico.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro no comando /help: {e}")
        await update.message.reply_text("❓ Ajuda indisponível no momento.")

help_handler = CommandHandler('help', help_command)