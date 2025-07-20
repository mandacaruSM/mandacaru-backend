# backend/apps/bot_telegram/main.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from .config import BOT_TOKEN
from .handlers import message, photo, callback
from .commands import start, help as help_cmd, status, logout
from .handlers.qr import handle_qr_photo

def build_application():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    app = Application.builder().token(BOT_TOKEN).build()

    # Comandos com barra
    app.add_handler(start.start_handler)
    app.add_handler(help_cmd.help_handler)
    app.add_handler(status.status_handler)
    app.add_handler(logout.logout_handler)

    # Texto e foto
    app.add_handler(message.text_handler)
    app.add_handler(photo.photo_handler)
    app.add_handler(MessageHandler(filters.PHOTO, handle_qr_photo))

    # Callback inline
    app.add_handler(callback.callback_handler)

    return app

def run_polling():
    app = build_application()
    logging.getLogger(__name__).info("🤖 Bot Mandacaru ERP iniciado (polling)")
    app.run_polling()

def run_webhook(webhook_url: str, port: int):
    app = build_application()
    logging.getLogger(__name__).info(f"🤖 Bot Mandacaru ERP iniciado (webhook @ {webhook_url}:{port})")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=f"/{BOT_TOKEN}",
        webhook_url=f"{webhook_url}/{BOT_TOKEN}"
    )
