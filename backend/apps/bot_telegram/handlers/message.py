# File: backend/apps/bot_telegram/handlers/message.py
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from backend.apps.bot_telegram.utils.sessions import get_session, init_session
from backend.apps.operadores.models import Operador
from asgiref.sync import sync_to_async


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()
    session = get_session(chat_id)

    # Se já estiver autenticado
    if session and session.get("operador_id"):
        await update.message.reply_text("✅ Você já está autenticado.")
        return

    # Tentar buscar operador por código
    operador = await sync_to_async(
        lambda: Operador.objects.filter(codigo__iexact=text, status="ATIVO", ativo_bot=True).first()
    )()

    if operador:
        operador.atualizar_ultimo_acesso(chat_id=chat_id)
        init_session(chat_id, {"operador_id": operador.id})
        await update.message.reply_text(f"✅ Olá {operador.nome}, acesso liberado.")
    else:
        await update.message.reply_text("❌ Código de operador inválido. Envie novamente.")


text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
