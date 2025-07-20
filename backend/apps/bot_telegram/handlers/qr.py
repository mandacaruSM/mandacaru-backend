from telegram import Update
from telegram.ext import ContextTypes
from backend.apps.bot_telegram.utils.qr_utils import ler_qr_code
from backend.apps.operadores.models import Operador
from asgiref.sync import sync_to_async

async def handle_qr_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 Envie a foto do QR Code para identificarmos o operador.")

async def handle_qr_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    caminho = await photo_file.download_to_drive()
    
    dados_qr = await sync_to_async(ler_qr_code)(caminho)
    if dados_qr and dados_qr.get("tipo") == "operador":
        codigo = dados_qr.get("codigo")
        operador = await sync_to_async(Operador.objects.filter(codigo=codigo).first)()
        if operador:
            operador.atualizar_ultimo_acesso(chat_id=update.effective_chat.id)
            await update.message.reply_text(f"✅ Operador {operador.nome} identificado com sucesso.")
            return
    await update.message.reply_text("❌ QR Code inválido ou operador não encontrado.")
