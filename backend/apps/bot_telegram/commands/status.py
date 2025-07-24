from telegram import Update
from telegram.ext import CommandHandler, ContextTypes  
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    try:
        from ..handlers.message import _memory_sessions
        
        chat_id = str(update.effective_chat.id)
        session = _memory_sessions.get(chat_id, {})
        
        if session.get('autenticado'):
            operador = session.get('operador')
            login_time = session.get('login_time')
            
            # Calcular tempo de sessão
            if login_time:
                session_time = datetime.now() - login_time
                session_minutes = int(session_time.total_seconds() / 60)
                tempo_sessao = f"{session_minutes} minutos"
            else:
                tempo_sessao = "Indeterminado"
            
            await update.message.reply_text(
                f"📊 **SEU STATUS**\n\n"
                f"✅ **Autenticado:** Sim\n"
                f"👤 **Operador:** {operador.nome}\n"
                f"🆔 **Código:** {operador.codigo}\n"
                f"💼 **Função:** {operador.funcao}\n"
                f"🏢 **Setor:** {operador.setor}\n"
                f"⏰ **Sessão ativa há:** {tempo_sessao}\n"
                f"📱 **Chat ID:** {chat_id}\n\n"
                f"🤖 **Bot:** Mandacaru ERP v2.0\n"
                f"📶 **Status:** Conectado",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"📊 **SEU STATUS**\n\n"
                f"❌ **Autenticado:** Não\n"
                f"📱 **Chat ID:** {chat_id}\n\n"
                f"💡 **Para fazer login:**\n"
                f"Digite seu código de operador (ex: `OP0001`)\n"
                f"Ou envie foto do QR Code do seu cartão.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Erro no comando /status: {e}")
        await update.message.reply_text("❌ Erro ao verificar status.")

status_handler = CommandHandler('status', status_command)