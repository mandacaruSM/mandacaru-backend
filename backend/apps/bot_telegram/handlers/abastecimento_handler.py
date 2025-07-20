# backend/apps/bot_telegram/handlers/abastecimento_handler.py
# Fluxo de registro de abastecimento via bot Telegram

from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

from backend.apps.equipamentos.models import Equipamento
from backend.apps.abastecimento.models import RegistroAbastecimento, TipoCombustivel
from backend.apps.operadores.models import Operador
from datetime import datetime


class AbastecimentoHandler:
    def __init__(self, user_sessions):
        self.sessions = user_sessions

    async def iniciar_fluxo(self, update: Update, context: ContextTypes.DEFAULT_TYPE, equipamento: Equipamento):
        chat_id = update.effective_chat.id
        self.sessions[chat_id]["equipamento_id"] = equipamento.id
        self.sessions[chat_id]["estado"] = "abastecimento_aguardando_quantidade"
        await update.message.reply_text(f"📆 {equipamento.nome} selecionado. Envie a quantidade abastecida em litros:")

    async def processar_mensagem(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        estado = self.sessions[chat_id].get("estado")

        if estado == "abastecimento_aguardando_quantidade":
            try:
                litros = float(update.message.text.replace(",", "."))
                self.sessions[chat_id]["quantidade"] = litros
                self.sessions[chat_id]["estado"] = "abastecimento_aguardando_tipo"

                tipos = await sync_to_async(list)(TipoCombustivel.objects.filter(ativo=True))
                botoes = [f"{tipo.nome}" for tipo in tipos]
                self.sessions[chat_id]["tipos_combustivel"] = {t.nome: t.id for t in tipos}

                botoes_texto = "\n".join(botoes)
                await update.message.reply_text(f"Escolha o tipo de combustível:\n{botoes_texto}")
            except:
                await update.message.reply_text("Valor inválido. Envie a quantidade abastecida em litros (ex: 25.5)")

        elif estado == "abastecimento_aguardando_tipo":
            tipo_nome = update.message.text.strip()
            tipo_id = self.sessions[chat_id].get("tipos_combustivel", {}).get(tipo_nome)
            if tipo_id:
                self.sessions[chat_id]["tipo_id"] = tipo_id
                self.sessions[chat_id]["estado"] = "abastecimento_aguardando_horimetro"
                await update.message.reply_text("Informe o horímetro atual do equipamento:")
            else:
                await update.message.reply_text("Tipo não reconhecido. Tente novamente.")

        elif estado == "abastecimento_aguardando_horimetro":
            try:
                horimetro = float(update.message.text.replace(",", "."))
                self.sessions[chat_id]["horimetro"] = horimetro
                await self.salvar_registro(update)
                self.sessions[chat_id]["estado"] = None
                await update.message.reply_text("✅ Abastecimento registrado com sucesso.")
            except:
                await update.message.reply_text("Horímetro inválido. Envie apenas número com ponto (ex: 1234.5)")

    async def salvar_registro(self, update: Update):
        chat_id = update.effective_chat.id
        sessao = self.sessions[chat_id]

        equipamento_id = sessao["equipamento_id"]
        operador_id = sessao.get("operador_id")
        quantidade = sessao["quantidade"]
        tipo_id = sessao["tipo_id"]
        horimetro = sessao["horimetro"]

        equipamento = await sync_to_async(Equipamento.objects.get)(id=equipamento_id)
        operador = await sync_to_async(Operador.objects.get)(id=operador_id)
        tipo = await sync_to_async(TipoCombustivel.objects.get)(id=tipo_id)

        await sync_to_async(RegistroAbastecimento.objects.create)(
            equipamento=equipamento,
            operador=operador,
            tipo_combustivel=tipo,
            quantidade=quantidade,
            horimetro=horimetro,
            data_abastecimento=datetime.now().date(),
            aprovado=False,
        )
