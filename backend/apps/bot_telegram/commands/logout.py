from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import logging

logger = logging.getLogger(__name__)

async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /logout"""
    try:
        from ..handlers.message import _memory_sessions
        
        chat_id = str(update.effective_chat.id)
        session = _memory_sessions.get(chat_id, {})
        
        if session.get('autenticado'):
            operador_nome = session.get('operador_nome', 'Usuário')
            
            # Limpar sessão
            _memory_sessions.pop(chat_id, None)
            
            await update.message.reply_text(
                f"👋 **Logout realizado com sucesso!**\n\n"
                f"Até logo, {operador_nome}!\n\n"
                f"Para usar novamente:\n"
                f"• Digite seu código de operador\n"
                f"• Ou envie foto do QR Code\n"
                f"• Ou use `/start` para reiniciar"
            )
            
            logger.info(f"Logout via comando: {operador_nome} (chat: {chat_id})")
        else:
            await update.message.reply_text(
                "❌ **Você não está autenticado.**\n\n"
                "Não há sessão ativa para encerrar.\n\n"
                "Para fazer login, digite seu código: `OP0001`"
            )
            
    except Exception as e:
        logger.error(f"Erro no comando /logout: {e}")
        await update.message.reply_text("❌ Erro ao fazer logout.")

logout_handler = CommandHandler('logout', logout_command)