# backend/apps/bot_telegram/handlers/nr12_handler.py
# Fluxo de checklist NR12 via Telegram Bot

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

from backend.apps.equipamentos.models import Equipamento
from backend.apps.operadores.models import Operador
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado, ItemChecklistPadrao, TipoEquipamentoNR12
from datetime import datetime


class NR12Handler:
    def __init__(self, user_sessions):
        self.sessions = user_sessions

    async def iniciar_checklist(self, update: Update, context: ContextTypes.DEFAULT_TYPE, equipamento: Equipamento):
        chat_id = update.effective_chat.id
        self.sessions[chat_id]["equipamento_id"] = equipamento.id
        self.sessions[chat_id]["estado"] = "checklist_em_andamento"

        tipo_nome = equipamento.tipo_checklist.nome if equipamento.tipo_checklist else None
        if not tipo_nome:
            await update.message.reply_text("⚠️ Este equipamento não tem um tipo de checklist associado.")
            return

        checklist_items = await sync_to_async(list)(
            ItemChecklistPadrao.objects.filter(tipo__nome=tipo_nome).order_by("ordem")
        )

        if not checklist_items:
            await update.message.reply_text("❌ Nenhum item de checklist configurado para esse tipo de equipamento.")
            return

        self.sessions[chat_id]["checklist_items"] = [(item.id, item.descricao) for item in checklist_items]
        self.sessions[chat_id]["checklist_respostas"] = {}
        await self.enviar_proximo_item(update)

    async def enviar_proximo_item(self, update: Update):
        chat_id = update.effective_chat.id
        respostas = self.sessions[chat_id].get("checklist_respostas", {})
        itens = self.sessions[chat_id]["checklist_items"]

        for item_id, descricao in itens:
            if item_id not in respostas:
                keyboard = [
                    [InlineKeyboardButton("✅ OK", callback_data=f"checklist_ok_{item_id}"),
                     InlineKeyboardButton("❌ N/C", callback_data=f"checklist_nc_{item_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(descricao, reply_markup=reply_markup)
                return

        await self.salvar_checklist(update)

    async def processar_resposta(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        data = query.data

        if not data.startswith("checklist_"):
            return

        partes = data.split("_")
        status = partes[1] == "ok"
        item_id = int(partes[2])

        self.sessions[chat_id]["checklist_respostas"][item_id] = status
        await self.enviar_proximo_item(query)

    async def salvar_checklist(self, update: Update):
        chat_id = update.effective_chat.id
        sessao = self.sessions[chat_id]

        equipamento = await sync_to_async(Equipamento.objects.get)(id=sessao["equipamento_id"])
        operador = await sync_to_async(Operador.objects.get)(id=sessao["operador_id"])
        respostas = sessao["checklist_respostas"]

        checklist = await sync_to_async(ChecklistNR12.objects.create)(
            equipamento=equipamento,
            operador=operador,
            data=datetime.now().date(),
            tipo=equipamento.tipo_checklist,
        )

        for item_id, status in respostas.items():
            item_padrao = await sync_to_async(ItemChecklistPadrao.objects.get)(id=item_id)
            await sync_to_async(ItemChecklistRealizado.objects.create)(
                checklist=checklist,
                item=item_padrao,
                status=status,
            )

        await update.message.reply_text("📊 Checklist finalizado e salvo com sucesso.")
        sessao["estado"] = None
