# -*- coding: utf-8 -*-
# ===============================================
# HANDLERS COMPLETOS DO CHECKLIST - VERSÃO CORRIGIDA
# ===============================================

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, Union
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Imports do core
from core.db import (
    buscar_equipamentos_com_nr12, buscar_checklists_nr12,
    criar_checklist_nr12, buscar_itens_checklist_nr12,
    atualizar_item_checklist_nr12, finalizar_checklist_nr12
)
from core.session import (
    obter_operador_sessao, verificar_autenticacao,
    definir_dados_temporarios, obter_dados_temporarios,
    limpar_dados_temporarios
)
from core.templates import MessageTemplates
from core.middleware import require_auth

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
async def comando_checklist(message: Message, operador: dict = None):
    """Handler principal do comando /checklist"""
    try:
        await mostrar_menu_checklist(message, operador)
    except Exception as e:
        logger.error(f"Erro no comando checklist: {e}")
        await message.answer("❌ Erro ao carregar checklist. Tente novamente.")

async def mostrar_menu_checklist(message: Message, operador: dict):
    """Mostra menu principal do checklist"""
    try:
        # Buscar checklists pendentes do operador
        operador_id = operador.get('id')
        checklists_hoje = await buscar_checklists_nr12(operador_id=operador_id)
        
        # Contar checklists por status
        pendentes = len([c for c in checklists_hoje if c.get('status') == 'PENDENTE'])
        em_andamento = len([c for c in checklists_hoje if c.get('status') == 'EM_ANDAMENTO'])
        
        texto = f"📋 **Checklist NR12**\n\n"
        texto += f"👤 **Operador:** {operador.get('nome')}\n"
        texto += f"📅 **Data:** {date.today().strftime('%d/%m/%Y')}\n\n"
        texto += f"📊 **Status:**\n"
        texto += f"   🟡 Pendentes: {pendentes}\n"
        texto += f"   🔵 Em andamento: {em_andamento}\n\n"
        texto += f"Escolha uma opção:"
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="🔍 Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="➕ Novo Checklist", callback_data="checklist_novo")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar menu checklist: {e}")
        await message.answer("❌ Erro ao carregar menu. Tente novamente.")

async def mostrar_equipamentos_checklist(message: Message, operador: dict):
    """Mostra equipamentos disponíveis para checklist"""
    try:
        # Buscar equipamentos com NR12 do operador
        operador_id = operador.get('id')
        equipamentos = await buscar_equipamentos_com_nr12(operador_id=operador_id)
        
        if not equipamentos:
            await message.answer(
                "🔧 **Equipamentos NR12**\n\n"
                "❌ Nenhum equipamento encontrado\n\n"
                "Você não tem equipamentos com NR12 configurado\n"
                "ou não há equipamentos disponíveis no momento.\n\n"
                "💬 Entre em contato com o supervisor.",
                parse_mode='Markdown'
            )
            return
        
        texto = f"🔧 **Equipamentos NR12**\n\n"
        texto += f"Selecione um equipamento para checklist:\n\n"
        
        keyboard = []
        for equipamento in equipamentos[:10]:  # Limitar a 10
            nome = equipamento.get('nome', equipamento.get('numero_serie', 'Sem nome'))
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🔧 {nome}",
                    callback_data=f"selecionar_eq_{equipamento['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="🔄 Atualizar", callback_data="checklist_equipamentos"),
            InlineKeyboardButton(text="◀️ Voltar", callback_data="checklist_menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar equipamentos: {e}")
        await message.answer("❌ Erro ao carregar equipamentos. Tente novamente.")

async def mostrar_meus_checklists(message: Message, operador: dict):
    """Mostra checklists do operador"""
    try:
        operador_id = operador.get('id')
        checklists = await buscar_checklists_nr12(operador_id=operador_id)
        
        if not checklists:
            texto = "📋 **Meus Checklists**\n\n"
            texto += "❌ Nenhum checklist encontrado\n\n"
            texto += "Você ainda não possui checklists atribuídos."
        else:
            texto = f"📋 **Meus Checklists**\n\n"
            texto += f"📊 Total: {len(checklists)}\n\n"
            
            for checklist in checklists[:5]:  # Mostrar últimos 5
                status_emoji = {
                    'PENDENTE': '🟡',
                    'EM_ANDAMENTO': '🔵', 
                    'CONCLUIDO': '✅',
                    'CANCELADO': '❌'
                }.get(checklist.get('status', ''), '❓')
                
                equipamento_nome = checklist.get('equipamento_nome', 'Equipamento')
                data_str = checklist.get('data_checklist', 'Sem data')
                
                texto += f"{status_emoji} **{equipamento_nome}**\n"
                texto += f"   📅 {data_str}\n"
                texto += f"   📊 {checklist.get('status', 'Sem status')}\n\n"
        
        keyboard = [
            [InlineKeyboardButton(text="🔄 Atualizar", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="◀️ Voltar", callback_data="checklist_menu")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar meus checklists: {e}")
        await message.answer("❌ Erro ao carregar seus checklists.")

# ===============================================
# HANDLER DE CALLBACKS
# ===============================================

async def handle_checklist_callback(callback: CallbackQuery, state: FSMContext):
    """Handler principal para todos os callbacks do checklist"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        # Processar diferentes tipos de callback
        if data == "checklist_menu":
            await mostrar_menu_checklist(callback.message, operador)
            
        elif data == "checklist_meus":
            await mostrar_meus_checklists(callback.message, operador)
            
        elif data == "checklist_equipamentos":
            await mostrar_equipamentos_checklist(callback.message, operador)
            
        elif data == "checklist_novo":
            await mostrar_equipamentos_checklist(callback.message, operador)
            
        elif data.startswith("selecionar_eq_"):
            equipamento_id = int(data.split("_")[-1])
            await iniciar_checklist_equipamento(callback, equipamento_id, operador, state)
            
        elif data.startswith("iniciar_checklist_"):
            checklist_id = int(data.split("_")[-1])
            await iniciar_execucao_checklist(callback, checklist_id, operador, state)
            
        elif data.startswith("continuar_checklist_"):
            checklist_id = int(data.split("_")[-1])
            await continuar_execucao_checklist(callback, checklist_id, operador, state)
            
        elif data.startswith("resposta_"):
            await processar_resposta_item(callback, operador, state)
            
        elif data == "finalizar_checklist":
            await finalizar_checklist_atual(callback, operador, state)
            
        elif data == "pausar_checklist":
            await callback.answer("⏸️ Checklist pausado")
            await callback.message.answer("⏸️ Checklist pausado. Use /checklist para continuar.")
            await state.clear()
            
        else:
            await callback.answer("❓ Ação não reconhecida")
        
        await callback.answer()
            
    except Exception as e:
        logger.error(f"Erro no callback checklist: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# FUNÇÕES DE CHECKLIST
# ===============================================

async def iniciar_checklist_equipamento(callback: CallbackQuery, equipamento_id: int, operador: dict, state: FSMContext):
    """Inicia processo de checklist para um equipamento"""
    try:
        # Verificar se já existe checklist hoje
        hoje = date.today().strftime('%Y-%m-%d')
        checklists_hoje = await buscar_checklists_nr12(
            equipamento_id=equipamento_id,
            operador_id=operador.get('id')
        )
        
        checklist_hoje = None
        for c in checklists_hoje:
            if c.get('data_checklist') == hoje:
                checklist_hoje = c
                break
        
        if checklist_hoje:
            if checklist_hoje.get('status') == 'CONCLUIDO':
                await callback.message.answer(
                    "✅ **Checklist já concluído**\n\n"
                    "O checklist deste equipamento já foi realizado hoje.\n\n"
                    "📊 Status: Concluído",
                    parse_mode='Markdown'
                )
                return
            else:
                # Continuar checklist existente
                await continuar_execucao_checklist(callback, checklist_hoje['id'], operador, state)
                return
        
        # Criar novo checklist
        dados_checklist = {
            'equipamento_id': equipamento_id,
            'operador_id': operador.get('id'),
            'data_checklist': hoje,
            'turno': calcular_turno_atual(),
            'status': 'EM_ANDAMENTO'
        }
        
        novo_checklist = await criar_checklist_nr12(dados_checklist)
        
        if novo_checklist:
            await iniciar_execucao_checklist(callback, novo_checklist['id'], operador, state)
        else:
            await callback.message.answer("❌ Erro ao criar checklist. Tente novamente.")
            
    except Exception as e:
        logger.error(f"Erro ao iniciar checklist: {e}")
        await callback.message.answer("❌ Erro ao iniciar checklist.")

async def iniciar_execucao_checklist(callback: CallbackQuery, checklist_id: int, operador: dict, state: FSMContext):
    """Inicia a execução de um checklist"""
    try:
        # Buscar itens do checklist
        itens = await buscar_itens_checklist_nr12(checklist_id)
        
        if not itens:
            await callback.message.answer("❌ Checklist sem itens configurados.")
            return
        
        # Salvar dados na sessão
        chat_id = str(callback.from_user.id)
        await definir_dados_temporarios(chat_id, 'checklist_id', checklist_id)
        await definir_dados_temporarios(chat_id, 'itens', itens)
        await definir_dados_temporarios(chat_id, 'item_atual', 0)
        await definir_dados_temporarios(chat_id, 'respostas', {})
        
        # Definir estado
        await state.set_state(ChecklistStates.executando_checklist)
        
        # Mostrar primeiro item
        await mostrar_item_atual(callback.message, chat_id)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar execução: {e}")
        await callback.message.answer("❌ Erro ao carregar checklist.")

async def continuar_execucao_checklist(callback: CallbackQuery, checklist_id: int, operador: dict, state: FSMContext):
    """Continua execução de checklist em andamento"""
    try:
        # Implementar lógica para continuar checklist
        await iniciar_execucao_checklist(callback, checklist_id, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao continuar checklist: {e}")
        await callback.message.answer("❌ Erro ao continuar checklist.")

async def mostrar_item_atual(message: Message, chat_id: str):
    """Mostra o item atual do checklist"""
    try:
        itens = await obter_dados_temporarios(chat_id, 'itens', [])
        item_atual_idx = await obter_dados_temporarios(chat_id, 'item_atual', 0)
        
        if item_atual_idx >= len(itens):
            # Checklist completo
            await finalizar_checklist_automatico(message, chat_id)
            return
        
        item = itens[item_atual_idx]
        
        texto = f"📋 **Checklist - Item {item_atual_idx + 1}/{len(itens)}**\n\n"
        texto += f"❓ **{item.get('descricao', 'Item sem descrição')}**\n\n"
        
        if item.get('observacoes'):
            texto += f"📝 *{item.get('observacoes')}*\n\n"
        
        texto += "Selecione sua resposta:"
        
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Conforme", callback_data="resposta_conforme"),
                InlineKeyboardButton(text="❌ Não Conforme", callback_data="resposta_nao_conforme")
            ],
            [
                InlineKeyboardButton(text="❓ N/A", callback_data="resposta_na"),
                InlineKeyboardButton(text="⏸️ Pausar", callback_data="pausar_checklist")
            ]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar item: {e}")
        await message.answer("❌ Erro ao carregar item.")

async def processar_resposta_item(callback: CallbackQuery, operador: dict, state: FSMContext):
    """Processa resposta de um item do checklist"""
    try:
        chat_id = str(callback.from_user.id)
        resposta = callback.data.split("_")[-1]  # conforme, nao_conforme, na
        
        # Obter dados atuais
        itens = await obter_dados_temporarios(chat_id, 'itens', [])
        item_atual_idx = await obter_dados_temporarios(chat_id, 'item_atual', 0)
        respostas = await obter_dados_temporarios(chat_id, 'respostas', {})
        
        if item_atual_idx >= len(itens):
            await callback.answer("❌ Item não encontrado")
            return
        
        item = itens[item_atual_idx]
        
        # Salvar resposta
        respostas[str(item['id'])] = {
            'resposta': resposta,
            'data_resposta': datetime.now().isoformat(),
            'operador_id': operador.get('id')
        }
        
        # Atualizar na API
        await atualizar_item_checklist_nr12(item['id'], respostas[str(item['id'])])
        
        # Salvar dados atualizados
        await definir_dados_temporarios(chat_id, 'respostas', respostas)
        await definir_dados_temporarios(chat_id, 'item_atual', item_atual_idx + 1)
        
        # Mostrar próximo item
        await mostrar_item_atual(callback.message, chat_id)
        
    except Exception as e:
        logger.error(f"Erro ao processar resposta: {e}")
        await callback.answer("❌ Erro ao salvar resposta")

async def finalizar_checklist_automatico(message: Message, chat_id: str):
    """Finaliza checklist automaticamente quando todos os itens são respondidos"""
    try:
        checklist_id = await obter_dados_temporarios(chat_id, 'checklist_id')
        
        if checklist_id:
            resultado = await finalizar_checklist_nr12(checklist_id)
            
            if resultado:
                await message.answer(
                    "✅ **Checklist Concluído!**\n\n"
                    "Todos os itens foram verificados com sucesso.\n\n"
                    "📊 Status: Finalizado\n"
                    "📅 Data: " + datetime.now().strftime('%d/%m/%Y %H:%M'),
                    parse_mode='Markdown'
                )
            else:
                await message.answer("⚠️ Checklist completado mas houve erro na finalização.")
        
        # Limpar dados temporários
        await limpar_dados_temporarios(chat_id)
        
    except Exception as e:
        logger.error(f"Erro ao finalizar checklist: {e}")
        await message.answer("❌ Erro ao finalizar checklist.")

async def finalizar_checklist_atual(callback: CallbackQuery, operador: dict, state: FSMContext):
    """Finaliza checklist atual manualmente"""
    try:
        chat_id = str(callback.from_user.id)
        await finalizar_checklist_automatico(callback.message, chat_id)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao finalizar: {e}")
        await callback.answer("❌ Erro ao finalizar")

# ===============================================
# FUNÇÕES AUXILIARES
# ===============================================

def calcular_turno_atual() -> str:
    """Calcula o turno atual baseado na hora"""
    hora_atual = datetime.now().hour
    
    if 6 <= hora_atual < 14:
        return 'MANHA'
    elif 14 <= hora_atual < 22:
        return 'TARDE'
    else:
        return 'NOITE'

# ===============================================
# REGISTRO DOS HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers do módulo checklist"""
    
    # Comando principal
    dp.message.register(comando_checklist, Command("checklist"))
    
    # Callbacks do checklist
    dp.callback_query.register(
        handle_checklist_callback,
        F.data.startswith("checklist_")
    )
    dp.callback_query.register(
        handle_checklist_callback,
        F.data.startswith("selecionar_eq_")
    )
    dp.callback_query.register(
        handle_checklist_callback,
        F.data.startswith("iniciar_checklist_")
    )
    dp.callback_query.register(
        handle_checklist_callback,
        F.data.startswith("continuar_checklist_")
    )
    dp.callback_query.register(
        handle_checklist_callback,
        F.data.startswith("resposta_")
    )
    dp.callback_query.register(
        handle_checklist_callback,
        F.data == "finalizar_checklist"
    )
    dp.callback_query.register(
        handle_checklist_callback,
        F.data == "pausar_checklist"
    )
    
    logger.info("✅ Handlers de checklist registrados com sucesso")