# backend/apps/bot_telegram/handlers/os_handler.py
# Fluxo para finalizar Ordem de Serviço via Telegram Bot

from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

from backend.apps.equipamentos.models import Equipamento
from backend.apps.ordens.models import OrdemServico
from backend.apps.operadores.models import Operador
from datetime import datetime


class OSHandler:
    def __init__(self, user_sessions):
        self.sessions = user_sessions

    async def iniciar_fluxo(self, update: Update, context: ContextTypes.DEFAULT_TYPE, equipamento: Equipamento):
        chat_id = update.effective_chat.id
        self.sessions[chat_id]["equipamento_id"] = equipamento.id
        self.sessions[chat_id]["estado"] = "os_aguardando_texto"

        os_aberta = await sync_to_async(self.get_os_aberta)(equipamento)
        if os_aberta:
            self.sessions[chat_id]["ordem_id"] = os_aberta.id
            await update.message.reply_text(
                f"🔧 OS em aberto localizada: {os_aberta.descricao}. Envie o que foi realizado no serviço."
            )
        else:
            await update.message.reply_text("⚠️ Nenhuma Ordem de Serviço em aberto encontrada para este equipamento.")
            self.sessions[chat_id]["estado"] = None

    def get_os_aberta(self, equipamento):
        return OrdemServico.objects.filter(equipamento=equipamento, finalizada=False).first()

    async def processar_mensagem(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        estado = self.sessions[chat_id].get("estado")

        if estado == "os_aguardando_texto":
            descricao = update.message.text
            self.sessions[chat_id]["descricao"] = descricao
            self.sessions[chat_id]["estado"] = "os_aguardando_foto"
            await update.message.reply_text("Agora envie uma foto do serviço finalizado ou equipamento.")

    async def processar_foto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        estado = self.sessions[chat_id].get("estado")

        if estado == "os_aguardando_foto":
            file = await update.message.photo[-1].get_file()
            photo_bytes = await file.download_as_bytearray()
            self.sessions[chat_id]["foto"] = photo_bytes

            await self.salvar_finalizacao(update)
            await update.message.reply_text("✅ Ordem de Serviço finalizada com sucesso.")
            self.sessions[chat_id]["estado"] = None

    async def salvar_finalizacao(self, update: Update):
        chat_id = update.message.chat_id
        sessao = self.sessions[chat_id]

        ordem_id = sessao["ordem_id"]
        operador_id = sessao["operador_id"]
        descricao = sessao["descricao"]
        foto_bytes = sessao.get("foto")

        ordem = await sync_to_async(OrdemServico.objects.get)(id=ordem_id)
        operador = await sync_to_async(Operador.objects.get)(id=operador_id)

        ordem.descricao_execucao = descricao
        ordem.tecnico_responsavel = operador
        ordem.data_execucao = datetime.now().date()
        ordem.finalizada = True

        if foto_bytes:
            nome_arquivo = f"os_{ordem.id}_final.jpg"
            from django.core.files.base import ContentFile
            ordem.anexo.save(nome_arquivo, ContentFile(foto_bytes), save=False)

        await sync_to_async(ordem.save)()
