# =============================
# bot_main/handlers.py (atualizado)
# =============================

from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from core.session import *
from core.db import buscar_operador_por_nome, validar_data_nascimento, registrar_chat_id

async def start_handler(message: Message):
    chat_id = str(message.chat.id)
    iniciar_sessao(chat_id)
    await message.answer("👤 Informe seu nome completo para buscar seu cadastro no sistema:")

async def nome_handler(message: Message):
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    if sessao.get("estado") != "AGUARDANDO_NOME":
        return
    nome = message.text.strip()
    operadores = await buscar_operador_por_nome(nome)

    if not operadores:
        await message.answer("❌ Nenhum operador encontrado com esse nome. Tente novamente.")
        return

    operador = operadores[0]  # pega o primeiro resultado encontrado
    atualizar_sessao(chat_id, "estado", "AGUARDANDO_DATA")
    atualizar_sessao(chat_id, "operador", operador)
    await message.answer(f"Confirme sua identidade. Digite sua data de nascimento (formato: DD/MM/AAAA) para validar o acesso.")

async def data_nascimento_handler(message: Message):
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    if sessao.get("estado") != "AGUARDANDO_DATA":
        return
    data_digitada = message.text.strip()

    operador = sessao.get("operador")
    if not operador:
        await message.answer("Erro interno. Envie /start para tentar novamente.")
        return

    try:
        dia, mes, ano = map(int, data_digitada.split("/"))
        data_formatada = f"{ano:04d}-{mes:02d}-{dia:02d}"
    except:
        await message.answer("❌ Data inválida. Use o formato: DD/MM/AAAA")
        return

    if await validar_data_nascimento(operador["id"], data_formatada):
        await registrar_chat_id(operador["id"], chat_id)
        limpar_sessao(chat_id)
        await message.answer(f"✅ Olá, {operador['nome']}! Seu acesso foi liberado. Use o menu abaixo para continuar.")
        # Aqui você pode chamar o menu principal
    else:
        await message.answer("❌ Data incorreta. Acesso negado.")
        limpar_sessao(chat_id)


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(nome_handler, F.text)
    dp.message.register(data_nascimento_handler, F.text)
