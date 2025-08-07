# ===============================================
# ARQUIVO: mandacaru_bot/bot_checklist/handlers.py
# Handlers completos do Checklist NR12
# ===============================================

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.session import (
    obter_operador_sessao, verificar_autenticacao,
    obter_equipamento_atual, definir_dados_temporarios,
    obter_dados_temporarios, definir_equipamento_atual,
    limpar_dados_temporarios
)
from core.db import fazer_requisicao_api, buscar_equipamento_por_id
from core.templates import MessageTemplates
from core.utils import Validators, Formatters

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
# FUNÇÕES DE API ESPECÍFICAS DO CHECKLIST
# ===============================================

async def buscar_checklists_operador(operador_id: int) -> List[Dict[str, Any]]:
    """Busca checklists disponíveis para o operador"""
    logger.info(f"🔍 Buscando checklists para operador {operador_id}")
    
    result = await fazer_requisicao_api('GET', f'operadores/{operador_id}/equipamentos/')
    
    if result and result.get('success'):
        checklists = result.get('results', [])
        logger.info(f"✅ {len(checklists)} checklists encontrados")
        return checklists
    
    logger.warning(f"⚠️ Nenhum checklist encontrado para operador {operador_id}")
    return []

async def buscar_equipamentos_operador(operador_id: int) -> List[Dict[str, Any]]:
    """Busca equipamentos que o operador pode operar"""
    logger.info(f"🔍 Buscando equipamentos para operador {operador_id}")
    
    result = await fazer_requisicao_api('GET', f'operadores/{operador_id}/equipamentos/')
    
    if result and result.get('success'):
        equipamentos = result.get('equipamentos', [])
        logger.info(f"✅ {len(equipamentos)} equipamentos encontrados")
        return equipamentos
    
    logger.warning(f"⚠️ Nenhum equipamento encontrado para operador {operador_id}")
    return []

async def criar_checklist_equipamento(
    equipamento_id: int, 
    operador_codigo: str,
    turno: str = "MANHA"
) -> Optional[Dict[str, Any]]:
    """Cria novo checklist para equipamento"""
    logger.info(f"➕ Criando checklist para equipamento {equipamento_id}")
    
    data = {
        'acao': 'criar_checklist',
        'operador_codigo': operador_codigo,
        'turno': turno,
        'frequencia': 'DIARIA'
    }
    
    result = await fazer_requisicao_api('POST', f'nr12/bot/equipamento/{equipamento_id}/', data=data)
    
    if result and result.get('success'):
        logger.info(f"✅ Checklist criado: {result.get('checklist', {}).get('id')}")
        return result
    
    logger.error(f"❌ Erro ao criar checklist: {result.get('error', 'Erro desconhecido') if result else 'Sem resposta'}")
    return None

async def iniciar_checklist(checklist_id: int, operador_codigo: str) -> Optional[Dict[str, Any]]:
    """Inicia execução de checklist"""
    logger.info(f"▶️ Iniciando checklist {checklist_id}")
    
    data = {
        'acao': 'iniciar_checklist',
        'checklist_id': checklist_id,
        'operador_codigo': operador_codigo
    }
    
    # Usar endpoint genérico para buscar dados do checklist
    result = await fazer_requisicao_api('GET', f'nr12/checklists/{checklist_id}/')
    
    if result:
        logger.info(f"✅ Checklist {checklist_id} iniciado")
        return result
    
    logger.error(f"❌ Erro ao iniciar checklist {checklist_id}")
    return None

async def buscar_itens_checklist(checklist_id: int) -> List[Dict[str, Any]]:
    """Busca itens de um checklist"""
    logger.info(f"📋 Buscando itens do checklist {checklist_id}")
    
    result = await fazer_requisicao_api('GET', f'nr12/checklists/{checklist_id}/itens/')
    
    if result:
        itens = result.get('results', []) if isinstance(result, dict) else result
        logger.info(f"✅ {len(itens)} itens encontrados")
        return itens
    
    logger.warning(f"⚠️ Nenhum item encontrado para checklist {checklist_id}")
    return []

async def atualizar_item_checklist(
    item_id: int,
    status: str,
    observacao: str = "",
    operador_codigo: str = "BOT001"
) -> bool:
    """Atualiza item do checklist usando endpoint correto"""
    logger.info(f"🔄 Atualizando item {item_id} com status {status}")
    
    data = {
        'item_id': item_id,
        'status': status,
        'observacao': observacao,
        'operador_codigo': operador_codigo
    }
    
    result = await fazer_requisicao_api('POST', 'nr12/bot/item-checklist/atualizar/', data=data)
    
    if result and result.get('success'):
        logger.info(f"✅ Item {item_id} atualizado com sucesso")
        return True
    
    logger.error(f"❌ Erro ao atualizar item {item_id}: {result.get('error', 'Erro desconhecido') if result else 'Sem resposta'}")
    return False

# ===============================================
# HANDLERS PRINCIPAIS
# ===============================================

def require_auth(handler):
    """Decorator que exige autenticação (reutilizado do módulo principal)"""
    async def wrapper(obj, *args, **kwargs):
        # Determinar chat_id baseado no tipo de objeto
        if hasattr(obj, 'chat'):
            chat_id = str(obj.chat.id)
        elif hasattr(obj, 'message') and hasattr(obj.message, 'chat'):
            chat_id = str(obj.message.chat.id)
        else:
            logger.error("❌ Não foi possível determinar chat_id")
            return
        
        # Verificar autenticação
        if not verificar_autenticacao(chat_id):
            await obj.answer(MessageTemplates.unauthorized_access())
            return
        
        # Adicionar operador aos argumentos
        operador = obter_operador_sessao(chat_id)
        kwargs['operador'] = operador
        
        return await handler(obj, *args, **kwargs)
    
    return wrapper

@require_auth
async def listar_checklists_handler(callback: CallbackQuery, operador=None):
    """Lista checklists disponíveis para o operador"""
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer()
        
        # Buscar checklists do operador
        checklists = await buscar_checklists_operador(operador['id'])
        
        if not checklists:
            await callback.message.edit_text(
                "📋 **Nenhum Checklist Disponível**\n\n"
                "Você não possui checklists pendentes no momento.\n\n"
                "💡 Escaneie um QR Code de equipamento para criar um novo checklist.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]
                ])
            )
            return
        
        # Criar keyboard com checklists
        keyboard = []
        texto = MessageTemplates.checklist_list_header()
        
        for i, checklist in enumerate(checklists[:10], 1):
            equipamento_nome = checklist.get('equipamento_nome', 'Equipamento')
            status = checklist.get('status', 'PENDENTE')
            data_checklist = checklist.get('data_checklist', 'Hoje')
            
            # Emoji baseado no status
            emoji = "📋" if status == "PENDENTE" else "✅" if status == "CONCLUIDO" else "🔄"
            
            texto += f"\n{i}. {emoji} **{equipamento_nome}**"
            texto += f"\n   Status: {status}"
            texto += f"\n   Data: {data_checklist}\n"
            
            # Botão para acessar checklist
            callback_data = f"checklist_select_{checklist.get('id', 0)}"
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{emoji} {equipamento_nome}",
                    callback_data=callback_data
                )
            ])
        
        # Botão de voltar
        keyboard.append([
            InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")
        ])
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar checklists: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def listar_equipamentos_handler(callback: CallbackQuery, operador=None):
    """Lista equipamentos disponíveis para o operador"""
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer()
        
        # Buscar equipamentos do operador
        equipamentos = await buscar_equipamentos_operador(operador['id'])
        
        if not equipamentos:
            await callback.message.edit_text(
                "🚜 **Nenhum Equipamento Disponível**\n\n"
                "Você não tem equipamentos autorizados para operar.\n\n"
                "💡 Contate seu supervisor para obter acesso.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]
                ])
            )
            return
        
        # Criar keyboard com equipamentos
        keyboard = []
        texto = "🚜 **Equipamentos Disponíveis**\n\nSelecione um equipamento:"
        
        for i, equipamento in enumerate(equipamentos[:10], 1):
            nome = equipamento.get('nome', 'Equipamento')
            status = equipamento.get('status_operacional', 'Operacional')
            horimetro = equipamento.get('horimetro_atual', 0)
            
            # Emoji baseado no status
            emoji = "🟢" if status == "Operacional" else "🟡" if status == "Manutenção" else "🔴"
            
            texto += f"\n{i}. {emoji} **{nome}**"
            texto += f"\n   Status: {status}"
            texto += f"\n   Horímetro: {Formatters.formatar_horimetro(horimetro)}\n"
            
            # Botão para selecionar equipamento
            callback_data = f"equipment_select_{equipamento.get('id', 0)}"
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{emoji} {nome}",
                    callback_data=callback_data
                )
            ])
        
        # Botão de voltar
        keyboard.append([
            InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")
        ])
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar equipamentos: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def selecionar_equipamento_handler(callback: CallbackQuery, operador=None):
    """Seleciona equipamento e mostra opções"""
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer()
        
        # Extrair ID do equipamento
        equipamento_id = int(callback.data.split('_')[-1])
        
        # Buscar dados do equipamento
        equipamento = await buscar_equipamento_por_id(equipamento_id)
        
        if not equipamento:
            await callback.message.edit_text(
                "❌ **Equipamento Não Encontrado**\n\n"
                "Não foi possível localizar o equipamento selecionado.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="list_equipamentos")]
                ])
            )
            return
        
        # Salvar equipamento na sessão
        definir_equipamento_atual(chat_id, equipamento)
        
        # Criar menu do equipamento
        nome = equipamento.get('nome', 'Equipamento')
        status = equipamento.get('status_operacional', 'N/A')
        horimetro = equipamento.get('horimetro_atual', 0)
        
        texto = MessageTemplates.equipment_menu(nome)
        texto += f"\n**Status:** {status}"
        texto += f"\n**Horímetro:** {Formatters.formatar_horimetro(horimetro)}"
        
        keyboard = [
            [
                InlineKeyboardButton(text="📋 Novo Checklist", callback_data=f"create_checklist_{equipamento_id}"),
                InlineKeyboardButton(text="📊 Ver Histórico", callback_data=f"checklist_history_{equipamento_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Voltar", callback_data="list_equipamentos"),
                InlineKeyboardButton(text="🏠 Menu", callback_data="menu_refresh")
            ]
        ]
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao selecionar equipamento: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def criar_checklist_handler(callback: CallbackQuery, operador=None):
    """Cria novo checklist para equipamento"""
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer("⏳ Criando checklist...", show_alert=True)
        
        # Extrair ID do equipamento
        equipamento_id = int(callback.data.split('_')[-1])
        
        # Criar checklist
        resultado = await criar_checklist_equipamento(
            equipamento_id, 
            operador['codigo']
        )
        
        if resultado and resultado.get('success'):
            checklist = resultado.get('checklist', {})
            checklist_id = checklist.get('id')
            
            # Salvar dados do checklist na sessão
            definir_dados_temporarios(chat_id, 'checklist_atual', checklist)
            
            # Mostrar confirmação e opções
            texto = f"✅ **Checklist Criado!**\n\n"
            texto += f"**ID:** {checklist_id}\n"
            texto += f"**Turno:** {checklist.get('turno', 'MANHA')}\n"
            texto += f"**Total de itens:** {checklist.get('total_itens', '?')}\n\n"
            texto += "O que deseja fazer?"
            
            keyboard = [
                [InlineKeyboardButton(text="▶️ Iniciar Agora", callback_data=f"start_checklist_{checklist_id}")],
                [InlineKeyboardButton(text="📋 Ver Detalhes", callback_data=f"checklist_details_{checklist_id}")],
                [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"equipment_select_{equipamento_id}")]
            ]
            
            await callback.message.edit_text(
                texto,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        else:
            erro = resultado.get('error', 'Erro desconhecido') if resultado else 'Falha na comunicação'
            
            await callback.message.edit_text(
                f"❌ **Erro ao Criar Checklist**\n\n{erro}\n\n"
                "Tente novamente ou contate o suporte.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Tentar Novamente", callback_data=f"create_checklist_{equipamento_id}")],
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"equipment_select_{equipamento_id}")]
                ])
            )
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar checklist: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def executar_checklist_handler(callback: CallbackQuery, state: FSMContext, operador=None):
    """Inicia execução de checklist item por item"""
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer("⏳ Carregando checklist...")
        
        # Extrair ID do checklist
        checklist_id = int(callback.data.split('_')[-1])
        
        # Buscar dados do checklist
        checklist = await buscar_checklist_por_id(checklist_id)
        
        if not checklist:
            await callback.message.edit_text(
                "❌ **Checklist Não Encontrado**\n\n"
                "Não foi possível localizar o checklist selecionado.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="list_checklists")]
                ])
            )
            return
        
        # Buscar itens do checklist
        itens = await buscar_itens_checklist(checklist_id)
        
        if not itens:
            await callback.message.edit_text(
                "📋 **Checklist Vazio**\n\n"
                "Este checklist não possui itens para verificação.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="list_checklists")]
                ])
            )
            return
        
        # Filtrar apenas itens pendentes
        itens_pendentes = [item for item in itens if item.get('status') == 'PENDENTE']
        
        if not itens_pendentes:
            await callback.message.edit_text(
                "✅ **Checklist Completo**\n\n"
                "Todos os itens já foram verificados!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Ver Resultado", callback_data=f"checklist_result_{checklist_id}")],
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="list_checklists")]
                ])
            )
            return
        
        # Salvar dados na sessão
        definir_dados_temporarios(chat_id, 'checklist_ativo', checklist)
        definir_dados_temporarios(chat_id, 'itens_checklist', itens)
        definir_dados_temporarios(chat_id, 'itens_pendentes', itens_pendentes)
        definir_dados_temporarios(chat_id, 'item_atual_index', 0)
        
        # Iniciar primeiro item
        await mostrar_proximo_item(callback.message, chat_id, state)
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar checklist: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

async def mostrar_proximo_item(message: Message, chat_id: str, state: FSMContext):
    """Mostra o próximo item do checklist"""
    try:
        # Obter dados da sessão
        checklist = obter_dados_temporarios(chat_id, 'checklist_ativo')
        itens_pendentes = obter_dados_temporarios(chat_id, 'itens_pendentes', [])
        index_atual = obter_dados_temporarios(chat_id, 'item_atual_index', 0)
        
        if index_atual >= len(itens_pendentes):
            # Todos os itens foram processados
            await finalizar_checklist_completo(message, chat_id)
            return
        
        item_atual = itens_pendentes[index_atual]
        total_itens = len(itens_pendentes)
        
        # Informações do item
        item_text = item_atual.get('item', 'Item não especificado')
        descricao = item_atual.get('descricao', '')
        criticidade = item_atual.get('criticidade', 'BAIXA')
        
        # Criar texto da pergunta
        texto = MessageTemplates.checklist_item_question(
            index_atual + 1, 
            total_itens, 
            item_text
        )
        
        if descricao:
            texto += f"\n\n**Descrição:** {descricao}"
        
        # Emoji baseado na criticidade
        if criticidade == 'CRITICA':
            texto += f"\n\n🔴 **ITEM CRÍTICO** - Falha pode parar operação"
        elif criticidade == 'ALTA':
            texto += f"\n\n🟡 **Alta prioridade**"
        
        # Criar keyboard de respostas
        keyboard = []
        
        # Botões de resposta
        keyboard.append([
            InlineKeyboardButton(text="✅ OK", callback_data=f"item_ok_{item_atual['id']}"),
            InlineKeyboardButton(text="❌ NOK", callback_data=f"item_nok_{item_atual['id']}")
        ])
        
        # Se permite N/A
        if item_atual.get('permite_na', False):
            keyboard.append([
                InlineKeyboardButton(text="➖ N/A", callback_data=f"item_na_{item_atual['id']}")
            ])
        
        # Botões de ação
        keyboard.append([
            InlineKeyboardButton(text="📝 Observação", callback_data=f"item_obs_{item_atual['id']}"),
            InlineKeyboardButton(text="📸 Foto", callback_data=f"item_photo_{item_atual['id']}")
        ])
        
        # Botão de sair
        keyboard.append([
            InlineKeyboardButton(text="💾 Salvar e Sair", callback_data="checklist_save_exit"),
            InlineKeyboardButton(text="🔙 Anterior", callback_data="item_previous") if index_atual > 0 else None
        ])
        
        # Filtrar botões None
        keyboard = [[btn for btn in row if btn is not None] for row in keyboard]
        
        # Definir estado
        await state.set_state(ChecklistStates.executando_checklist)
        
        try:
            await message.edit_text(
                texto,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        except:
            await message.answer(
                texto,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar próximo item: {e}")
        await message.answer(MessageTemplates.error_generic())

@require_auth
async def processar_resposta_item(callback: CallbackQuery, state: FSMContext, operador=None):
    """Processa resposta de item do checklist"""
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer()
        
        # Extrair dados do callback
        partes = callback.data.split('_')
        acao = partes[1]  # ok, nok, na
        item_id = int(partes[2])
        
        # Mapear ação para status
        status_map = {
            'ok': 'OK',
            'nok': 'NOK',
            'na': 'NA'
        }
        
        status = status_map.get(acao, 'PENDENTE')
        
        # Atualizar item na API
        sucesso = await atualizar_item_checklist_nr12(
            item_id, 
            status, 
            "",  # observação vazia por enquanto
            operador['codigo']
        )
        
        if sucesso:
            # Avançar para próximo item
            index_atual = obter_dados_temporarios(chat_id, 'item_atual_index', 0)
            definir_dados_temporarios(chat_id, 'item_atual_index', index_atual + 1)
            
            # Mostrar próximo item
            await mostrar_proximo_item(callback.message, chat_id, state)
        else:
            await callback.message.edit_text(
                "❌ **Erro ao Salvar Resposta**\n\n"
                "Não foi possível salvar a resposta. Tente novamente.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Tentar Novamente", callback_data=callback.data)],
                    [InlineKeyboardButton(text="💾 Salvar e Sair", callback_data="checklist_save_exit")]
                ])
            )
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar resposta: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

async def finalizar_checklist_completo(message: Message, chat_id: str):
    """Finaliza checklist completamente"""
    try:
        checklist = obter_dados_temporarios(chat_id, 'checklist_ativo')
        
        if not checklist:
            await message.edit_text("❌ Erro: Dados do checklist perdidos")
            return
        
        # Buscar resultado final
        checklist_final = await buscar_checklist_por_id(checklist['id'])
        
        if checklist_final:
            equipamento_nome = checklist_final.get('equipamento_nome', 'Equipamento')
            total_itens = checklist_final.get('total_itens', 0)
            itens_ok = checklist_final.get('itens_aprovados', 0)
            
            texto = MessageTemplates.checklist_completed(
                equipamento_nome,
                total_itens,
                itens_ok
            )
        else:
            texto = "✅ **Checklist Finalizado!**\n\nO checklist foi concluído com sucesso."
        
        # Limpar dados temporários
        limpar_dados_temporarios(chat_id)
        
        keyboard = [
            [InlineKeyboardButton(text="📊 Ver Relatório", callback_data=f"checklist_report_{checklist['id']}")],
            [InlineKeyboardButton(text="📋 Novo Checklist", callback_data="list_equipamentos")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]
        ]
        
        await message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao finalizar checklist: {e}")
        await message.answer(MessageTemplates.error_generic())

# ===============================================
# REGISTRAR HANDLERS ATUALIZADOS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra handlers de checklist no dispatcher"""
    
    # Callbacks de checklist
    dp.callback_query.register(listar_checklists_handler, F.data == "list_checklists")
    dp.callback_query.register(listar_equipamentos_handler, F.data == "list_equipamentos")
    dp.callback_query.register(selecionar_equipamento_handler, F.data.startswith("equipment_select_"))
    dp.callback_query.register(criar_checklist_handler, F.data.startswith("create_checklist_"))
    
    # Callbacks de execução de checklist
    dp.callback_query.register(executar_checklist_handler, F.data.startswith("checklist_select_"))
    dp.callback_query.register(executar_checklist_handler, F.data.startswith("start_checklist_"))
    
    # Callbacks de resposta de itens
    dp.callback_query.register(processar_resposta_item, F.data.startswith("item_ok_"))
    dp.callback_query.register(processar_resposta_item, F.data.startswith("item_nok_"))
    dp.callback_query.register(processar_resposta_item, F.data.startswith("item_na_"))
    
    logger.info("✅ Handlers de checklist registrados")