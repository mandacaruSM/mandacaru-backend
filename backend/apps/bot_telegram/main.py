# ================================================================
# ARQUIVO: backend/apps/bot_telegram/main.py
# Arquivo principal do bot atualizado com QR Reader
# ================================================================

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from .config import BOT_TOKEN
from .handlers import message, callback
from .handlers.qr import handle_qr_photo
from .commands import start, help as help_cmd, status, logout

logger = logging.getLogger(__name__)


def build_application():
    """Constrói a aplicação do bot com todos os handlers"""
    
    # Configurar logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Criar aplicação
    app = Application.builder().token(BOT_TOKEN).build()
    
    # ==========================================
    # COMANDOS
    # ==========================================
    app.add_handler(start.start_handler)
    app.add_handler(help_cmd.help_handler)
    app.add_handler(status.status_handler)
    app.add_handler(logout.logout_handler)
    
    # ==========================================
    # HANDLERS DE CONTEÚDO
    # ==========================================
    
    # QR Code (fotos) - PRIORIDADE ALTA
    app.add_handler(MessageHandler(filters.PHOTO, handle_qr_photo), group=0)
    
    # Mensagens de texto - PRIORIDADE NORMAL
    app.add_handler(message.text_handler, group=1)
    
    # Callbacks de botões inline
    app.add_handler(callback.callback_handler)
    
    # ==========================================
    # HANDLERS DE ERRO
    # ==========================================
    async def error_handler(update, context):
        """Log de erros"""
        logger.error(f"Erro no update {update}: {context.error}")
    
    app.add_error_handler(error_handler)
    
    logger.info("✅ Aplicação do bot configurada com sucesso!")
    return app


def run_polling():
    """Executa o bot em modo polling (desenvolvimento)"""
    app = build_application()
    logger.info("🤖 Bot Mandacaru ERP iniciado (polling)")
    logger.info("📷 Leitura de QR Code ativada!")
    app.run_polling(allowed_updates=["message", "callback_query"])


def run_webhook(webhook_url: str, port: int):
    """Executa o bot em modo webhook (produção)"""
    app = build_application()
    logger.info(f"🤖 Bot Mandacaru ERP iniciado (webhook @ {webhook_url}:{port})")
    logger.info("📷 Leitura de QR Code ativada!")
    
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=f"/{BOT_TOKEN}",
        webhook_url=f"{webhook_url}/{BOT_TOKEN}",
        allowed_updates=["message", "callback_query"]
    )