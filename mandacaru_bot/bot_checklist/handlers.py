# ===============================================
# ARQUIVO ATUALIZADO: mandacaru_bot/bot_checklist/handlers.py
# Integração completa com API NR12 real
# ===============================================

import logging
from datetime import datetime, date
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Imports do core
from core.session import (
    obter_operador_sessao, verificar_autenticacao,
    obter_equipamento_atual, definir_dados_temporarios,
    obter_dados_temporarios, definir_equipamento_atual
)
from core.db import (
    # Funções NR12 reais
    buscar_checklists_nr12, criar_checklist_nr12,
    buscar_itens_checklist_nr12, atualizar_item_checklist_nr12,
    finalizar_checklist_nr12, buscar_equipamentos_com_nr12,
    verificar_checklist_equipamento_hoje, buscar_checklists_operador_hoje,
    buscar_itens_padrao_nr12,
    # Funções gerais
    listar_equipamentos
)
from core.templates import MessageTemplates
from core.middleware import require_auth
from core.utils import Formatters

logger = logging.getLogger(__name__)

# ===============================================
# ESTADOS FSM PARA CHECKLIST
# ===============================================

class ChecklistStates(StatesGroup):
    aguardando_equipamento = State()
    executando_checklist = State()
    aguardando_observacao = State()
    aguardando_confirmacao = State()

# ===============================================
# HANDLERS PRINCIPAIS
# ===============================================

@require_auth
async def checklist_menu_handler(message: Message, operador: dict):
    """Menu principal do módulo checklist"""
    try:
        # Verificar se há equipamento selecionado
        chat_id = str(message.chat.id)
        equipamento_atual = await obter_equipamento_atual(chat_id)
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="🔗 Acessar Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="✅ Checklist do Dia", callback_data="checklist_hoje")],
            [InlineKeyboardButton(text="📊 Relatórios", callback_data="checklist_relatorios")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        equipamento_info = ""
        if equipamento_atual:
            equipamento_info = f"\n🚜 **Equipamento atual:** {equipamento_atual.get('nome')}"
        
        await message.answer(
            f"📋 **Módulo Checklist NR12**\n\n"
            f"👤 Operador: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}"
            f"{equipamento_info}\n\n"
            f"🎯 **Escolha uma opção:**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro no menu de checklist: {e}")
        await message.answer("❌ Erro interno no módulo checklist.")

async def handle_checklist_callback(callback: CallbackQuery, state: FSMContext):
    """Handler para callbacks do checklist"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data == "checklist_meus":
            await mostrar_meus_checklists(callback.message, operador)
            
        elif data == "checklist_equipamentos":
            await mostrar_equipamentos_checklist(callback.message, operador)
            
        elif data == "checklist_hoje":
            await verificar_checklist_hoje(callback.message, operador)
            
        elif data == "checklist_relatorios":
            await mostrar_relatorios_checklist(callback.message, operador)
            
        elif data.startswith("selecionar_eq_"):
            equipamento_id = int(data.split("_")[-1])
            await selecionar_equipamento(callback.message, equipamento_id, operador)
            
        elif data.startswith("iniciar_checklist_"):
            equipamento_id = int(data.split("_")[-1])
            await iniciar_novo_checklist(callback.message, equipamento_id, operador, state)
            
        elif data.startswith("continuar_checklist_"):
            checklist_id = int(data.split("_")[-1])
            await continuar_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("executar_checklist_"):
            checklist_id = int(data.split("_")[-1])
            await executar_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("resposta_"):
            await processar_resposta_checklist(callback, operador, state)
            
        elif data == "finalizar_checklist":
            await finalizar_checklist_completo(callback.message, operador, state)
            
        elif data == "salvar_checklist":
            await salvar_checklist_final(callback, operador, state)
            
    except Exception as e:
        logger.error(f"Erro no callback de checklist: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# FUNÇÕES DE NAVEGAÇÃO (COM API REAL)
# ===============================================

async def mostrar_meus_checklists(message: Message, operador: dict):
    """Mostra checklists reais do operador"""
    try:
        # Buscar checklists reais do dia atual
        checklists_hoje = await buscar_checklists_operador_hoje(operador.get('id', 0))
        
        if not checklists_hoje:
            await message.answer(
                f"📋 **Meus Checklists - Hoje**\n\n"
                f"👤 Operador: {operador.get('nome')}\n"
                f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
                f"📊 **Nenhum checklist encontrado para hoje.**\n\n"
                f"💡 Acesse um equipamento para iniciar um checklist.",
                parse_mode='Markdown'
            )
            return
        
        # Contar status
        concluidos = len([c for c in checklists_hoje if c.get('status') == 'CONCLUIDO'])
        pendentes = len([c for c in checklists_hoje if c.get('status') == 'PENDENTE'])
        em_andamento = len([c for c in checklists_hoje if c.get('status') == 'EM_ANDAMENTO'])
        
        keyboard = []
        
        # Adicionar checklists do dia
        for checklist in checklists_hoje[:5]:  # Máximo 5 para não sobrecarregar
            status = checklist.get('status', 'PENDENTE')
            status_emoji = {
                'CONCLUIDO': '✅',
                'EM_ANDAMENTO': '🔄',
                'PENDENTE': '⏳',
                'CANCELADO': '❌'
            }.get(status, '⚪')
            
            equipamento_nome = checklist.get('equipamento_nome', 'Equipamento')
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{status_emoji} {equipamento_nome}", 
                    callback_data=f"ver_checklist_{checklist.get('id')}"
                )
            ])
        
        keyboard.extend([
            [InlineKeyboardButton(text="📅 Esta Semana", callback_data="meus_checklist_semana")],
            [InlineKeyboardButton(text="📊 Estatísticas", callback_data="meus_checklist_stats")],
            [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_checklist")]
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        total = len(checklists_hoje)
        taxa_conclusao = (concluidos / total * 100) if total > 0 else 0
        
        await message.answer(
            f"📋 **Meus Checklists - Hoje**\n\n"
            f"👤 Operador: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"📊 **Resumo:**\n"
            f"• ✅ Concluídos: {concluidos}\n"
            f"• 🔄 Em andamento: {em_andamento}\n"
            f"• ⏳ Pendentes: {pendentes}\n"
            f"• 📈 Taxa de conclusão: {taxa_conclusao:.1f}%\n\n"
            f"🎯 **Checklists de hoje:**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar meus checklists: {e}")
        await message.answer("❌ Erro ao carregar checklists")

async def mostrar_equipamentos_checklist(message: Message, operador: dict):
    """Mostra equipamentos reais disponíveis para checklist"""
    try:
        # Buscar equipamentos reais da API
        equipamentos = await listar_equipamentos()
        
        if not equipamentos:
            await message.answer(
                f"❌ **Nenhum Equipamento Encontrado**\n\n"
                f"Não foi possível carregar a lista de equipamentos.\n"
                f"Verifique a conexão com o sistema.",
                parse_mode='Markdown'
            )
            return
        
        keyboard = []
        
        # Filtrar apenas equipamentos disponíveis
        equipamentos_disponiveis = [
            eq for eq in equipamentos 
            if eq.get('status_operacional') in ['DISPONIVEL', 'EM_USO']
        ]
        
        if not equipamentos_disponiveis:
            await message.answer(
                f"⚠️ **Nenhum Equipamento Disponível**\n\n"
                f"Todos os equipamentos estão em manutenção ou indisponíveis.\n"
                f"Total de equipamentos: {len(equipamentos)}",
                parse_mode='Markdown'
            )
            return
        
        for eq in equipamentos_disponiveis[:10]:  # Máximo 10 equipamentos
            status = eq.get('status_operacional', 'DESCONHECIDO')
            status_emoji = "✅" if status == "DISPONIVEL" else "🔄"
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{status_emoji} {eq.get('nome', 'Equipamento')}", 
                    callback_data=f"selecionar_eq_{eq.get('id')}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_checklist")])
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            f"🚜 **Equipamentos Disponíveis**\n\n"
            f"📋 Selecione um equipamento para gerenciar checklist:\n\n"
            f"✅ = Disponível\n"
            f"🔄 = Em uso\n\n"
            f"📊 Total disponível: {len(equipamentos_disponiveis)}\n"
            f"⚠️ **Lembrança NR12:** Todo equipamento deve ter checklist diário obrigatório.",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar equipamentos: {e}")
        await message.answer("❌ Erro ao carregar equipamentos")

async def selecionar_equipamento(message: Message, equipamento_id: int, operador: dict):
    """Seleciona um equipamento real e mostra opções"""
    try:
        # Buscar equipamentos para encontrar o selecionado
        equipamentos = await listar_equipamentos()
        equipamento = next((eq for eq in equipamentos if eq.get('id') == equipamento_id), None)
        
        if not equipamento:
            await message.answer("❌ Equipamento não encontrado")
            return
        
        # Definir como equipamento atual
        chat_id = str(message.chat.id)
        await definir_equipamento_atual(chat_id, equipamento)
        
        # Verificar se já existe checklist hoje (API real)
        checklist_hoje = await verificar_checklist_equipamento_hoje(equipamento_id)
        
        keyboard = []
        
        if checklist_hoje:
            status_checklist = checklist_hoje.get('status', 'PENDENTE')
            if status_checklist == 'CONCLUIDO':
                keyboard.extend([
                    [InlineKeyboardButton(text="👀 Ver Checklist Concluído", callback_data=f"ver_checklist_{checklist_hoje.get('id')}")],
                    [InlineKeyboardButton(text="📋 Novo Checklist", callback_data=f"iniciar_checklist_{equipamento_id}")]
                ])
            else:
                keyboard.extend([
                    [InlineKeyboardButton(text="▶️ Continuar Checklist", callback_data=f"continuar_checklist_{checklist_hoje.get('id')}")],
                    [InlineKeyboardButton(text="👀 Ver Progresso", callback_data=f"ver_checklist_{checklist_hoje.get('id')}")]
                ])
        else:
            keyboard.append([
                InlineKeyboardButton(text="📋 Iniciar Checklist NR12", callback_data=f"iniciar_checklist_{equipamento_id}")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton(text="📊 Histórico", callback_data=f"historico_eq_{equipamento_id}")],
            [InlineKeyboardButton(text="🔙 Voltar", callback_data="checklist_equipamentos")]
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        status_text = Formatters.formatar_status(equipamento.get('status_operacional', 'DESCONHECIDO'))
        
        if checklist_hoje:
            status_checklist = checklist_hoje.get('status', 'PENDENTE')
            checklist_status = f"📋 Checklist: {Formatters.formatar_status(status_checklist)}"
        else:
            checklist_status = "⚠️ Checklist pendente para hoje"
        
        await message.answer(
            f"🚜 **{equipamento.get('nome', 'Equipamento')}**\n\n"
            f"📊 **Status:** {status_text}\n"
            f"{checklist_status}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y')}\n"
            f"👤 **Operador:** {operador.get('nome')}\n"
            f"🆔 **ID:** {equipamento.get('id')}\n\n"
            f"🎯 **O que você deseja fazer?**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao selecionar equipamento: {e}")
        await message.answer("❌ Erro ao