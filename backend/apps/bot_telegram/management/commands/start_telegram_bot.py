from django.core.management.base import BaseCommand
from django.conf import settings
from asgiref.sync import sync_to_async

import logging
import re
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import httpx

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

from backend.apps.equipamentos.models import Equipamento
from backend.apps.operadores.models import Operador

logger = logging.getLogger(__name__)


class TelegramBotManager:
    def __init__(self):
        self.user_sessions = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        operador = await sync_to_async(self.get_operador_by_telegram)(user.id)

        if operador:
            self.user_sessions[chat_id] = {"operador_id": operador.id, "estado": None}
            await update.message.reply_text(
                f"👷 Olá {operador.nome}, bem-vindo ao Bot Mandacaru!",
                reply_markup=self.teclado_lateral()
            )
            await self.menu_principal(update, context)
        else:
            await update.message.reply_text("🔒 Você não está autorizado. Envie /registrar e informe seu código de operador.")
            self.user_sessions[chat_id] = {"estado": "aguardando_codigo"}

    async def registrar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.user_sessions[chat_id] = {"estado": "aguardando_codigo"}
        await update.message.reply_text("🔐 Informe o código de operador fornecido pela empresa:")

    async def processar_codigo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        estado = self.user_sessions.get(chat_id, {}).get("estado")

        if estado == "aguardando_codigo":
            codigo_digitado = update.message.text.strip()
            operador_qs = await sync_to_async(Operador.objects.filter)(codigo=codigo_digitado)

            if await sync_to_async(operador_qs.exists)():
                operador = await sync_to_async(operador_qs.first)()
                operador.chat_id_telegram = update.effective_user.id
                operador.status = True
                await sync_to_async(operador.save)()

                self.user_sessions[chat_id] = {"operador_id": operador.id, "estado": None}
                await update.message.reply_text(
                    f"✅ Código validado. Bem-vindo, {operador.nome}!",
                    reply_markup=self.teclado_lateral()
                )
                await self.menu_principal(update, context)
            else:
                await update.message.reply_text("❌ Código inválido. Tente novamente ou peça outro ao supervisor.")

    def get_operador_by_telegram(self, telegram_id):
        try:
            return Operador.objects.get(chat_id_telegram=telegram_id)
        except Operador.DoesNotExist:
            return None

    async def menu_principal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("✅ Checklist NR12", callback_data='menu_checklist')],
            [InlineKeyboardButton("📄 Relatório", callback_data='menu_relatorio')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Escolha uma opção:", reply_markup=reply_markup)

    def teclado_lateral(self):
        return ReplyKeyboardMarkup([
            ["✅ Checklist NR12", "📄 Relatório"]
        ], resize_keyboard=True)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        data = query.data

        if data == 'menu_checklist':
            await query.edit_message_text("📷 Envie a foto do QR Code do equipamento para iniciar o checklist.")
            self.user_sessions[chat_id]['estado'] = 'aguardando_qrcode_checklist'

        elif data == 'menu_relatorio':
            await query.edit_message_text("📷 Envie a foto do QR Code do equipamento para obter o relatório.")
            self.user_sessions[chat_id]['estado'] = 'aguardando_qrcode_relatorio'

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        estado = self.user_sessions.get(chat_id, {}).get('estado')

        if estado and estado.startswith('aguardando_qrcode'):
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            equipamento_id = self.ler_qrcode_real(photo_bytes)

            if equipamento_id:
                if estado == 'aguardando_qrcode_checklist':
                    await self.iniciar_checklist(update, equipamento_id)
                elif estado == 'aguardando_qrcode_relatorio':
                    await update.message.reply_text("🔧 Relatório ainda não implementado.")
                self.user_sessions[chat_id]['estado'] = None
            else:
                await update.message.reply_text("❌ Não foi possível ler o QR Code.")

    async def iniciar_checklist(self, update, equipamento_id):
        try:
            # 1. Buscar checklist do equipamento via API
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://127.0.0.1:8000/api/nr12/bot/equipamento/{equipamento_id}/")
                if resp.status_code != 200:
                    await update.message.reply_text("❌ Equipamento ou checklist não encontrado.")
                    return

                dados = resp.json()
                checklist = dados.get("checklist")
                if not checklist:
                    await update.message.reply_text("⚠️ Nenhum checklist encontrado para hoje.")
                    return

                checklist_id = checklist["id"]
                equipamento_nome = dados["equipamento"]["nome"]

                # 2. Iniciar checklist
                iniciar_resp = await client.post(f"http://127.0.0.1:8000/api/nr12/checklists/{checklist_id}/iniciar/")
                if iniciar_resp.status_code == 200:
                    await update.message.reply_text(f"✅ Checklist iniciado para {equipamento_nome}")
                else:
                    await update.message.reply_text("❌ Falha ao iniciar o checklist.")
                    return

                # 3. Buscar e exibir itens
                itens_resp = await client.get(f"http://127.0.0.1:8000/api/nr12/checklists/{checklist_id}/itens/")
                if itens_resp.status_code == 200:
                    itens = itens_resp.json()
                    texto = "📝 Itens do checklist:"
                    for item in itens:
                        texto += f"🔹 {item['item_padrao']['item']} - {item['status']}"
                    await update.message.reply_text(texto)
                else:
                    await update.message.reply_text("❌ Erro ao carregar os itens do checklist.")
        except Exception as e:
            await update.message.reply_text(f"Erro: {str(e)}")

    def ler_qrcode_real(self, photo_bytes):
        try:
            image = Image.open(BytesIO(photo_bytes)).convert('RGB')
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            decoded_objects = decode(opencv_image)

            for obj in decoded_objects:
                texto = obj.data.decode('utf-8').strip().lower()
                logger.info(f"QR Code detectado: {texto}")

                match = re.search(r'start=(?:eq|equip)?(\d+)', texto)
                if match:
                    return int(match.group(1))

                match = re.search(r'(?:eq|equip(?:amento)?)?(\d+)', texto)
                if match:
                    return int(match.group(1))

                if texto.isdigit():
                    return int(texto)

            return None
        except Exception as e:
            logger.error(f"Erro ao ler QR Code: {str(e)}")
            return None


class Command(BaseCommand):
    help = "Inicia o bot Telegram Mandacaru com checklist real via QR Code"

    def handle(self, *args, **options):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        app = Application.builder().token(bot_token).build()

        manager = TelegramBotManager()
        app.add_handler(CommandHandler("start", manager.start))
        app.add_handler(CommandHandler("registrar", manager.registrar))
        app.add_handler(CallbackQueryHandler(manager.handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), manager.processar_codigo))
        app.add_handler(MessageHandler(filters.PHOTO, manager.handle_photo))

        self.stdout.write("🚀 Bot Mandacaru com checklist e QR Code iniciado.")
        app.run_polling()
