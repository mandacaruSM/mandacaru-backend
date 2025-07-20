# =============================
# bot_main/handlers.py (corrigido)
# =============================

from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from core.session import *
from core.db import buscar_operador_por_nome, validar_data_nascimento, registrar_chat_id

async def start_handler(message: Message):
    chat_id = str(message.chat.id)
    iniciar_sessao(chat_id)
    await message.answer("👋 Bem-vindo ao Bot Mandacaru!\n\n👤 Informe seu nome completo para buscar seu cadastro no sistema:")

async def nome_handler(message: Message):
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    
    # Verifica se está no estado correto
    if sessao.get("estado") != "AGUARDANDO_NOME":
        return
    
    nome = message.text.strip()
    
    # Validação básica do nome
    if len(nome) < 3:
        await message.answer("❌ Nome muito curto. Digite seu nome completo:")
        return
    
    try:
        operadores = await buscar_operador_por_nome(nome)
        
        if not operadores:
            await message.answer("❌ Nenhum operador encontrado com esse nome.\n\nTente novamente ou verifique se digitou corretamente:")
            return

        operador = operadores[0]  # pega o primeiro resultado encontrado
        atualizar_sessao(chat_id, "estado", "AGUARDANDO_DATA")
        atualizar_sessao(chat_id, "operador", operador)
        
        await message.answer(
            f"👤 Operador encontrado: {operador['nome']}\n\n"
            f"🔐 Para confirmar sua identidade, digite sua data de nascimento no formato DD/MM/AAAA:"
        )
        
    except Exception as e:
        await message.answer("❌ Erro ao buscar operador. Tente novamente em alguns instantes.")
        print(f"Erro ao buscar operador: {e}")

async def data_nascimento_handler(message: Message):
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    
    if sessao.get("estado") != "AGUARDANDO_DATA":
        return
    
    data_digitada = message.text.strip()
    operador = sessao.get("operador")
    
    if not operador:
        await message.answer("❌ Erro interno. Envie /start para tentar novamente.")
        limpar_sessao(chat_id)
        return

    # Validação do formato da data
    try:
        dia, mes, ano = map(int, data_digitada.split("/"))
        if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= ano <= 2024):
            raise ValueError("Data fora do intervalo válido")
        data_formatada = f"{ano:04d}-{mes:02d}-{dia:02d}"
    except:
        await message.answer("❌ Data inválida. Use o formato DD/MM/AAAA (exemplo: 15/03/1990):")
        return

    try:
        if await validar_data_nascimento(operador["id"], data_formatada):
            await registrar_chat_id(operador["id"], chat_id)
            limpar_sessao(chat_id)
            
            # Menu principal
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📋 Checklist"), KeyboardButton(text="⛽ Abastecimento")],
                    [KeyboardButton(text="🔧 Ordem de Serviço"), KeyboardButton(text="💰 Financeiro")],
                    [KeyboardButton(text="📱 QR Code"), KeyboardButton(text="❓ Ajuda")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )
            
            await message.answer(
                f"✅ Acesso liberado!\n\n"
                f"Olá, {operador['nome']}! 👋\n\n"
                f"Escolha uma das opções do menu abaixo:",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                "❌ Data de nascimento incorreta.\n\n"
                "Acesso negado. Envie /start para tentar novamente."
            )
            limpar_sessao(chat_id)
            
    except Exception as e:
        await message.answer("❌ Erro ao validar dados. Tente novamente.")
        print(f"Erro na validação: {e}")

async def menu_handler(message: Message):
    """Handler para as opções do menu principal"""
    text = message.text
    
    if text == "📋 Checklist":
        await message.answer("📋 Módulo Checklist em desenvolvimento...")
    elif text == "⛽ Abastecimento":
        await message.answer("⛽ Módulo Abastecimento em desenvolvimento...")
    elif text == "🔧 Ordem de Serviço":
        await message.answer("🔧 Módulo OS em desenvolvimento...")
    elif text == "💰 Financeiro":
        await message.answer("💰 Módulo Financeiro em desenvolvimento...")
    elif text == "📱 QR Code":
        await message.answer("📱 Módulo QR Code em desenvolvimento...")
    elif text == "❓ Ajuda":
        await message.answer(
            "❓ **Ajuda - Bot Mandacaru**\n\n"
            "Este bot permite acesso aos módulos:\n"
            "• 📋 Checklist - Verificações diárias\n"
            "• ⛽ Abastecimento - Controle de combustível\n"
            "• 🔧 Ordem de Serviço - Solicitações de manutenção\n"
            "• 💰 Financeiro - Consultas financeiras\n"
            "• 📱 QR Code - Geração de códigos\n\n"
            "Para suporte, entre em contato com a equipe técnica."
        )

def register_handlers(dp: Dispatcher):
    # Comando /start
    dp.message.register(start_handler, Command("start"))
    
    # Handler para nome (apenas quando está aguardando nome)
    dp.message.register(
        nome_handler, 
        F.text & ~F.text.startswith('/') & 
        lambda message: obter_sessao(str(message.chat.id)).get("estado") == "AGUARDANDO_NOME"
    )
    
    # Handler para data (apenas quando está aguardando data)
    dp.message.register(
        data_nascimento_handler,
        F.text & ~F.text.startswith('/') &
        lambda message: obter_sessao(str(message.chat.id)).get("estado") == "AGUARDANDO_DATA"
    )
    
    # Handler para menu principal
    dp.message.register(
        menu_handler,
        F.text.in_([
            "📋 Checklist", "⛽ Abastecimento", "🔧 Ordem de Serviço",
            "💰 Financeiro", "📱 QR Code", "❓ Ajuda"
        ])
    )