# ===============================================
# ARQUIVO COMPLETADO: mandacaru_bot/bot_checklist/handlers.py
# Integração completa com API NR12 real - VERSÃO FINAL CORRIGIDA
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
from core.session import (
    obter_operador_sessao, verificar_autenticacao,
    obter_equipamento_atual, definir_dados_temporarios,
    obter_dados_temporarios, definir_equipamento_atual,
    limpar_dados_temporarios
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
# FUNÇÕES AUXILIARES
# ===============================================

async def obter_dados_checklist(chat_id: str) -> Optional[Dict[str, Any]]:
    """Obtém todos os dados temporários do checklist de forma consolidada"""
    try:
        checklist_id = await obter_dados_temporarios(chat_id, 'checklist_id')
        if not checklist_id:
            return None
            
        itens = await obter_dados_temporarios(chat_id, 'itens', [])
        item_atual = await obter_dados_temporarios(chat_id, 'item_atual', 0)
        respostas = await obter_dados_temporarios(chat_id, 'respostas', {})
        
        return {
            'checklist_id': checklist_id,
            'itens': itens,
            'item_atual': item_atual,
            'respostas': respostas
        }
    except Exception as e:
        logger.error(f"Erro ao obter dados do checklist: {e}")
        return None

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
# FUNÇÕES DE NAVEGAÇÃO
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
        
        # Montar texto com checklists encontrados
        texto = (
            f"📋 **Meus Checklists - Hoje**\n\n"
            f"👤 Operador: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        )
        
        # Adicionar cada checklist
        keyboard = []
        for checklist in checklists_hoje:
            equipamento_nome = checklist.get('equipamento_nome', 'Equipamento')
            status_emoji = {
                'PENDENTE': '🟡',
                'EM_ANDAMENTO': '🔵',
                'CONCLUIDO': '✅',
                'CANCELADO': '❌'
            }.get(checklist.get('status', 'PENDENTE'), '🟡')
            
            texto += (
                f"{status_emoji} **{equipamento_nome}**\n"
                f"   Status: {checklist.get('status', 'PENDENTE')}\n"
                f"   Turno: {checklist.get('turno', 'MANHA')}\n\n"
            )
            
            # Botão para acessar checklist
            if checklist.get('status') == 'EM_ANDAMENTO':
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"🔍 Continuar {equipamento_nome}",
                        callback_data=f"continuar_checklist_{checklist.get('id')}"
                    )
                ])
            elif checklist.get('status') == 'PENDENTE':
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"▶️ Iniciar {equipamento_nome}",
                        callback_data=f"executar_checklist_{checklist.get('id')}"
                    )
                ])
        
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="checklist_menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar meus checklists: {e}")
        await message.answer("❌ Erro ao buscar checklists.")

async def mostrar_equipamentos_checklist(message: Message, operador: dict):
    """Mostra equipamentos disponíveis para checklist"""
    try:
        # Buscar equipamentos com NR12 configurado
        equipamentos = await buscar_equipamentos_com_nr12()
        
        if not equipamentos:
            await message.answer(
                f"🔗 **Equipamentos NR12**\n\n"
                f"❌ **Nenhum equipamento encontrado**\n\n"
                f"Os equipamentos precisam ter NR12 configurado\n"
                f"para aparecer nesta lista.\n\n"
                f"💬 Entre em contato com o administrador.",
                parse_mode='Markdown'
            )
            return
        
        texto = (
            f"🔗 **Equipamentos NR12 Disponíveis**\n\n"
            f"👤 Operador: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"🎯 **Selecione um equipamento:**\n\n"
        )
        
        keyboard = []
        for equipamento in equipamentos[:10]:
            nome = equipamento.get('nome', 'Sem nome')
            status = equipamento.get('status_operacional', 'DESCONHECIDO')
            
            status_emoji = {
                'DISPONIVEL': '🟢',
                'EM_USO': '🔵',
                'MANUTENCAO': '🔧',
                'INATIVO': '❌'
            }.get(status, '❓')
            
            texto += f"{status_emoji} **{nome}** - {status}\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📋 {nome}",
                    callback_data=f"selecionar_eq_{equipamento.get('id')}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="checklist_menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar equipamentos: {e}")
        await message.answer("❌ Erro ao buscar equipamentos.")

async def verificar_checklist_hoje(message: Message, operador: dict):
    """Verifica status dos checklists do dia"""
    try:
        # Buscar todos os checklists de hoje
        hoje = date.today().isoformat()
        checklists_hoje = await buscar_checklists_nr12(data_checklist=hoje)
        
        if not checklists_hoje:
            await message.answer(
                f"✅ **Checklists do Dia**\n\n"
                f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
                f"📊 **Nenhum checklist programado para hoje.**\n\n"
                f"💡 Os checklists são criados automaticamente\n"
                f"ou podem ser iniciados manualmente.",
                parse_mode='Markdown'
            )
            return
        
        # Contar por status
        total = len(checklists_hoje)
        pendentes = sum(1 for c in checklists_hoje if c.get('status') == 'PENDENTE')
        em_andamento = sum(1 for c in checklists_hoje if c.get('status') == 'EM_ANDAMENTO')
        concluidos = sum(1 for c in checklists_hoje if c.get('status') == 'CONCLUIDO')
        
        texto = (
            f"✅ **Checklists do Dia**\n\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"📊 **Resumo Geral:**\n"
            f"• Total: {total}\n"
            f"• 🟡 Pendentes: {pendentes}\n"
            f"• 🔵 Em andamento: {em_andamento}\n"
            f"• ✅ Concluídos: {concluidos}\n\n"
        )
        
        # Mostrar detalhes dos meus checklists
        meus_checklists = [c for c in checklists_hoje 
                          if c.get('responsavel_id') == operador.get('id')]
        
        if meus_checklists:
            texto += f"👤 **Meus Checklists ({len(meus_checklists)}):**\n"
            for checklist in meus_checklists:
                equipamento_nome = checklist.get('equipamento_nome', 'Equipamento')
                status = checklist.get('status', 'PENDENTE')
                status_emoji = {
                    'PENDENTE': '🟡',
                    'EM_ANDAMENTO': '🔵',
                    'CONCLUIDO': '✅'
                }.get(status, '❓')
                
                texto += f"  {status_emoji} {equipamento_nome} - {status}\n"
        else:
            texto += f"👤 **Você não possui checklists atribuídos hoje.**\n"
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Ver Meus Checklists", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="🔗 Acessar Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="checklist_menu")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao verificar checklists do dia: {e}")
        await message.answer("❌ Erro ao verificar checklists.")

async def mostrar_relatorios_checklist(message: Message, operador: dict):
    """Mostra relatórios do módulo checklist"""
    try:
        await message.answer(
            f"📊 **Relatórios de Checklist**\n\n"
            f"👤 Operador: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"🚧 **Em desenvolvimento**\n\n"
            f"Os relatórios detalhados serão implementados\n"
            f"em breve. Por enquanto, use:\n\n"
            f"• 📋 Meus Checklists - para ver seus checklists\n"
            f"• ✅ Checklist do Dia - para resumo do dia",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar relatórios: {e}")
        await message.answer("❌ Erro ao acessar relatórios.")

# ===============================================
# FUNÇÕES DE EQUIPAMENTO
# ===============================================

async def selecionar_equipamento(message: Message, equipamento_id: int, operador: dict):
    """Seleciona um equipamento e mostra opções de checklist"""
    try:
        # Buscar dados do equipamento
        equipamentos = await listar_equipamentos()
        equipamento = None
        for eq in equipamentos:
            if eq.get('id') == equipamento_id:
                equipamento = eq
                break
        
        if not equipamento:
            await message.answer("❌ Equipamento não encontrado.")
            return
        
        # Verificar se já existe checklist hoje
        checklist_hoje = await verificar_checklist_equipamento_hoje(equipamento_id)
        
        # Definir equipamento atual na sessão
        chat_id = str(message.chat.id)
        await definir_equipamento_atual(chat_id, equipamento)
        
        texto = (
            f"🚜 **Equipamento Selecionado**\n\n"
            f"📋 **{equipamento.get('nome')}**\n"
            f"🏷️ Código: {equipamento.get('codigo', 'N/A')}\n"
            f"📍 Status: {equipamento.get('status_operacional', 'N/A')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        )
        
        keyboard = []
        
        if checklist_hoje:
            status = checklist_hoje.get('status', 'PENDENTE')
            texto += f"📋 **Checklist de hoje:** {status}\n\n"
            
            if status == 'PENDENTE':
                keyboard.append([
                    InlineKeyboardButton(
                        text="▶️ Iniciar Checklist",
                        callback_data=f"executar_checklist_{checklist_hoje.get('id')}"
                    )
                ])
            elif status == 'EM_ANDAMENTO':
                keyboard.append([
                    InlineKeyboardButton(
                        text="🔍 Continuar Checklist",
                        callback_data=f"continuar_checklist_{checklist_hoje.get('id')}"
                    )
                ])
            elif status == 'CONCLUIDO':
                texto += "✅ **Checklist já foi concluído hoje!**\n\n"
        else:
            texto += "📋 **Nenhum checklist encontrado para hoje.**\n\n"
            keyboard.append([
                InlineKeyboardButton(
                    text="➕ Criar Novo Checklist",
                    callback_data=f"iniciar_checklist_{equipamento_id}"
                )
            ])
        
        keyboard.extend([
            [InlineKeyboardButton(text="🔗 Outros Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="🔙 Menu Checklist", callback_data="checklist_menu")]
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao selecionar equipamento: {e}")
        await message.answer("❌ Erro ao selecionar equipamento.")

# ===============================================
# FUNÇÕES DE EXECUÇÃO DO CHECKLIST
# ===============================================

async def iniciar_novo_checklist(message: Message, equipamento_id: int, operador: dict, state: FSMContext):
    """Inicia um novo checklist para o equipamento"""
    try:
        # Verificar se já existe checklist hoje
        checklist_hoje = await verificar_checklist_equipamento_hoje(equipamento_id)
        
        if checklist_hoje:
            await message.answer(
                f"⚠️ **Checklist já existe**\n\n"
                f"Já existe um checklist para este equipamento hoje:\n"
                f"Status: {checklist_hoje.get('status', 'PENDENTE')}\n\n"
                f"Use a opção 'Continuar' se necessário.",
                parse_mode='Markdown'
            )
            return
        
        # Criar novo checklist
        novo_checklist = await criar_checklist_nr12(
            equipamento_id=equipamento_id,
            responsavel_id=operador.get('id'),
            turno='MANHA'
        )
        
        if not novo_checklist:
            await message.answer("❌ Erro ao criar checklist. Tente novamente.")
            return
        
        await message.answer(
            f"✅ **Checklist Criado com Sucesso!**\n\n"
            f"📋 ID: {novo_checklist.get('id')}\n"
            f"🚜 Equipamento: {novo_checklist.get('equipamento_nome', 'N/A')}\n"
            f"👤 Responsável: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"🎯 **Iniciando execução...**",
            parse_mode='Markdown'
        )
        
        # Iniciar execução do checklist
        await executar_checklist(message, novo_checklist.get('id'), operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar novo checklist: {e}")
        await message.answer("❌ Erro ao criar novo checklist.")

async def continuar_checklist(message: Message, checklist_id: int, operador: dict, state: FSMContext):
    """Continua um checklist existente"""
    try:
        # Buscar dados do checklist
        checklists = await buscar_checklists_nr12()
        checklist = None
        for c in checklists:
            if c.get('id') == checklist_id:
                checklist = c
                break
        
        if not checklist:
            await message.answer("❌ Checklist não encontrado.")
            return
        
        if checklist.get('status') == 'CONCLUIDO':
            await message.answer("✅ Este checklist já foi concluído.")
            return
        
        await message.answer(
            f"🔍 **Continuando Checklist**\n\n"
            f"📋 ID: {checklist_id}\n"
            f"🚜 Equipamento: {checklist.get('equipamento_nome', 'N/A')}\n"
            f"📅 Data: {checklist.get('data_checklist', 'N/A')}\n\n"
            f"🎯 **Carregando itens...**",
            parse_mode='Markdown'
        )
        
        # Executar checklist
        await executar_checklist(message, checklist_id, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao continuar checklist: {e}")
        await message.answer("❌ Erro ao continuar checklist.")

async def executar_checklist(message: Message, checklist_id: int, operador: dict, state: FSMContext):
    """Executa um checklist mostrando os itens para verificação"""
    try:
        # Buscar itens do checklist
        itens = await buscar_itens_checklist_nr12(checklist_id)
        
        if not itens:
            await message.answer("❌ Nenhum item encontrado no checklist.")
            return
        
        # Salvar dados na sessão
        chat_id = str(message.chat.id)
        await definir_dados_temporarios(chat_id, 'checklist_id', checklist_id)
        await definir_dados_temporarios(chat_id, 'itens', itens)
        await definir_dados_temporarios(chat_id, 'item_atual', 0)
        await definir_dados_temporarios(chat_id, 'respostas', {})
        
        # Definir estado
        await state.set_state(ChecklistStates.executando_checklist)
        
        # Mostrar primeiro item
        await mostrar_proximo_item(message, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao executar checklist: {e}")
        await message.answer("❌ Erro ao executar checklist.")

def get_item_description(item):
    """Obtém a descrição do item baseado na estrutura real da API"""
    
    # Campo confirmado pela API: item_padrao_nome
    descricao = item.get('item_padrao_nome')
    if descricao and str(descricao).strip():
        return str(descricao).strip()
    
    # Fallback para outros campos
    fallback_fields = ['descricao', 'nome', 'titulo']
    for field in fallback_fields:
        value = item.get(field)
        if value and str(value).strip():
            return str(value).strip()
    
    # Último recurso
    return f"Item {item.get('id', 'N/A')}"

async def mostrar_proximo_item(message: Message, operador: dict, state: FSMContext):
    """Mostra o próximo item do checklist"""
    try:
        chat_id = str(message.chat.id)
        dados = await obter_dados_checklist(chat_id)
        
        if not dados:
            await message.answer("❌ Dados do checklist perdidos. Reinicie o processo.")
            await state.clear()
            return
        
        itens = dados.get('itens', [])
        item_atual = dados.get('item_atual', 0)
        
        if item_atual >= len(itens):
            # Checklist concluído
            await finalizar_checklist_completo(message, operador, state)
            return
        
        item = itens[item_atual]
        total_itens = len(itens)
        progresso = item_atual + 1
        
        # DEBUG: Log da estrutura do item
        logger.info(f"🔍 DEBUG - Item {progresso}: {item}")
        logger.info(f"🔍 DEBUG - Chaves disponíveis: {list(item.keys()) if isinstance(item, dict) else 'Não é dict'}")
        
        # DEBUG adicional para item_padrao
        if 'item_padrao' in item:
            logger.info(f"🔍 DEBUG - item_padrao: {item['item_padrao']}")
        
        # Obter descrição do item
        descricao = get_item_description(item)
        
        texto = (
            f"📋 **Checklist em Andamento**\n\n"
            f"📊 **Item {progresso}/{total_itens}**\n\n"
            f"🔍 **{descricao}**\n\n"
        )
        
        # Adicionar observações se existirem
        observacoes_fields = [
            'observacoes', 'observacao', 'obs', 
            ('item_padrao', 'observacoes'),
            ('item_padrao', 'observacao')
        ]
        
        for obs_field in observacoes_fields:
            obs_value = None
            if isinstance(obs_field, tuple):
                parent, child = obs_field
                parent_obj = item.get(parent)
                if isinstance(parent_obj, dict):
                    obs_value = parent_obj.get(child)
            else:
                obs_value = item.get(obs_field)
            
            if obs_value and str(obs_value).strip():
                texto += f"📝 *Observações: {str(obs_value).strip()}*\n\n"
                break
        
        texto += f"❓ **Este item está conforme?**"
        
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Conforme (OK)", callback_data=f"resposta_ok_{item.get('id')}"),
                InlineKeyboardButton(text="❌ Não Conforme (NOK)", callback_data=f"resposta_nok_{item.get('id')}")
            ],
            [
                InlineKeyboardButton(text="📝 Adicionar Observação", callback_data=f"resposta_obs_{item.get('id')}")
            ],
            [
                InlineKeyboardButton(text="⏸️ Pausar Checklist", callback_data="pausar_checklist"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar_checklist")
            ]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar próximo item: {e}")
        await message.answer("❌ Erro ao exibir item do checklist.")

async def processar_resposta_checklist(callback: CallbackQuery, operador: dict, state: FSMContext):
    """Processa a resposta do operador para um item do checklist"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Extrair dados do callback
        partes = data.split("_")
        if len(partes) < 3:
            await callback.answer("❌ Comando inválido")
            return
        
        resposta_tipo = partes[1]
        item_id = int(partes[2])
        
        dados = await obter_dados_checklist(chat_id)
        if not dados:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        # Processar resposta baseado no tipo
        if resposta_tipo == "obs":
            # Solicitar observação
            await callback.message.answer(
                f"📝 **Adicionar Observação**\n\n"
                f"Digite sua observação para este item:\n"
                f"(Digite /cancelar para voltar)",
                parse_mode='Markdown'
            )
            
            # Salvar ID do item atual para observação
            await definir_dados_temporarios(chat_id, 'item_observacao', item_id)
            await state.set_state(ChecklistStates.aguardando_observacao)
            return
        
        # Processar resposta OK/NOK
        status = 'OK' if resposta_tipo == 'ok' else 'NOK'
        
        # Atualizar item no backend
        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status=status,
            observacao="",
            responsavel_id=operador.get('id')
        )
        
        if not sucesso:
            await callback.message.answer("❌ Erro ao salvar resposta. Tente novamente.")
            return
        
        # Salvar resposta localmente
        respostas = dados.get('respostas', {})
        respostas[item_id] = {
            'status': status,
            'observacao': '',
            'timestamp': datetime.now().isoformat()
        }
        await definir_dados_temporarios(chat_id, 'respostas', respostas)
        
        # Avançar para próximo item
        item_atual = dados.get('item_atual', 0) + 1
        await definir_dados_temporarios(chat_id, 'item_atual', item_atual)
        
        # Feedback da resposta
        emoji = "✅" if status == 'OK' else "❌"
        await callback.message.answer(
            f"{emoji} **Resposta registrada: {status}**\n\n"
            f"🔄 Carregando próximo item...",
            parse_mode='Markdown'
        )
        
        # Mostrar próximo item
        await mostrar_proximo_item(callback.message, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao processar resposta: {e}")
        await callback.answer("❌ Erro interno")

async def processar_observacao_item(message: Message, state: FSMContext):
    """Processa observação digitada pelo operador"""
    try:
        if message.text.startswith('/cancelar'):
            await message.answer("❌ Observação cancelada.")
            await state.set_state(ChecklistStates.executando_checklist)
            return
        
        chat_id = str(message.chat.id)
        operador = await obter_operador_sessao(chat_id)
        
        if not operador:
            await message.answer("❌ Sessão expirada")
            await state.clear()
            return
        
        # Buscar item_observacao
        item_id = await obter_dados_temporarios(chat_id, 'item_observacao')
        if not item_id:
            await message.answer("❌ Erro: item não identificado")
            return
        
        observacao = message.text.strip()
        
        # Atualizar item com observação
        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status='PENDENTE',
            observacao=observacao,
            responsavel_id=operador.get('id')
        )
        
        if sucesso:
            await message.answer(
                f"📝 **Observação salva com sucesso!**\n\n"
                f"💬 *{observacao}*\n\n"
                f"🎯 Agora selecione o status do item:",
                parse_mode='Markdown'
            )
            
            # Voltar para seleção de status
            await state.set_state(ChecklistStates.executando_checklist)
            
            # Mostrar botões OK/NOK para o item atual
            keyboard = [
                [
                    InlineKeyboardButton(text="✅ Conforme (OK)", callback_data=f"resposta_ok_{item_id}"),
                    InlineKeyboardButton(text="❌ Não Conforme (NOK)", callback_data=f"resposta_nok_{item_id}")
                ]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await message.answer("❓ **Este item está conforme?**", reply_markup=markup)
            
        else:
            await message.answer("❌ Erro ao salvar observação. Tente novamente.")
        
    except Exception as e:
        logger.error(f"Erro ao processar observação: {e}")
        await message.answer("❌ Erro ao salvar observação.")

async def finalizar_checklist_completo(message: Message, operador: dict, state: FSMContext):
    """Finaliza o checklist e mostra resumo"""
    try:
        chat_id = str(message.chat.id)
        dados = await obter_dados_checklist(chat_id)
        
        if not dados:
            await message.answer("❌ Dados do checklist não encontrados.")
            return
        
        checklist_id = dados.get('checklist_id')
        respostas = dados.get('respostas', {})
        
        # Finalizar checklist no backend
        resultado = await finalizar_checklist_nr12(
            checklist_id=checklist_id,
            responsavel_id=operador.get('id')
        )
        
        if not resultado:
            await message.answer("❌ Erro ao finalizar checklist.")
            return
        
        # Calcular estatísticas
        total_itens = len(dados.get('itens', []))
        itens_ok = sum(1 for r in respostas.values() if r.get('status') == 'OK')
        itens_nok = sum(1 for r in respostas.values() if r.get('status') == 'NOK')
        
        # Determinar status geral
        if itens_nok == 0:
            status_geral = "✅ APROVADO"
            emoji_status = "🟢"
        else:
            status_geral = "⚠️ ATENÇÃO NECESSÁRIA"
            emoji_status = "🟡"
        
        texto = (
            f"🎉 **Checklist Finalizado!**\n\n"
            f"📋 **Resumo Final:**\n"
            f"🆔 ID: {checklist_id}\n"
            f"👤 Operador: {operador.get('nome')}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"📊 **Estatísticas:**\n"
            f"• Total de itens: {total_itens}\n"
            f"• ✅ Conformes: {itens_ok}\n"
            f"• ❌ Não conformes: {itens_nok}\n\n"
            f"{emoji_status} **Status: {status_geral}**\n\n"
        )
        
        if itens_nok > 0:
            texto += (
                f"⚠️ **Atenção:**\n"
                f"Foram encontrados {itens_nok} itens não conformes.\n"
                f"Providencie as correções necessárias.\n\n"
            )
        
        texto += f"💾 **Checklist salvo no sistema!**"
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="🔗 Outros Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
        # Limpar dados temporários
        await limpar_dados_temporarios(chat_id)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao finalizar checklist: {e}")
        await message.answer("❌ Erro ao finalizar checklist.")

async def salvar_checklist_final(callback: CallbackQuery, operador: dict, state: FSMContext):
    """Salva checklist final (callback alternativo)"""
    await callback.answer()
    await finalizar_checklist_completo(callback.message, operador, state)

# ===============================================
# HANDLERS DE COMANDO
# ===============================================

async def comando_checklist(message: Message, state: FSMContext):
    """Handler para comando /checklist"""
    chat_id = str(message.chat.id)
    operador = await obter_operador_sessao(chat_id)
    
    if not operador:
        await message.answer(
            "❌ **Acesso negado**\n\n"
            "Você precisa estar autenticado para usar o checklist.\n"
            "Use /start para fazer login."
        )
        return
    
    await checklist_menu_handler(message, operador)

# ===============================================
# HANDLERS DE ESTADO
# ===============================================

async def handle_observacao_state(message: Message, state: FSMContext):
    """Handler para estado de observação"""
    await processar_observacao_item(message, state)

async def handle_confirmacao_state(message: Message, state: FSMContext):
    """Handler para estado de confirmação"""
    if message.text.lower() in ['sim', 's', 'confirmar', 'ok']:
        chat_id = str(message.chat.id)
        operador = await obter_operador_sessao(chat_id)
        await finalizar_checklist_completo(message, operador, state)
    else:
        await message.answer(
            "❌ Finalização cancelada.\n"
            "Use os botões para continuar o checklist."
        )
        await state.set_state(ChecklistStates.executando_checklist)

# ===============================================
# CALLBACKS AUXILIARES
# ===============================================

async def callback_pausar_checklist(callback: CallbackQuery):
    """Callback para pausar checklist"""
    await callback.answer("⏸️ Checklist pausado. Use /checklist para continuar.")

async def callback_cancelar_checklist(callback: CallbackQuery):
    """Callback para cancelar checklist"""
    await callback.answer("❌ Checklist cancelado.")
    await callback.message.answer("Checklist cancelado. Use /checklist para recomeçar.")

# ===============================================
# FUNÇÃO DE REGISTRO DOS HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers do módulo checklist"""
    
    # Comando principal
    dp.message.register(comando_checklist, Command("checklist"))
    
    # Estados FSM
    dp.message.register(
        handle_observacao_state, 
        ChecklistStates.aguardando_observacao
    )
    dp.message.register(
        handle_confirmacao_state, 
        ChecklistStates.aguardando_confirmacao
    )
    
    # Callbacks principais
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
        F.data.startswith("executar_checklist_")
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
        F.data == "salvar_checklist"
    )
    
    # Callbacks de controle
    dp.callback_query.register(
        callback_pausar_checklist,
        F.data == "pausar_checklist"
    )
    dp.callback_query.register(
        callback_cancelar_checklist,
        F.data == "cancelar_checklist"
    )
    
    logger.info("✅ Handlers de checklist registrados com sucesso")

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

def validar_checklist_data(checklist_data: dict) -> bool:
    """Valida dados do checklist"""
    campos_obrigatorios = ['id', 'equipamento_nome', 'status']
    return all(campo in checklist_data for campo in campos_obrigatorios)

def formatar_status_checklist(status: str) -> str:
    """Formata status do checklist para exibição"""
    status_map = {
        'PENDENTE': '🟡 Pendente',
        'EM_ANDAMENTO': '🔵 Em Andamento', 
        'CONCLUIDO': '✅ Concluído',
        'CANCELADO': '❌ Cancelado'
    }
    return status_map.get(status, f'❓ {status}')