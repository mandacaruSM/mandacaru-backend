# =============================
# bot_equipamento/handlers.py (corrigido)
# =============================

"""
Módulo de equipamentos para o Bot Mandacaru
Handlers para gerenciamento de equipamentos via Telegram
"""

from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from core.middleware import require_auth
from core.session import atualizar_sessao, obter_sessao, SessionState
from core.db import buscar_equipamentos, obter_equipamento_por_id
from core.templates import MessageTemplates

@require_auth
async def equipamento_menu_handler(message: Message, operador=None):
    """Menu principal do módulo equipamento"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Buscar Equipamento"), KeyboardButton(text="📋 Meus Equipamentos")],
            [KeyboardButton(text="📊 Status Equipamentos"), KeyboardButton(text="🔧 Manutenções")],
            [KeyboardButton(text="🏠 Menu Principal")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"🏭 **Módulo Equipamentos**\n\n"
        f"Olá, {operador['nome']}!\n"
        f"Escolha uma das opções abaixo:",
        reply_markup=keyboard
    )
    
    # Atualiza estado da sessão
    await atualizar_sessao(str(message.chat.id), {"estado": SessionState.EQUIPAMENTO_ATIVO})

@require_auth
async def buscar_equipamento_handler(message: Message, operador=None):
    """Busca equipamentos disponíveis"""
    chat_id = str(message.chat.id)
    
    try:
        # Simular busca de equipamentos (integrar com API real)
        await message.answer(
            "🔍 **Equipamentos Disponíveis:**\n\n"
            "1. **Escavadeira CAT-320**\n"
            "   📍 Setor A - Operacional\n"
            "   🔧 Última manutenção: 15/07/2025\n\n"
            "2. **Caminhão Volvo FH540**\n"
            "   📍 Setor B - Em manutenção\n"
            "   ⚠️ Previsão retorno: 30/07/2025\n\n"
            "3. **Motoniveladora RG140**\n"
            "   📍 Setor C - Operacional\n"
            "   ✅ Checklist em dia\n\n"
            "💡 Em breve: integração completa com sistema de equipamentos"
        )
        
    except Exception as e:
        await message.answer(
            MessageTemplates.error_template(
                "Erro na Busca",
                "Não foi possível buscar equipamentos no momento."
            )
        )

@require_auth
async def meus_equipamentos_handler(message: Message, operador=None):
    """Lista equipamentos do operador"""
    await message.answer(
        f"📋 **Meus Equipamentos - {operador['nome']}**\n\n"
        "🚛 **Veículos Autorizados:**\n"
        "• Caminhão ABC-1234\n"
        "• Van XYZ-5678\n\n"
        "🏭 **Equipamentos Autorizados:**\n"
        "• Escavadeira EQ-001\n"
        "• Compressor AR-002\n\n"
        "📊 **Status:** Todos operacionais\n"
        "🔧 **Última verificação:** Hoje às 08:30"
    )

@require_auth
async def status_equipamentos_handler(message: Message, operador=None):
    """Mostra status geral dos equipamentos"""
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Operacionais", callback_data="status_operacional")],
            [InlineKeyboardButton(text="🟡 Em Manutenção", callback_data="status_manutencao")],
            [InlineKeyboardButton(text="🔴 Fora de Serviço", callback_data="status_inativo")],
            [InlineKeyboardButton(text="📊 Relatório Completo", callback_data="status_relatorio")]
        ]
    )
    
    await message.answer(
        "📊 **Status dos Equipamentos**\n\n"
        "Selecione a categoria para ver detalhes:",
        reply_markup=inline_keyboard
    )

@require_auth
async def manutencoes_handler(message: Message, operador=None):
    """Gerencia manutenções de equipamentos"""
    await message.answer(
        "🔧 **Manutenções Programadas**\n\n"
        "📅 **Próximas 7 dias:**\n"
        "• 28/07 - Escavadeira CAT-320 (Preventiva)\n"
        "• 30/07 - Caminhão Volvo (Revisão)\n"
        "• 02/08 - Compressor (Troca filtros)\n\n"
        "⚠️ **Pendentes:**\n"
        "• Motoniveladora - Vazamento hidráulico\n"
        "• Betoneira - Substituição correia\n\n"
        "📞 **Para agendar:** Entre em contato com manutenção"
    )

async def callback_status_handler(callback_query):
    """Processa callbacks de status de equipamentos"""
    await callback_query.answer()
    
    status_type = callback_query.data.split("_")[1]
    
    status_responses = {
        "operacional": "🟢 **Equipamentos Operacionais (12)**\n\n• Escavadeira CAT-320\n• Caminhão Volvo FH540\n• Motoniveladora RG140\n• Compressor Atlas\n• E mais 8 equipamentos...",
        "manutencao": "🟡 **Em Manutenção (3)**\n\n• Retroescavadeira JCB - Troca pneus\n• Betoneira Schwing - Revisão bomba\n• Guindaste Liebherr - Inspeção anual",
        "inativo": "🔴 **Fora de Serviço (2)**\n\n• Caminhão Mercedes - Aguardando peças\n• Perfuratriz Ingersoll - Reforma geral",
        "relatorio": "📊 **Relatório Completo**\n\n✅ Operacionais: 12 (75%)\n🟡 Manutenção: 3 (19%)\n🔴 Inativo: 2 (6%)\n\n📈 Disponibilidade: 94%\n⏱️ Tempo médio reparo: 2,5 dias"
    }
    
    response = status_responses.get(status_type, "Status não encontrado")
    await callback_query.message.edit_text(response)

async def voltar_menu_principal(message: Message):
    """Volta ao menu principal"""
    chat_id = str(message.chat.id)
    atualizar_sessao(chat_id, "estado", SessionState.AUTENTICADO)
    
    # Menu principal
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Checklist"), KeyboardButton(text="⛽ Abastecimento")],
            [KeyboardButton(text="🔧 Ordem de Serviço"), KeyboardButton(text="💰 Financeiro")],
            [KeyboardButton(text="🏭 Equipamentos"), KeyboardButton(text="❓ Ajuda")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"🏠 **Menu Principal**\n\n"
        f"Bem-vindo de volta!\n\n"
        f"Escolha uma das opções:",
        reply_markup=keyboard
    )

def register_handlers(dp: Dispatcher):
    """
    Registra todos os handlers do módulo equipamento
    
    Args:
        dp: Dispatcher do aiogram
    """
    
    # Menu principal do equipamento
    dp.message.register(
        equipamento_menu_handler,
        F.text == "🏭 Equipamentos"
    )
    
    # Handlers do submenu equipamento
    dp.message.register(
        buscar_equipamento_handler,
        F.text == "🔍 Buscar Equipamento"
    )
    
    dp.message.register(
        meus_equipamentos_handler,
        F.text == "📋 Meus Equipamentos"
    )
    
    dp.message.register(
        status_equipamentos_handler,
        F.text == "📊 Status Equipamentos"
    )
    
    dp.message.register(
        manutencoes_handler,
        F.text == "🔧 Manutenções"
    )
    
    dp.message.register(
        voltar_menu_principal,
        F.text == "🏠 Menu Principal"
    )
    
    # Callbacks
    dp.callback_query.register(
        callback_status_handler,
        F.data.startswith("status_")
    )

# =============================
# IMPORTANTE: ESTA É A FUNÇÃO QUE DEVE SER IMPORTADA
# Não existe 'router' neste arquivo, apenas 'register_handlers'
# =============================