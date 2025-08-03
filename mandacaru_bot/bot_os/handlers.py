# ===============================================
# IMPLEMENTAÇÃO 5: Módulo de Ordens de Serviço
# mandacaru_bot/bot_os/handlers.py
# ===============================================

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.db import (
    listar_equipamentos,
    criar_ordem_servico,
    listar_tipos_manutencao,
    buscar_ordem_servico,
    atualizar_status_os,
    listar_ordens_servico_abertas
)
from core.session import (
    obter_operador_sessao, verificar_autenticacao,
    definir_dados_temporarios, obter_dados_temporarios,
    limpar_dados_temporarios
)

logger = logging.getLogger(__name__)

# ===============================================
# ESTADOS DA ORDEM DE SERVIÇO
# ===============================================

class OrdemServicoStates(StatesGroup):
    aguardando_equipamento = State()
    aguardando_tipo_problema = State()
    aguardando_descricao = State()
    aguardando_prioridade = State()
    confirmando_os = State()
    consultando_os = State()

# ===============================================
# HANDLER PRINCIPAL: Menu OS
# ===============================================

async def menu_ordem_servico(message: Message, state: FSMContext):
    """Menu principal das ordens de serviço"""
    try:
        chat_id = str(message.chat.id)
        
        # Verificar autenticação
        if not await verificar_autenticacao(chat_id):
            await message.answer(
                "❌ **Acesso negado**\n\n"
                "Faça login primeiro usando /start",
                parse_mode='Markdown'
            )
            return
        
        operador = await obter_operador_sessao(chat_id)
        
        # Buscar OSs abertas do operador
        os_abertas = await listar_ordens_servico_abertas(operador.get('id'))
        count_os = len(os_abertas) if os_abertas else 0
        
        keyboard = [
            [InlineKeyboardButton(text="🆕 Nova Ordem de Serviço", callback_data="os_nova")],
            [InlineKeyboardButton(text=f"📋 Minhas OS Abertas ({count_os})", callback_data="os_listar")],
            [InlineKeyboardButton(text="🔍 Consultar OS", callback_data="os_consultar")],
            [InlineKeyboardButton(text="❌ Voltar ao Menu", callback_data="os_voltar")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "🔧 **ORDENS DE SERVIÇO**\n\n"
            "📝 Gerencie manutenções e reparos dos equipamentos\n\n"
            "🔽 **Escolha uma opção:**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro no menu OS: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

# ===============================================
# HANDLER: Nova Ordem de Serviço
# ===============================================

async def iniciar_nova_os(callback: CallbackQuery, state: FSMContext):
    """Inicia criação de nova OS"""
    try:
        if callback.data == "os_voltar":
            await callback.message.answer("🔙 Voltando ao menu principal...")
            await state.clear()
            return
        
        await callback.answer("🆕 Criando nova OS...")
        
        chat_id = str(callback.message.chat.id)
        
        # Buscar equipamentos disponíveis
        equipamentos = await listar_equipamentos()
        
        if not equipamentos:
            await callback.message.answer(
                "❌ **Nenhum equipamento encontrado**\n\n"
                "Cadastre equipamentos no sistema antes de continuar."
            )
            return
        
        # Criar teclado com equipamentos
        keyboard = []
        for equipamento in equipamentos[:10]:  # Máximo 10 equipamentos
            nome = equipamento.get('nome', equipamento.get('numero_serie', 'N/A'))
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🚜 {nome}",
                    callback_data=f"os_equip_{equipamento.get('id')}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="❌ Cancelar", callback_data="os_cancelar")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.answer(
            "🚜 **Selecione o equipamento com problema:**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        await state.set_state(OrdemServicoStates.aguardando_equipamento)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar nova OS: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# HANDLER: Selecionar Equipamento
# ===============================================

async def selecionar_equipamento_os(callback: CallbackQuery, state: FSMContext):
    """Processa seleção do equipamento para OS"""
    try:
        if callback.data == "os_cancelar":
            await callback.message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        equipamento_id = int(callback.data.split('_')[2])
        chat_id = str(callback.message.chat.id)
        
        # Salvar equipamento selecionado
        await definir_dados_temporarios(chat_id, 'os_equipamento_id', equipamento_id)
        
        await callback.answer("✅ Equipamento selecionado")
        
        # Buscar tipos de problemas/manutenção
        tipos_manutencao = await listar_tipos_manutencao()
        
        if not tipos_manutencao:
            # Tipos padrão se não houver no sistema
            tipos_manutencao = [
                {'id': 1, 'nome': 'Manutenção Preventiva', 'codigo': 'PREV'},
                {'id': 2, 'nome': 'Manutenção Corretiva', 'codigo': 'CORR'},
                {'id': 3, 'nome': 'Problema Elétrico', 'codigo': 'ELET'},
                {'id': 4, 'nome': 'Problema Mecânico', 'codigo': 'MECA'},
                {'id': 5, 'nome': 'Problema Hidráulico', 'codigo': 'HIDR'},
                {'id': 6, 'nome': 'Outros', 'codigo': 'OUTR'}
            ]
        
        # Criar teclado com tipos
        keyboard = []
        for tipo in tipos_manutencao[:8]:  # Máximo 8 tipos
            emoji_map = {
                'PREV': '🔧', 'CORR': '⚠️', 'ELET': '⚡',
                'MECA': '🔩', 'HIDR': '💧', 'OUTR': '❓'
            }
            emoji = emoji_map.get(tipo.get('codigo', ''), '🔧')
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{emoji} {tipo.get('nome')}",
                    callback_data=f"os_tipo_{tipo.get('id')}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="❌ Cancelar", callback_data="os_cancelar")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.answer(
            "🔧 **Qual o tipo do problema/manutenção?**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        await state.set_state(OrdemServicoStates.aguardando_tipo_problema)
        
    except Exception as e:
        logger.error(f"Erro ao selecionar equipamento OS: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# HANDLER: Selecionar Tipo de Problema
# ===============================================

async def selecionar_tipo_problema(callback: CallbackQuery, state: FSMContext):
    """Processa seleção do tipo de problema"""
    try:
        if callback.data == "os_cancelar":
            await callback.message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        tipo_id = int(callback.data.split('_')[2])
        chat_id = str(callback.message.chat.id)
        
        # Salvar tipo selecionado
        await definir_dados_temporarios(chat_id, 'os_tipo_id', tipo_id)
        
        await callback.answer("✅ Tipo selecionado")
        
        await callback.message.answer(
            "📝 **Descreva o problema em detalhes:**\n\n"
            "💡 *Seja específico sobre:\n"
            "• O que está acontecendo\n"
            "• Quando começou\n"
            "• Sintomas observados\n"
            "• Qualquer ruído ou comportamento anormal*\n\n"
            "✍️ **Digite a descrição:**",
            parse_mode='Markdown'
        )
        
        await state.set_state(OrdemServicoStates.aguardando_descricao)
        
    except Exception as e:
        logger.error(f"Erro ao selecionar tipo: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# HANDLER: Processar Descrição
# ===============================================

async def processar_descricao_os(message: Message, state: FSMContext):
    """Processa descrição do problema digitada"""
    try:
        if message.text.startswith('/cancelar'):
            await message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        chat_id = str(message.chat.id)
        descricao = message.text.strip()
        
        if len(descricao) < 10:
            await message.answer(
                "❌ **Descrição muito curta**\n\n"
                "Por favor, forneça mais detalhes sobre o problema.\n"
                "Mínimo de 10 caracteres.\n\n"
                "Ou use /cancelar para cancelar."
            )
            return
        
        if len(descricao) > 1000:
            await message.answer(
                "❌ **Descrição muito longa**\n\n"
                "Máximo de 1000 caracteres.\n"
                "Seja mais conciso.\n\n"
                "Ou use /cancelar para cancelar."
            )
            return
        
        # Salvar descrição
        await definir_dados_temporarios(chat_id, 'os_descricao', descricao)
        
        # Perguntar sobre prioridade
        keyboard = [
            [InlineKeyboardButton(text="🔴 ALTA - Equipamento parado", callback_data="os_prio_ALTA")],
            [InlineKeyboardButton(text="🟡 MÉDIA - Funcionando com limitações", callback_data="os_prio_MEDIA")],
            [InlineKeyboardButton(text="🟢 BAIXA - Manutenção preventiva", callback_data="os_prio_BAIXA")],
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="os_cancelar")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "⚡ **Qual a prioridade desta OS?**\n\n"
            "🔴 **ALTA:** Equipamento parado ou com risco de segurança\n"
            "🟡 **MÉDIA:** Funcionando mas com problemas\n"
            "🟢 **BAIXA:** Manutenção preventiva ou melhorias\n\n"
            "🔽 **Escolha a prioridade:**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        await state.set_state(OrdemServicoStates.aguardando_prioridade)
        
    except Exception as e:
        logger.error(f"Erro ao processar descrição: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

# ===============================================
# HANDLER: Selecionar Prioridade
# ===============================================

async def selecionar_prioridade_os(callback: CallbackQuery, state: FSMContext):
    """Processa seleção da prioridade"""
    try:
        if callback.data == "os_cancelar":
            await callback.message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        prioridade = callback.data.split('_')[2]
        chat_id = str(callback.message.chat.id)
        
        # Salvar prioridade
        await definir_dados_temporarios(chat_id, 'os_prioridade', prioridade)
        
        await callback.answer("✅ Prioridade definida")
        
        # Mostrar confirmação
        await mostrar_confirmacao_os(callback.message, state)
        
    except Exception as e:
        logger.error(f"Erro ao selecionar prioridade: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# FUNÇÃO: Mostrar Confirmação da OS
# ===============================================

async def mostrar_confirmacao_os(message: Message, state: FSMContext):
    """Mostra resumo da OS e pede confirmação"""
    try:
        chat_id = str(message.chat.id)
        
        # Buscar dados salvos
        equipamento_id = await obter_dados_temporarios(chat_id, 'os_equipamento_id')
        tipo_id = await obter_dados_temporarios(chat_id, 'os_tipo_id')
        descricao = await obter_dados_temporarios(chat_id, 'os_descricao')
        prioridade = await obter_dados_temporarios(chat_id, 'os_prioridade')
        
        # Buscar detalhes
        equipamentos = await listar_equipamentos()
        equipamento = next((e for e in equipamentos if e.get('id') == equipamento_id), None)
        
        tipos_manutencao = await listar_tipos_manutencao()
        if not tipos_manutencao:
            tipos_manutencao = [
                {'id': 1, 'nome': 'Manutenção Preventiva'},
                {'id': 2, 'nome': 'Manutenção Corretiva'},
                {'id': 3, 'nome': 'Problema Elétrico'},
                {'id': 4, 'nome': 'Problema Mecânico'},
                {'id': 5, 'nome': 'Problema Hidráulico'},
                {'id': 6, 'nome': 'Outros'}
            ]
        
        tipo = next((t for t in tipos_manutencao if t.get('id') == tipo_id), None)
        
        if not equipamento or not tipo:
            await message.answer("❌ Erro ao carregar dados. Tente novamente.")
            await state.clear()
            return
        
        # Mapear emojis de prioridade
        emoji_prioridade = {
            'ALTA': '🔴 ALTA',
            'MEDIA': '🟡 MÉDIA', 
            'BAIXA': '🟢 BAIXA'
        }
        
        # Montar resumo
        resumo = (
            f"🔧 **CONFIRMAÇÃO DA ORDEM DE SERVIÇO**\n\n"
            f"🚜 **Equipamento:** {equipamento.get('nome', 'N/A')}\n"
            f"🆔 **Série:** {equipamento.get('numero_serie', 'N/A')}\n\n"
            f"🔧 **Tipo:** {tipo.get('nome', 'N/A')}\n"
            f"⚡ **Prioridade:** {emoji_prioridade.get(prioridade, prioridade)}\n\n"
            f"📝 **Descrição:**\n"
            f"_{descricao}_\n\n"
            f"✅ **Confirmar criação da OS?**"
        )
        
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Confirmar", callback_data="os_confirmar"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data="os_cancelar")
            ]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            resumo,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        await state.set_state(OrdemServicoStates.confirmando_os)
        
    except Exception as e:
        logger.error(f"Erro ao mostrar confirmação OS: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

# ===============================================
# HANDLER: Confirmar Criação da OS
# ===============================================

async def confirmar_criacao_os(callback: CallbackQuery, state: FSMContext):
    """Confirma e cria a ordem de serviço"""
    try:
        if callback.data == "os_cancelar":
            await callback.message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        chat_id = str(callback.message.chat.id)
        operador = await obter_operador_sessao(chat_id)
        
        await callback.answer("🔄 Criando ordem de serviço...")
        
        # Buscar dados da OS
        equipamento_id = await obter_dados_temporarios(chat_id, 'os_equipamento_id')
        tipo_id = await obter_dados_temporarios(chat_id, 'os_tipo_id')
        descricao = await obter_dados_temporarios(chat_id, 'os_descricao')
        prioridade = await obter_dados_temporarios(chat_id, 'os_prioridade')
        
        # Dados para criar na API
        dados_os = {
            'equipamento_id': equipamento_id,
            'tipo_manutencao_id': tipo_id,
            'descricao_problema': descricao,
            'prioridade': prioridade,
            'solicitante_id': operador.get('id'),
            'data_abertura': datetime.now().isoformat(),
            'status': 'ABERTA',
            'origem': 'BOT_TELEGRAM'
        }
        
        # Criar OS na API
        resultado = await criar_ordem_servico(dados_os)
        
        if resultado and resultado.get('success'):
            os_id = resultado.get('ordem_servico_id')
            os_numero = resultado.get('numero_os', os_id)
            
            await callback.message.answer(
                f"✅ **ORDEM DE SERVIÇO CRIADA COM SUCESSO!**\n\n"
                f"🆔 **Número:** #{os_numero}\n"
                f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                f"👤 **Solicitante:** {operador.get('nome')}\n"
                f"📊 **Status:** ABERTA\n\n"
                f"🔔 **A equipe de manutenção foi notificada**\n\n"
                f"📋 Use /consultar_os {os_numero} para acompanhar",
                parse_mode='Markdown'
            )
            
            # Limpar dados temporários
            await limpar_dados_temporarios(chat_id, 'os_equipamento_id')
            await limpar_dados_temporarios(chat_id, 'os_tipo_id')
            await limpar_dados_temporarios(chat_id, 'os_descricao')
            await limpar_dados_temporarios(chat_id, 'os_prioridade')
            
        else:
            await callback.message.answer(
                f"❌ **ERRO AO CRIAR ORDEM DE SERVIÇO**\n\n"
                f"Motivo: {resultado.get('error', 'Erro desconhecido')}\n\n"
                f"Tente novamente ou contate o administrador."
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao confirmar criação OS: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# HANDLER: Listar OS Abertas
# ===============================================

async def listar_os_abertas(callback: CallbackQuery, state: FSMContext):
    """Lista ordens de serviço abertas do operador"""
    try:
        await callback.answer("📋 Carregando suas OS...")
        
        chat_id = str(callback.message.chat.id)
        operador = await obter_operador_sessao(chat_id)
        
        # Buscar OSs abertas
        os_abertas = await listar_ordens_servico_abertas(operador.get('id'))
        
        if not os_abertas:
            await callback.message.answer(
                "📭 **Nenhuma OS aberta encontrada**\n\n"
                "Você não possui ordens de serviço abertas no momento."
            )
            return
        
        # Montar lista de OSs
        texto = "📋 **SUAS ORDENS DE SERVIÇO ABERTAS**\n\n"
        
        keyboard = []
        for os in os_abertas[:5]:  # Máximo 5 OSs
            numero = os.get('numero_os', os.get('id'))
            status = os.get('status', 'ABERTA')
            prioridade = os.get('prioridade', 'MEDIA')
            
            # Emoji por prioridade
            emoji_prio = {'ALTA': '🔴', 'MEDIA': '🟡', 'BAIXA': '🟢'}.get(prioridade, '⚪')
            
            # Emoji por status
            emoji_status = {
                'ABERTA': '🆕', 'EM_ANDAMENTO': '🔄', 
                'AGUARDANDO_PECA': '⏳', 'PAUSADA': '⏸️'
            }.get(status, '📋')
            
            texto += f"{emoji_prio} **OS #{numero}**\n"
            texto += f"   {emoji_status} {status}\n"
            texto += f"   🚜 {os.get('equipamento_nome', 'N/A')}\n\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"👁️ Ver OS #{numero}",
                    callback_data=f"os_ver_{os.get('id')}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar", callback_data="os_menu")
        ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.answer(
            texto,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar OS: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# FUNÇÕES DA API (core/db.py) - ORDEM DE SERVIÇO
# ===============================================

async def listar_tipos_manutencao():
    """Lista tipos de manutenção disponíveis"""
    try:
        url = f"{API_BASE_URL}/tipos-manutencao/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                tipos = data.get('results', [])
                logger.info(f"Encontrados {len(tipos)} tipos de manutenção")
                return tipos
            else:
                logger.error(f"Erro ao buscar tipos de manutenção: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar tipos de manutenção: {e}")
        return []

async def criar_ordem_servico(dados: Dict):
    """Cria ordem de serviço na API"""
    try:
        url = f"{API_BASE_URL}/ordens-servico/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=dados)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Erro ao criar OS: {response.status_code}")
                return {'success': False, 'error': f'Erro HTTP {response.status_code}'}
                
    except Exception as e:
        logger.error(f"Erro ao criar OS: {e}")
        return {'success': False, 'error': str(e)}

async def listar_ordens_servico_abertas(operador_id: int):
    """Lista OSs abertas de um operador"""
    try:
        url = f"{API_BASE_URL}/ordens-servico/"
        params = {
            'solicitante_id': operador_id,
            'status': 'ABERTA,EM_ANDAMENTO,AGUARDANDO_PECA'
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Erro ao listar OS: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao listar OS: {e}")
        return []

async def buscar_ordem_servico(os_id: int):
    """Busca detalhes de uma OS específica"""
    try:
        url = f"{API_BASE_URL}/ordens-servico/{os_id}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao buscar OS: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao buscar OS: {e}")
        return None

# ===============================================
# HANDLERS PARA REGISTRAR NO DISPATCHER
# ===============================================

def registrar_handlers_os(dp: Dispatcher):
    """Registra todos os handlers do módulo de OS"""
    
    # Handler principal
    dp.message.register(
        menu_ordem_servico,
        F.text == "🔧 Ordem de Serviço"
    )
    
    # Callbacks do menu
    dp.callback_query.register(
        iniciar_nova_os,
        F.data.in_(["os_nova", "os_voltar"])
    )
    
    dp.callback_query.register(
        listar_os_abertas,
        F.data == "os_listar"
    )
    
    # Callbacks de criação de OS
    dp.callback_query.register(
        selecionar_equipamento_os,
        F.data.startswith("os_equip_"),
        OrdemServicoStates.aguardando_equipamento
    )
    
    dp.callback_query.register(
        selecionar_tipo_problema,
        F.data.startswith("os_tipo_"),
        OrdemServicoStates.aguardando_tipo_problema
    )
    
    dp.callback_query.register(
        selecionar_prioridade_os,
        F.data.startswith("os_prio_"),
        OrdemServicoStates.aguardando_prioridade
    )
    
    dp.callback_query.register(
        confirmar_criacao_os,
        F.data.in_(["os_confirmar", "os_cancelar"]),
        OrdemServicoStates.confirmando_os
    )
    
    # Estados
    dp.message.register(
        processar_descricao_os,
        OrdemServicoStates.aguardando_descricao
    )