import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import requests

# Setup
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE_URL = os.getenv("ERP_API_URL", "http://localhost:8000/api")

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# Estado da conversa
class ChecklistState(StatesGroup):
    AguardandoCodigo = State()
    EscolhendoEquipamento = State()
    RespondendoChecklist = State()

# Sessão simples
user_sessions = {}

# Comando /start
@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.set_state(ChecklistState.AguardandoCodigo)
    await message.answer("🔐 Envie seu <b>código de operador</b> para começar.")

# Autenticação
@dp.message(ChecklistState.AguardandoCodigo)
async def autenticar(message: Message, state: FSMContext):
    codigo = message.text.strip()
    resp = requests.get(f"{API_BASE_URL}/operadores/validar_codigo/?codigo={codigo}")
    if resp.status_code == 200:
        operador = resp.json()
        user_sessions[message.from_user.id] = {
            "operador": operador,
            "equipamento": None,
            "itens": [],
            "respostas": [],
            "indice": 0
        }
        await state.set_state(ChecklistState.EscolhendoEquipamento)
        await message.answer(f"✅ Autenticado como <b>{operador['nome']}</b>.\nAgora selecione o equipamento.")

        equipamentos = requests.get(f"{API_BASE_URL}/equipamentos/").json()
        kb = InlineKeyboardBuilder()
        for eq in equipamentos:
            kb.button(text=eq['nome'], callback_data=f"eq_{eq['id']}")
        await message.answer("🔧 Equipamentos disponíveis:", reply_markup=kb.as_markup())
    else:
        await message.answer("❌ Código inválido. Tente novamente.")

# Seleção de equipamento
@dp.callback_query(F.data.startswith("eq_"))
async def selecionar_equipamento(callback: CallbackQuery, state: FSMContext):
    eq_id = int(callback.data.replace("eq_", ""))
    session = user_sessions.get(callback.from_user.id)
    if not session:
        await callback.message.answer("⚠️ Sessão expirada. Envie /start novamente.")
        return

    session['equipamento'] = eq_id

    # Buscar checklist
    r = requests.get(f"{API_BASE_URL}/nr12_checklist/itens_padrao/?equipamento_id={eq_id}")
    itens = r.json()
    if not itens:
        await callback.message.answer("⚠️ Nenhum checklist encontrado.")
        return

    session['itens'] = itens
    session['respostas'] = []
    session['indice'] = 0

    await state.set_state(ChecklistState.RespondendoChecklist)
    await enviar_pergunta(callback.message, session)

# Enviar pergunta
async def enviar_pergunta(message: Message, session):
    i = session['indice']
    item = session['itens'][i]
    session['respostas'].append({
        "item_id": item['id'],
        "resposta": None,
        "observacao": ""
    })

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Sim", callback_data="resp_sim")
    kb.button(text="❌ Não", callback_data="resp_nao")
    kb.button(text="⚠️ N/A", callback_data="resp_na")
    await message.answer(f"{i+1}. {item['descricao']}", reply_markup=kb.as_markup())

# Processar resposta
@dp.callback_query(F.data.startswith("resp_"))
async def processar_resposta(callback: CallbackQuery, state: FSMContext):
    session = user_sessions.get(callback.from_user.id)
    if not session:
        await callback.message.answer("⚠️ Sessão expirada. Envie /start novamente.")
        return

    resposta = callback.data.replace("resp_", "")
    session['respostas'][session['indice']]["resposta"] = resposta
    session['indice'] += 1

    if session['indice'] < len(session['itens']):
        await enviar_pergunta(callback.message, session)
    else:
        await finalizar_checklist(callback.message, session)
        await state.clear()

# Enviar para API
async def finalizar_checklist(message: Message, session):
    payload = {
        "operador_id": session["operador"]["id"],
        "equipamento_id": session["equipamento"],
        "itens": session["respostas"]
    }
    r = requests.post(f"{API_BASE_URL}/nr12_checklist/finalizar_checklist/", json=payload)
    if r.status_code == 201:
        await message.answer("✅ Checklist finalizado com sucesso!")
    else:
        await message.answer("❌ Erro ao salvar checklist.")

# Fallback
@dp.message()
async def fallback(message: Message):
    await message.answer("📎 Use /start para iniciar o checklist.")

# Main
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
