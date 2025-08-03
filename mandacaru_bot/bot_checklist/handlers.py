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

from core.db import (
    # Funções NR12 reais
    buscar_checklists_nr12, criar_checklist_nr12,
    buscar_itens_checklist_nr12, atualizar_item_checklist_nr12_com_operador,  # NOVA FUNÇÃO
    finalizar_checklist_nr12, buscar_equipamentos_com_nr12,
    verificar_checklist_equipamento_hoje, buscar_checklists_operador_hoje,
    buscar_itens_padrao_nr12,
    # Funções gerais
    listar_equipamentos
)
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

def criar_menu_principal():
    """Menu principal CORRIGIDO - sem underscores"""
    keyboard = [
        [InlineKeyboardButton(text="📋 Checklist", callback_data="menu-checklist")],
        [InlineKeyboardButton(text="⛽ Abastecimento", callback_data="menu-abastecimento")],
        [InlineKeyboardButton(text="🔧 Ordem de Serviço", callback_data="menu-os")],
        [InlineKeyboardButton(text="💰 Financeiro", callback_data="menu-financeiro")],
        [InlineKeyboardButton(text="📱 QR Code", callback_data="menu-qrcode")],
        [InlineKeyboardButton(text="❓ Ajuda", callback_data="menu-ajuda")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def criar_menu_equipamento(equipamento_id: int):
    """Menu de equipamento CORRIGIDO - sem underscores"""
    keyboard = [
        [InlineKeyboardButton(text="📋 Novo Checklist NR12", callback_data=f"eq-novo-checklist-{equipamento_id}")],
        [InlineKeyboardButton(text="⛽ Registrar Abastecimento", callback_data=f"eq-abastecimento-{equipamento_id}")],
        [InlineKeyboardButton(text="🔧 Abrir Ordem de Serviço", callback_data=f"eq-os-{equipamento_id}")],
        [InlineKeyboardButton(text="⏱️ Atualizar Horímetro", callback_data=f"eq-horimetro-{equipamento_id}")],
        [InlineKeyboardButton(text="📊 Ver Histórico", callback_data=f"eq-historico-{equipamento_id}")],
        [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu-principal")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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
            
        )
        
    except Exception as e:
        logger.error(f"Erro no menu de checklist: {e}")
        await message.answer("❌ Erro interno no módulo checklist.")

async def checklist_callback_handler(callback: CallbackQuery, operador: dict, state: FSMContext):
    """Handler corrigido para callbacks de checklist - SEM underscores"""
    try:
        data = callback.data
        await callback.answer()
        
        # ✅ CORREÇÃO: Usar hífen em vez de underscore
        if data.startswith("equipamento-"):
            equipamento_id = int(data.split("-")[-1])
            await selecionar_equipamento(callback.message, equipamento_id, operador)
            
        elif data.startswith("iniciar-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await iniciar_novo_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("continuar-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await continuar_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("executar-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await executar_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("resposta-"):
            await processar_resposta_checklist(callback, operador, state)
            
        elif data == "finalizar-checklist":
            await finalizar_checklist_completo(callback.message, operador, state)
            
        elif data == "salvar-checklist":
            await salvar_checklist_final(callback, operador, state)
            
    except Exception as e:
        logger.error(f"Erro no callback de checklist: {e}")
        await callback.answer("❌ Erro interno")
# ===============================================
# FUNÇÕES DE NAVEGAÇÃO
# ===============================================

async def mostrar_meus_equipamentos(message: Message, operador: dict):
    """
    NOVA FUNÇÃO: Mostra equipamentos do operador com resumo de checklists
    """
    try:
        operador_id = operador.get('id')
        
        # Buscar todos os checklists do operador (últimos 30 dias)
        checklists = await buscar_checklists_nr12(operador_id=operador_id)
        
        if not checklists:
            await message.answer(
                f"🔧 **Meus Equipamentos**\n\n"
                f"❌ Nenhum equipamento encontrado para você.\n\n"
                f"👤 Operador: {operador.get('nome')}\n\n"
                f"💡 Entre em contato com o supervisor para\n"
                f"configurar seus equipamentos autorizados.",
                parse_mode='Markdown'
            )
            return
        
        # Agrupar checklists por equipamento
        equipamentos_resumo = {}
        
        for checklist in checklists:
            equipamento_id = checklist.get('equipamento')
            equipamento_nome = checklist.get('equipamento_nome', 'Sem nome')
            status = checklist.get('status', 'PENDENTE')
            data_checklist = checklist.get('data_checklist', '')
            
            if equipamento_id not in equipamentos_resumo:
                equipamentos_resumo[equipamento_id] = {
                    'nome': equipamento_nome,
                    'checklists': [],
                    'pendentes': 0,
                    'em_andamento': 0,
                    'concluidos': 0,
                    'ultimo_checklist': None
                }
            
            # Adicionar checklist ao equipamento
            equipamentos_resumo[equipamento_id]['checklists'].append(checklist)
            
            # Contar por status
            if status == 'PENDENTE':
                equipamentos_resumo[equipamento_id]['pendentes'] += 1
            elif status == 'EM_ANDAMENTO':
                equipamentos_resumo[equipamento_id]['em_andamento'] += 1
            elif status == 'CONCLUIDO':
                equipamentos_resumo[equipamento_id]['concluidos'] += 1
            
            # Encontrar último checklist (mais recente)
            if not equipamentos_resumo[equipamento_id]['ultimo_checklist']:
                equipamentos_resumo[equipamento_id]['ultimo_checklist'] = data_checklist
            elif data_checklist > equipamentos_resumo[equipamento_id]['ultimo_checklist']:
                equipamentos_resumo[equipamento_id]['ultimo_checklist'] = data_checklist
        
        # Montar mensagem
        total_equipamentos = len(equipamentos_resumo)
        texto = f"🔧 **Meus Equipamentos ({total_equipamentos})**\n\n"
        keyboard = []
        
        for equipamento_id, resumo in equipamentos_resumo.items():
            nome = resumo['nome']
            pendentes = resumo['pendentes']
            em_andamento = resumo['em_andamento']
            concluidos = resumo['concluidos']
            ultimo = resumo['ultimo_checklist']
            
            # Ícone do equipamento baseado no status
            if em_andamento > 0:
                icone = "🔵"
                status_text = f"{em_andamento} em andamento"
            elif pendentes > 0:
                icone = "🟡"
                status_text = f"{pendentes} pendente(s)"
            else:
                icone = "✅"
                status_text = "Em dia"
            
            # Formatação da data
            try:
                from datetime import datetime
                ultimo_formatado = datetime.strptime(ultimo, '%Y-%m-%d').strftime('%d/%m') if ultimo else 'N/A'
            except:
                ultimo_formatado = ultimo or 'N/A'
            
            texto += f"{icone} **{nome}**\n"
            texto += f"   📊 {status_text}\n"
            texto += f"   📅 Último: {ultimo_formatado}\n"
            if concluidos > 0:
                texto += f"   ✅ {concluidos} concluído(s)\n"
            texto += "\n"
            
            # Botão para ver checklists do equipamento
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🔍 Ver {nome} ({pendentes + em_andamento})",
                    callback_data=f"ver-equipamento-{equipamento_id}"
                )
            ])
        
        # Botão de voltar
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="checklist-menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao mostrar equipamentos: {e}")
        await message.answer("❌ Erro ao carregar equipamentos")

#============================


async def verificar_e_criar_checklist_hoje(equipamento_id: int, operador_id: int):
    """
    Verifica se existe checklist de hoje, se não existir, cria um
    """
    try:
        from datetime import date
        hoje = date.today().strftime('%Y-%m-%d')
        
        # Buscar checklist de hoje para este equipamento
        checklists_hoje = await buscar_checklists_nr12(
            equipamento_id=equipamento_id,
            data_checklist=hoje
        )
        
        if not checklists_hoje:
            logger.info(f"🔄 Criando checklist de hoje para equipamento {equipamento_id}")
            
            # Criar checklist do dia
            novo_checklist = await criar_checklist_nr12(
                equipamento_id=equipamento_id,
                responsavel_id=operador_id,
                turno="MANHA"
            )
            
            if novo_checklist:
                logger.info(f"✅ Checklist criado: ID {novo_checklist.get('id')}")
                return novo_checklist
            else:
                logger.error(f"❌ Falha ao criar checklist para equipamento {equipamento_id}")
        
        return checklists_hoje[0] if checklists_hoje else None
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar/criar checklist: {e}")
        return None

#============================


async def mostrar_checklists_equipamento(message: Message, equipamento_id: int, operador: dict):
    """
    Mostra checklists do equipamento com criação automática do dia
    """
    try:
        operador_id = operador.get('id')
        
        # 1. VERIFICAR/CRIAR CHECKLIST DE HOJE
        checklist_hoje = await verificar_e_criar_checklist_hoje(equipamento_id, operador_id)
        
        # 2. BUSCAR TODOS OS CHECKLISTS DO EQUIPAMENTO
        checklists = await buscar_checklists_nr12(
            operador_id=operador_id,
            equipamento_id=equipamento_id
        )
        
        if not checklists:
            await message.answer("❌ Nenhum checklist encontrado para este equipamento")
            return
        
        equipamento_nome = checklists[0].get('equipamento_nome', f'Equipamento {equipamento_id}')
        
        # 3. SEPARAR POR DATA
        from datetime import date
        hoje = date.today().strftime('%Y-%m-%d')
        
        checklists_hoje = [c for c in checklists if c.get('data_checklist') == hoje]
        checklists_historico = [c for c in checklists if c.get('data_checklist') != hoje]
        
        # 4. MONTAR MENSAGEM
        texto = f"🚜 **{equipamento_nome}**\n\n"
        keyboard = []
        
        # ✅ CHECKLISTS DE HOJE
        if checklists_hoje:
            texto += f"📅 **Hoje ({hoje.split('-')[2]}/{hoje.split('-')[1]}):**\n"
            
            for checklist in checklists_hoje:
                status = checklist.get('status', 'PENDENTE')
                turno = checklist.get('turno', 'MANHA')
                checklist_id = checklist.get('id')
                percentual = checklist.get('percentual_conclusao', 0)
                
                if status == 'PENDENTE':
                    status_icon = '🟡'
                    status_text = 'Pendente'
                    botao_text = f"▶️ Iniciar {turno}"
                    callback = f"iniciar-checklist-{checklist_id}"
                elif status == 'EM_ANDAMENTO':
                    status_icon = '🔵'
                    status_text = f'Em Andamento ({percentual:.0f}%)'
                    botao_text = f"🔍 Continuar {turno}"
                    callback = f"continuar-checklist-{checklist_id}"
                else:  # CONCLUIDO
                    status_icon = '✅'
                    status_text = 'Concluído'
                    botao_text = f"📋 Ver {turno}"
                    callback = f"ver-checklist-{checklist_id}"
                
                texto += f"   {status_icon} **{turno}**: {status_text}\n"
                
                # ADICIONAR BOTÃO
                keyboard.append([
                    InlineKeyboardButton(text=botao_text, callback_data=callback)
                ])
            
            texto += "\n"
        else:
            # 5. SE NÃO TEM CHECKLIST DE HOJE, OFERECER CRIAR
            texto += f"📅 **Hoje ({hoje.split('-')[2]}/{hoje.split('-')[1]}):** Nenhum checklist encontrado\n\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    text="➕ Criar Checklist de Hoje", 
                    callback_data=f"criar-checklist-hoje-{equipamento_id}"
                )
            ])
        
        # 6. HISTÓRICO
        if checklists_historico:
            texto += "📊 **Histórico Recente:**\n"
            for checklist in checklists_historico[:5]:
                data = checklist.get('data_checklist', '')
                turno = checklist.get('turno', 'MANHA')
                status = checklist.get('status', 'PENDENTE')
                percentual = checklist.get('percentual_conclusao', 0)
                
                try:
                    from datetime import datetime
                    data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m')
                except:
                    data_formatada = data
                
                if status == 'CONCLUIDO':
                    status_icon = '✅'
                elif status == 'EM_ANDAMENTO':
                    status_icon = f'🔵 ({percentual:.0f}%)'
                else:
                    status_icon = '🟡'
                
                texto += f"   {status_icon} {data_formatada} - {turno}\n"
            
            if len(checklists_historico) > 5:
                texto += f"   📋 +{len(checklists_historico) - 5} checklists anteriores\n"
        
        # 7. ESTATÍSTICAS
        total_pendentes = sum(1 for c in checklists if c.get('status') == 'PENDENTE')
        total_andamento = sum(1 for c in checklists if c.get('status') == 'EM_ANDAMENTO')
        total_concluidos = sum(1 for c in checklists if c.get('status') == 'CONCLUIDO')
        
        texto += f"\n📊 **Resumo:** {total_pendentes} pendentes, {total_andamento} em andamento, {total_concluidos} concluídos\n"
        
        # 8. NAVEGAÇÃO
        keyboard.append([
            InlineKeyboardButton(text="🔙 Meus Equipamentos", callback_data="checklist-equipamentos"),
            InlineKeyboardButton(text="🏠 Menu Principal", callback_data="checklist-menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar checklists do equipamento {equipamento_id}: {e}")
        await message.answer(f"❌ Erro ao carregar equipamento: {e}")

# ===================================================================
# 2. INICIAR CHECKLIST
# ===================================================================

async def iniciar_checklist_handler(callback: CallbackQuery, checklist_id: int, operador: dict, state: FSMContext):
    """Inicia um checklist PENDENTE"""
    try:
        # Chamar API para iniciar checklist
        from core.db import iniciar_checklist_nr12
        
        resultado = await iniciar_checklist_nr12(checklist_id, operador.get('id'))
        
        if not resultado:
            await callback.message.answer("❌ Erro ao iniciar checklist")
            return
        
        await callback.answer("✅ Checklist iniciado!")
        
        await callback.message.answer(
            f"✅ Checklist Iniciado!\n\n"
            f"📋 ID: {checklist_id}\n"
            f"👤 Responsável: {operador.get('nome')}\n\n"
            f"🎯 Carregando primeiro item..."
        )
        
        # Começar execução
        await executar_checklist(callback.message, checklist_id, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar checklist: {e}")
        await callback.answer("❌ Erro ao iniciar")

# ===================================================================
# 3. CONTINUAR CHECKLIST
# ===================================================================

async def continuar_checklist_handler(callback: CallbackQuery, checklist_id: int, operador: dict, state: FSMContext):
    """Continua um checklist EM_ANDAMENTO"""
    try:
        await callback.answer("🔍 Continuando checklist...")
        
        await callback.message.answer(
            f"🔍 Continuando Checklist\n\n"
            f"📋 ID: {checklist_id}\n"
            f"👤 Operador: {operador.get('nome')}\n\n"
            f"🎯 Carregando próximo item..."
        )
        
        # Continuar execução
        await executar_checklist(callback.message, checklist_id, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao continuar checklist: {e}")
        await callback.answer("❌ Erro ao continuar")

# ===================================================================
# 4. EXECUTAR CHECKLIST - Função Principal
# ===================================================================

async def executar_checklist(message: Message, checklist_id: int, operador: dict, state: FSMContext):
    """Executa checklist mostrando itens um por um"""
    try:
        # Buscar itens do checklist
        from core.db import buscar_itens_checklist_nr12
        
        itens = await buscar_itens_checklist_nr12(checklist_id)
        
        if not itens:
            await message.answer("❌ Nenhum item encontrado no checklist")
            return
        
        # Encontrar primeiro item PENDENTE
        item_atual = None
        item_index = 0
        
        for i, item in enumerate(itens):
            if item.get('status') == 'PENDENTE':
                item_atual = item
                item_index = i
                break
        
        if not item_atual:
            # Todos os itens já foram verificados
            await message.answer(
                "✅ Todos os itens foram verificados!\n\n"
                "📋 Pronto para finalizar o checklist."
            )
            await finalizar_checklist_prompt(message, checklist_id, operador, state)
            return
        
        # Salvar dados na sessão
        chat_id = str(message.chat.id)
        await definir_dados_temporarios(chat_id, 'checklist_id', checklist_id)
        await definir_dados_temporarios(chat_id, 'itens', itens)
        await definir_dados_temporarios(chat_id, 'item_atual', item_index)
        
        # Mostrar item atual
        await mostrar_item_checklist(message, item_atual, item_index + 1, len(itens), state)
        
    except Exception as e:
        logger.error(f"Erro ao executar checklist: {e}")
        await message.answer("❌ Erro ao executar checklist")

# ===================================================================
# 5. MOSTRAR ITEM DO CHECKLIST
# ===================================================================

async def mostrar_item_checklist(message: Message, item: dict, numero: int, total: int, state: FSMContext):
    """Mostra um item específico do checklist para verificação"""
    try:
        # Extrair dados do item
        item_id = item.get('id')
        descricao = item.get('item_padrao_nome', 'Item sem descrição')
        criticidade = item.get('criticidade', 'MEDIA')
        permite_na = item.get('permite_na', True)
        
        # Montar texto
        texto = f"📋 Item {numero}/{total}\n\n"
        texto += f"🔍 {descricao}\n\n"
        
        if criticidade == 'ALTA':
            texto += "⚠️ Item CRÍTICO\n\n"
        elif criticidade == 'MEDIA':
            texto += "🔸 Item Importante\n\n"
        
        texto += "❓ Este item está conforme?"
        
        # Montar teclado
        keyboard = [
            [
                InlineKeyboardButton(text="✅ OK", callback_data=f"resposta_ok_{item_id}"),
                InlineKeyboardButton(text="❌ NOK", callback_data=f"resposta_nok_{item_id}")
            ]
        ]
        
        if permite_na:
            keyboard.append([
                InlineKeyboardButton(text="➖ N/A", callback_data=f"resposta_na_{item_id}")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton(text="📝 Observação", callback_data=f"obs_{item_id}")],
            [
                InlineKeyboardButton(text="⏸️ Pausar", callback_data="pausar_checklist"),
                InlineKeyboardButton(text="🏁 Finalizar", callback_data="finalizar_checklist")
            ]
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup)
        
        # Definir estado
        await state.set_state(ChecklistStates.executando_checklist)
        
    except Exception as e:
        logger.error(f"Erro ao mostrar item: {e}")
        await message.answer("❌ Erro ao exibir item")

# ===================================================================
# 6. PROCESSAR RESPOSTAS (OK/NOK/NA)
# ===================================================================

async def processar_resposta_item(callback: CallbackQuery, operador: dict, state: FSMContext):
    """Processa resposta do operador para um item"""
    try:
        data = callback.data
        partes = data.split("_")
        
        if len(partes) < 3:
            await callback.answer("❌ Comando inválido")
            return
        
        acao = partes[1]  # ok, nok, na
        item_id = int(partes[2])
        
        # Mapear ação para status
        status_map = {
            'ok': 'OK',
            'nok': 'NOK', 
            'na': 'NA'
        }
        
        status = status_map.get(acao)
        if not status:
            await callback.answer("❌ Ação inválida")
            return
        
        # Atualizar item via API
        from core.db import atualizar_item_checklist_nr12
        
        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status=status,
            observacao="",
            responsavel_id=operador.get('nome')  # ✅ CORRETO
        )
        
        if not sucesso:
            await callback.answer("❌ Erro ao salvar")
            return
        
        await callback.answer(f"✅ Marcado como {status}")
        
        # Ir para próximo item
        await proximo_item_checklist(callback.message, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao processar resposta: {e}")
        await callback.answer("❌ Erro interno")

# ===================================================================
# 7. PRÓXIMO ITEM
# ===================================================================

async def proximo_item_checklist(message: Message, operador: dict, state: FSMContext):
    """Avança para o próximo item do checklist"""
    try:
        chat_id = str(message.chat.id)
        
        # Buscar dados da sessão
        checklist_id = await obter_dados_temporarios(chat_id, 'checklist_id')
        itens = await obter_dados_temporarios(chat_id, 'itens', [])
        item_atual = await obter_dados_temporarios(chat_id, 'item_atual', 0)
        
        if not checklist_id or not itens:
            await message.answer("❌ Sessão perdida. Reinicie o checklist.")
            await state.clear()
            return
        
        # Buscar próximo item PENDENTE
        proximo_item = None
        proximo_index = item_atual + 1
        
        # Re-buscar itens atualizados da API
        from core.db import buscar_itens_checklist_nr12
        itens_atualizados = await buscar_itens_checklist_nr12(checklist_id)
        
        for i in range(len(itens_atualizados)):
            if itens_atualizados[i].get('status') == 'PENDENTE':
                proximo_item = itens_atualizados[i]
                proximo_index = i
                break
        
        if proximo_item:
            # Atualizar índice na sessão
            await definir_dados_temporarios(chat_id, 'item_atual', proximo_index)
            await definir_dados_temporarios(chat_id, 'itens', itens_atualizados)
            
            # Mostrar próximo item
            await mostrar_item_checklist(
                message, 
                proximo_item, 
                proximo_index + 1, 
                len(itens_atualizados), 
                state
            )
        else:
            # Todos os itens foram verificados
            await message.answer(
                "🎉 Todos os itens verificados!\n\n"
                "✅ Checklist pronto para finalização."
            )
            await finalizar_checklist_prompt(message, checklist_id, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao avançar item: {e}")
        await message.answer("❌ Erro ao avançar")

# ===================================================================
# 8. FINALIZAR CHECKLIST
# ===================================================================

async def finalizar_checklist_prompt(message: Message, checklist_id: int, operador: dict, state: FSMContext):
    """Pergunta se quer finalizar o checklist"""
    try:
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Finalizar Checklist", callback_data=f"confirmar_finalizar_{checklist_id}"),
                InlineKeyboardButton(text="📋 Revisar Itens", callback_data=f"revisar_checklist_{checklist_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Voltar", callback_data="checklist_menu")
            ]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "🏁 Checklist Pronto para Finalização\n\n"
            "Todos os itens foram verificados.\n"
            "Deseja finalizar o checklist?",
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Erro ao finalizar prompt: {e}")
        await message.answer("❌ Erro ao finalizar")

async def finalizar_checklist_definitivo(callback: CallbackQuery, checklist_id: int, operador: dict, state: FSMContext):
    """Finaliza o checklist definitivamente"""
    try:
        # Chamar API para finalizar
        from core.db import finalizar_checklist_nr12
        
        resultado = await finalizar_checklist_nr12(checklist_id)
        
        if not resultado:
            await callback.answer("❌ Erro ao finalizar")
            return
        
        await callback.answer("✅ Checklist finalizado!")
        
        # Calcular estatísticas
        estatisticas = resultado.get('estatisticas', {})
        total = estatisticas.get('total_itens', 0)
        ok = estatisticas.get('itens_ok', 0)
        nok = estatisticas.get('itens_nok', 0)
        na = estatisticas.get('itens_na', 0)
        
        texto = f"🎉 Checklist Finalizado!\n\n"
        texto += f"📋 ID: {checklist_id}\n"
        texto += f"👤 Operador: {operador.get('nome')}\n\n"
        texto += f"📊 Resumo:\n"
        texto += f"• Total: {total} itens\n"
        texto += f"• ✅ OK: {ok}\n"
        texto += f"• ❌ NOK: {nok}\n"
        texto += f"• ➖ N/A: {na}\n\n"
        
        if nok > 0:
            texto += "⚠️ Itens não conformes detectados!\n"
            texto += "Providencie as correções necessárias.\n\n"
        else:
            texto += "✅ Todos os itens estão conformes!\n\n"
        
        texto += "💾 Checklist salvo no sistema."
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await callback.message.answer(texto, reply_markup=markup)
        
        # Limpar sessão
        chat_id = str(callback.from_user.id)
        await limpar_dados_temporarios(chat_id)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao finalizar definitivo: {e}")
        await callback.answer("❌ Erro ao finalizar")

# ===================================================================
# 9. ATUALIZAR HANDLER DE CALLBACKS
# ===================================================================

async def handle_checklist_callback(callback: CallbackQuery, state: FSMContext):
    """Handler atualizado com novo fluxo de equipamentos - CORRIGIDO"""
    try:
        # ✅ DEFINIR data NO INÍCIO
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Log para debug
        logger.info(f"🔍 Callback recebido: {data}")
        
        # Verificar autenticação
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        # ✅ CALLBACKS PARA EQUIPAMENTOS
        if data == "checklist_equipamentos":
            await mostrar_meus_equipamentos(callback.message, operador)
            
        elif data.startswith("ver-equipamento-"):
            equipamento_id = int(data.split("-")[-1])
            logger.info(f"🚜 Acessando equipamento ID: {equipamento_id}")
            await mostrar_checklists_equipamento(callback.message, equipamento_id, operador)
        
        # ✅ CALLBACKS EXISTENTES
        elif data == "checklist_meus":
            await mostrar_meus_equipamentos(callback.message, operador)
            
        elif data == "checklist_hoje":
            await verificar_checklist_hoje(callback.message, operador)
            
        elif data == "checklist_relatorios":
            await mostrar_relatorios_checklist(callback.message, operador)
            
        elif data.startswith("iniciar-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await iniciar_novo_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("continuar-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await continuar_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("ver-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await callback.message.answer(f"📋 Visualizando checklist {checklist_id}")
            
        elif data.startswith("executar-checklist-"):
            checklist_id = int(data.split("-")[-1])
            await executar_checklist(callback.message, checklist_id, operador, state)
            
        elif data.startswith("resposta-"):
            await processar_resposta_checklist(callback, operador, state)
            
        elif data == "finalizar-checklist":
            await finalizar_checklist_completo(callback.message, operador, state)
            
        elif data == "salvar-checklist":
            await salvar_checklist_final(callback, operador, state)
        elif data == "checklist-equipamentos":
            await mostrar_meus_equipamentos(callback.message, operador)
            
        elif data == "checklist-menu":
            # Voltar ao menu principal do checklist
            await checklist_menu_handler(callback.message, operador)

        elif data.startswith("criar-checklist-hoje-"):
            equipamento_id = int(data.split("-")[-1])
            logger.info(f"🔄 Criando checklist de hoje para equipamento {equipamento_id}")
            
            checklist = await verificar_e_criar_checklist_hoje(equipamento_id, operador.get('id'))
            
            if checklist:
                await callback.message.answer(
                    f"✅ **Checklist criado com sucesso!**\n\n"
                    f"🆔 ID: {checklist.get('id')}\n"
                    f"📅 Data: {checklist.get('data_checklist')}\n"
                    f"🕐 Turno: {checklist.get('turno', 'MANHA')}\n\n"
                    f"Agora você pode iniciar o checklist.",
                    parse_mode='Markdown'
                )
                # Recarregar a tela do equipamento
                await mostrar_checklists_equipamento(callback.message, equipamento_id, operador)
            else:
                await callback.message.answer("❌ Erro ao criar checklist. Tente novamente.")

        
        else:
            logger.warning(f"⚠️ Callback não reconhecido: {data}")
            await callback.answer("❓ Ação não reconhecida")
            
    except Exception as e:
        logger.error(f"❌ Erro no callback de checklist: {e}")
        await callback.answer("❌ Erro interno")



# ===================================================================
# 10. REGISTRAR NOVOS HANDLERS
# ===================================================================

def register_handlers(dp: Dispatcher):
    """Registra handlers corrigidos - CAPTURA TODOS OS CALLBACKS"""
    
    # 🔍 CALLBACK GERAL - CAPTURA QUALQUER COISA QUE COMECE COM:
    # - checklist
    # - ver-
    # - iniciar-
    # - continuar-
    # - resposta-
    # - finalizar
    # - salvar
    
    @dp.callback_query()
    async def handle_all_checklist_callbacks(callback: CallbackQuery, state: FSMContext):
        """Handler que captura TODOS os callbacks relacionados a checklist"""
        data = callback.data
        
        # Log para debug
        logger.info(f"🔍 HANDLER GERAL - Callback: '{data}'")
        
        # Verificar se é relacionado ao checklist
        if (data.startswith("checklist") or 
            data.startswith("ver-") or 
            data.startswith("iniciar-") or 
            data.startswith("continuar-") or 
            data.startswith("resposta-") or 
            data in ["finalizar-checklist", "salvar-checklist", "pausar-checklist"]):
            
            logger.info(f"✅ Callback relacionado ao checklist, processando...")
            await handle_checklist_callback(callback, state)
        else:
            logger.info(f"❌ Callback NÃO relacionado ao checklist, ignorando...")
    
    logger.info("✅ Handler geral de callbacks registrado")
# ===================================================================
# OUTRAS FUNÇÕES QUE TAMBÉM PRECISAM SER CORRIGIDAS
# ===================================================================

async def mostrar_equipamentos_checklist(message: Message, operador: dict):
    """Mostra equipamentos disponíveis para checklist - VERSÃO CORRIGIDA"""
    try:
        # Buscar equipamentos com NR12 configurado
        equipamentos = await buscar_equipamentos_com_nr12()
        
        if not equipamentos:
            await message.answer(
                "🔗 Equipamentos NR12\n\n"
                "❌ Nenhum equipamento encontrado\n\n"
                "Os equipamentos precisam ter NR12 configurado\n"
                "para aparecer nesta lista.\n\n"
                "💬 Entre em contato com o administrador."
                # CORREÇÃO: REMOVIDO 
            )
            return
        
        # CORREÇÃO: Formatação simples
        texto = f"🔗 Equipamentos NR12 Disponíveis\n\n"
        texto += f"👤 Operador: {operador.get('nome')}\n"
        texto += f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        texto += f"🎯 Selecione um equipamento:\n\n"
        
        keyboard = []
        for equipamento in equipamentos[:10]:  # Limitar a 10
            nome = equipamento.get('nome', 'Sem nome')
            status = equipamento.get('status_operacional', 'DESCONHECIDO')
            
            status_emoji = {
                'DISPONIVEL': '🟢',
                'EM_USO': '🔵',
                'MANUTENCAO': '🔧',
                'INATIVO': '❌'
            }.get(status, '❓')
            
            # CORREÇÃO: Formatação simples sem **
            texto += f"{status_emoji} {nome} - {status}\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📋 {nome[:25]}",  # Limitar tamanho
                    callback_data=f"selecionar_eq_{equipamento.get('id')}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="checklist_menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # CORREÇÃO: REMOVIDO 
        await message.answer(texto, reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Erro ao mostrar equipamentos: {e}")
        await message.answer("❌ Erro ao buscar equipamentos.")

async def verificar_checklist_hoje(message: Message, operador: dict):
    """Verifica status dos checklists do dia - VERSÃO CORRIGIDA"""
    try:
        # Buscar todos os checklists de hoje
        hoje = date.today().isoformat()
        checklists_hoje = await buscar_checklists_nr12(data_checklist=hoje)
        
        if not checklists_hoje:
            await message.answer(
                f"✅ Checklists do Dia\n\n"
                f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
                f"📊 Nenhum checklist programado para hoje.\n\n"
                f"💡 Os checklists são criados automaticamente\n"
                f"ou podem ser iniciados manualmente."
                # CORREÇÃO: REMOVIDO 
            )
            return
        
        # Contar por status
        total = len(checklists_hoje)
        pendentes = sum(1 for c in checklists_hoje if c.get('status') == 'PENDENTE')
        em_andamento = sum(1 for c in checklists_hoje if c.get('status') == 'EM_ANDAMENTO')
        concluidos = sum(1 for c in checklists_hoje if c.get('status') == 'CONCLUIDO')
        
        # CORREÇÃO: Formatação simples
        texto = f"✅ Checklists do Dia\n\n"
        texto += f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        texto += f"📊 Resumo Geral:\n"
        texto += f"• Total: {total}\n"
        texto += f"• 🟡 Pendentes: {pendentes}\n"
        texto += f"• 🔵 Em andamento: {em_andamento}\n"
        texto += f"• ✅ Concluídos: {concluidos}\n\n"
        
        # Mostrar detalhes dos meus checklists
        meus_checklists = [c for c in checklists_hoje 
                          if c.get('responsavel_id') == operador.get('id')]
        
        if meus_checklists:
            texto += f"👤 Meus Checklists ({len(meus_checklists)}):\n"
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
            texto += f"👤 Você não possui checklists atribuídos hoje.\n"
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Ver Meus Checklists", callback_data="checklist_meus")],
            [InlineKeyboardButton(text="🔗 Acessar Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="🔙 Voltar ao Menu", callback_data="checklist_menu")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # CORREÇÃO: REMOVIDO 
        await message.answer(texto, reply_markup=markup)
        
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
        await message.answer(texto, reply_markup=markup)
        
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
        await message.answer(texto, reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Erro ao mostrar próximo item: {e}")
        await message.answer("❌ Erro ao exibir item do checklist.")

# ===============================================
# FUNÇÃO CORRIGIDA: processar_resposta_checklist
# ===============================================

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
                
            )
            
            # Salvar ID do item atual para observação
            await definir_dados_temporarios(chat_id, 'item_observacao', item_id)
            await state.set_state(ChecklistStates.aguardando_observacao)
            return
        
        # Processar resposta OK/NOK
        status = 'OK' if resposta_tipo == 'ok' else 'NOK'
        
        # CORREÇÃO: Usar função com operador real
        sucesso = await atualizar_item_checklist_nr12_com_operador(
            item_id=item_id,
            status=status,
            chat_id=chat_id,  # Passar chat_id para buscar operador
            observacao=""
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
            
        )
        
        # Mostrar próximo item
        await mostrar_proximo_item(callback.message, operador, state)
        
    except Exception as e:
        logger.error(f"Erro ao processar resposta: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# FUNÇÃO CORRIGIDA: processar_observacao_item
# ===============================================

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
        
        # CORREÇÃO: Usar função com operador real - só observação
        sucesso = await atualizar_item_checklist_nr12_com_operador(
            item_id=item_id,
            status='PENDENTE',  # Manter status atual
            chat_id=chat_id,
            observacao=observacao
        )
        
        if sucesso:
            await message.answer(
                f"📝 **Observação salva com sucesso!**\n\n"
                f"💬 *{observacao}*\n\n"
                f"✅ Agora marque este item como conforme ou não conforme.",
                
            )
            
            # Limpar dados temporários de observação
            await definir_dados_temporarios(chat_id, 'item_observacao', None)
            await state.set_state(ChecklistStates.executando_checklist)
            
            # Reexibir o item atual para marcar
            dados = await obter_dados_checklist(chat_id)
            if dados:
                await mostrar_proximo_item(message, operador, state)
        else:
            await message.answer("❌ Erro ao salvar observação. Tente novamente.")
    
    except Exception as e:
        logger.error(f"Erro ao processar observação: {e}")
        await message.answer("❌ Erro interno ao salvar observação.")

# ===============================================
# HANDLER PARA OBSERVAÇÃO
# ===============================================

async def handle_observacao_state(message: Message, state: FSMContext):
    """Handler para capturar observações"""
    chat_id = str(message.from_user.id)
    operador = await obter_operador_sessao(chat_id)
    
    if not operador:
        await message.answer("❌ Sessão expirada")
        await state.clear()
        return
    
    await processar_observacao_item(message, state)

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
            [InlineKeyboardButton(text="🔧 Meus Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="🔗 Outros Equipamentos", callback_data="checklist_equipamentos")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(texto, reply_markup=markup)
        
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
    """Registra handlers corrigidos - CAPTURA TODOS OS CALLBACKS"""
    
    # 🔍 CALLBACK GERAL - CAPTURA QUALQUER COISA QUE COMECE COM:
    # - checklist
    # - ver-
    # - iniciar-
    # - continuar-
    # - resposta-
    # - finalizar
    # - salvar
    
    @dp.callback_query()
    async def handle_all_checklist_callbacks(callback: CallbackQuery, state: FSMContext):
        """Handler que captura TODOS os callbacks relacionados a checklist"""
        data = callback.data
        
        # Log para debug
        logger.info(f"🔍 HANDLER GERAL - Callback: '{data}'")
        
        # Verificar se é relacionado ao checklist
        if (data.startswith("checklist") or 
            data.startswith("ver-") or 
            data.startswith("iniciar-") or 
            data.startswith("continuar-") or 
            data.startswith("resposta-") or 
            data in ["finalizar-checklist", "salvar-checklist", "pausar-checklist"]):
            
            logger.info(f"✅ Callback relacionado ao checklist, processando...")
            await handle_checklist_callback(callback, state)
        else:
            logger.info(f"❌ Callback NÃO relacionado ao checklist, ignorando...")
    
    logger.info("✅ Handler geral de callbacks registrado")

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
    """Formata status de checklist de forma segura para Telegram"""
    status_map = {
        'PENDENTE': '🟡 Pendente',
        'EM_ANDAMENTO': '🔵 Em Andamento',
        'CONCLUIDO': '✅ Concluído', 
        'CANCELADO': '❌ Cancelado',
        'FALHA': '🔴 Com Falha'
    }
    return status_map.get(status.upper(), status.replace('_', ' ').title())

def formatar_status_equipamento(status: str) -> str:
    """Formata status de equipamento de forma segura"""
    status_map = {
        'DISPONIVEL': '✅ Disponível',
        'EM_USO': '🔄 Em Uso',
        'MANUTENCAO': '🔧 Manutenção',
        'QUEBRADO': '🔴 Quebrado',
        'INATIVO': '❌ Inativo'
    }
    return status_map.get(status.upper(), status.replace('_', ' ').title())

def callback_data_seguro(data: str) -> str:
    """
    Garante que callback_data seja seguro para Telegram
    Remove/substitui caracteres problemáticos
    """
    # Substituir underscores por hífens
    data = data.replace('_', '-')
    
    # Remover caracteres especiais que podem quebrar markdown
    caracteres_problematicos = ['*', '`', '[', ']', '(', ')', '~', '>', '#', '+', '=', '|', '{', '}', '.', '!']
    for char in caracteres_problematicos:
        data = data.replace(char, '')
    
    # Limitar tamanho (Telegram tem limite de 64 bytes)
    if len(data.encode('utf-8')) > 64:
        data = data[:60] + "..."
    
    return data