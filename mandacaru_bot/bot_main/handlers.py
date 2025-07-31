# ===============================================
# ARQUIVO CORRIGIDO: mandacaru_bot/bot_main/handlers.py
# Handlers principais com fluxos completos
# ===============================================

import logging
import re
from datetime import datetime, date
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional

# Imports do core
from core.config import API_BASE_URL, API_TIMEOUT
from core.session import (
    iniciar_sessao, obter_sessao, atualizar_sessao, 
    limpar_sessao, obter_operador_sessao, verificar_autenticacao,
    definir_equipamento_atual, obter_equipamento_atual,
    definir_dados_temporarios, obter_dados_temporarios
)
from core.db import (
    buscar_operador_por_nome, 
    buscar_operador_por_chat_id,
    buscar_equipamento_por_uuid,
    atualizar_chat_id_operador,
    registrar_abastecimento,
    criar_ordem_servico
)
from core.templates import MessageTemplates
from core.utils import Validators

logger = logging.getLogger(__name__)

# ===============================================
# DEFINIÇÃO DE ESTADOS FSM
# ===============================================

class AuthStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()

class EquipmentStates(StatesGroup):
    waiting_for_fuel_quantity = State()
    waiting_for_fuel_value = State()
    waiting_for_horimeter = State()
    waiting_for_os_description = State()

# ===============================================
# HANDLERS DE COMANDO PRINCIPAL
# ===============================================

async def start_handler(message: Message, state: FSMContext):
    """Handler principal do comando /start"""
    try:
        comando = message.text.strip()
        chat_id = str(message.chat.id)
        
        # Verificar se é um QR code: /start eq_{uuid}
        match = re.match(r'/start eq_([a-f0-9\-]{36})', comando)
        
        if match:
            # Processar QR code de equipamento
            await handle_qr_code_start(message, state)
            return
        
        # Comando /start normal
        await process_normal_start(message, state)
        
    except Exception as e:
        logger.error(f"Erro no start_handler: {e}")
        await message.answer(
            "❌ Erro interno. Tente novamente em alguns instantes.",
            reply_markup=ReplyKeyboardRemove()
        )

async def process_normal_start(message: Message, state: FSMContext):
    """Processa /start normal (sem QR code)"""
    try:
        chat_id = str(message.chat.id)
        
        # Verificar se usuário já está registrado
        operador_registrado = await buscar_operador_por_chat_id(chat_id)
        
        if operador_registrado:
            # Login automático
            await iniciar_sessao(chat_id, operador_registrado, 'AUTENTICADO')
            await show_main_menu(message, operador_registrado)
            return
        
        # Não registrado - iniciar processo de login
        await message.answer(
            MessageTemplates.welcome_template(),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        
        await message.answer(
            "👤 **Informe seu nome completo:**",
            parse_mode="Markdown"
        )
        
        await state.set_state(AuthStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"Erro no process_normal_start: {e}")
        await message.answer("❌ Erro no processo de autenticação.")

async def handle_qr_code_start(message: Message, state: FSMContext):
    """Handler para QR codes: /start eq_{uuid}"""
    try:
        comando = message.text.strip()
        chat_id = str(message.chat.id)
        
        # Extrair UUID do comando
        match = re.match(r'/start eq_([a-f0-9\-]{36})', comando)
        if not match:
            await process_normal_start(message, state)
            return
            
        uuid_equipamento = match.group(1)
        
        # Buscar equipamento na API
        equipamento_data = await buscar_equipamento_por_uuid(uuid_equipamento)
        
        if not equipamento_data:
            await message.answer(
                "❌ **Equipamento Não Encontrado**\n\n"
                "O QR Code escaneado não corresponde a nenhum equipamento válido.",
                parse_mode='Markdown'
            )
            return
        
        # Verificar se usuário está autenticado
        operador = await obter_operador_sessao(chat_id)
        
        if operador:
            # Usuário já logado - ir direto para menu do equipamento
            await definir_equipamento_atual(chat_id, equipamento_data)
            await mostrar_menu_equipamento(message, equipamento_data, operador)
            return
        
        # Verificar se chat_id está registrado no banco
        operador_banco = await buscar_operador_por_chat_id(chat_id)
        
        if operador_banco:
            # LOGIN AUTOMÁTICO para QR code
            await iniciar_sessao(chat_id, operador_banco, 'AUTENTICADO')
            await definir_equipamento_atual(chat_id, equipamento_data)
            
            await message.answer(
                f"👋 **Bem-vindo de volta, {operador_banco.get('nome')}!**\n\n"
                f"🚜 Acessando equipamento **{equipamento_data.get('nome')}**...",
                parse_mode='Markdown'
            )
            
            await mostrar_menu_equipamento(message, equipamento_data, operador_banco)
            return
        
        # Não registrado - pedir login mas guardar contexto do equipamento
        await definir_dados_temporarios(chat_id, 'equipamento_qr_uuid', uuid_equipamento)
        await definir_dados_temporarios(chat_id, 'equipamento_qr_data', equipamento_data)
        
        await message.answer(
            f"📱 **QR Code: {equipamento_data.get('nome', 'Equipamento')}**\n\n"
            "🔐 Para acessar este equipamento, primeiro faça seu login.\n\n"
            "👤 **Informe seu nome completo:**",
            parse_mode='Markdown'
        )
        
        await state.set_state(AuthStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"Erro no QR Code: {e}")
        await message.answer(
            f"❌ **Erro no QR Code**\n\n"
            f"Ocorreu um erro: {str(e)}",
            parse_mode='Markdown'
        )

# ===============================================
# HANDLERS DE AUTENTICAÇÃO
# ===============================================

async def process_name(message: Message, state: FSMContext):
    """Processa nome informado pelo usuário"""
    try:
        nome = message.text.strip()
        chat_id = str(message.chat.id)
        
        if not Validators.validar_nome(nome):
            await message.answer(
                "❌ Nome inválido. Informe seu nome completo (mínimo 3 caracteres):"
            )
            return
        
        # Buscar operadores com esse nome
        operadores = await buscar_operador_por_nome(nome)
        
        if not operadores:
            await message.answer(
                f"❌ **Operador não encontrado**\n\n"
                f"Não foi encontrado nenhum operador com o nome '{nome}'.\n\n"
                f"Verifique se o nome está correto ou entre em contato com o administrador."
            )
            await state.clear()
            return
        
        if len(operadores) == 1:
            # Apenas um operador encontrado
            operador = operadores[0]
            await definir_dados_temporarios(chat_id, 'operador_candidato', operador)
            
            await message.answer(
                f"👤 **Operador encontrado:**\n"
                f"📋 Nome: {operador.get('nome')}\n"
                f"💼 Função: {operador.get('funcao', 'N/A')}\n\n"
                f"📅 **Informe sua data de nascimento** (DD/MM/AAAA):",
                parse_mode='Markdown'
            )
            
            await state.set_state(AuthStates.waiting_for_birth_date)
        else:
            # Múltiplos operadores - mostrar lista para seleção
            keyboard = []
            for operador in operadores[:5]:  # Máximo 5 opções
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"{operador.get('nome')} - {operador.get('funcao', 'N/A')}",
                        callback_data=f"select_operator_{operador.get('id')}"
                    )
                ])
            
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            await message.answer(
                f"👥 **Múltiplos operadores encontrados**\n\n"
                f"Selecione seu perfil:",
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
            # Guardar lista de operadores
            await definir_dados_temporarios(chat_id, 'operadores_candidatos', operadores)
        
    except Exception as e:
        logger.error(f"Erro ao processar nome: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

async def process_birth_date(message: Message, state: FSMContext):
    """Processa data de nascimento para autenticação"""
    try:
        data_texto = message.text.strip()
        chat_id = str(message.chat.id)
        
        # Validar formato da data
        data_nascimento = Validators.validar_data_nascimento(data_texto)
        if not data_nascimento:
            await message.answer(
                "❌ Data inválida. Use o formato DD/MM/AAAA (ex: 15/03/1990):"
            )
            return
        
        # Buscar operador candidato
        operador = await obter_dados_temporarios(chat_id, 'operador_candidato')
        if not operador:
            await message.answer("❌ Erro na sessão. Digite /start para recomeçar.")
            await state.clear()
            return
        
        # Verificar data de nascimento
        data_banco_str = operador.get('data_nascimento')
        if not data_banco_str:
            await message.answer(
                "❌ **Data de nascimento não cadastrada**\n\n"
                "Entre em contato com o administrador para regularizar seu cadastro."
            )
            await state.clear()
            return
        
        # Comparar datas
        try:
            data_banco = datetime.strptime(data_banco_str, '%Y-%m-%d').date()
        except:
            data_banco = datetime.strptime(data_banco_str, '%d/%m/%Y').date()
        
        if data_nascimento != data_banco:
            await message.answer(
                "❌ **Data de nascimento incorreta**\n\n"
                "A data informada não confere com nossos registros."
            )
            await state.clear()
            return
        
        # Autenticação bem-sucedida
        await complete_authentication(message, state, operador)
        
    except Exception as e:
        logger.error(f"Erro ao processar data de nascimento: {e}")
        await message.answer("❌ Erro na autenticação. Tente novamente.")

async def complete_authentication(message: Message, state: FSMContext, operador: dict):
    """Completa o processo de autenticação"""
    try:
        chat_id = str(message.chat.id)
        
        # Atualizar chat_id no banco de dados
        operador_id = operador.get('id')
        await atualizar_chat_id_operador(operador_id, chat_id)
        
        # Iniciar sessão
        await iniciar_sessao(chat_id, operador, 'AUTENTICADO')
        
        # Verificar se veio de QR code
        equipamento_qr = await obter_dados_temporarios(chat_id, 'equipamento_qr_data')
        
        if equipamento_qr:
            # Definir equipamento atual e ir para menu específico
            await definir_equipamento_atual(chat_id, equipamento_qr)
            
            await message.answer(
                f"✅ **Login realizado com sucesso!**\n\n"
                f"👋 Bem-vindo, {operador['nome']}!\n\n"
                f"🚜 Acessando equipamento **{equipamento_qr.get('nome')}**...",
                parse_mode='Markdown'
            )
            await mostrar_menu_equipamento(message, equipamento_qr, operador)
        else:
            # Mostrar menu principal
            await show_main_menu(message, operador)
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro no processo de autenticação: {e}")
        await message.answer(
            "❌ Erro na autenticação. Não foi possível completar o login."
        )
        await state.clear()

# ===============================================
# HANDLERS DE CALLBACK
# ===============================================

async def handle_operator_selection(callback: CallbackQuery, state: FSMContext):
    """Handler para seleção de operador quando há múltiplos"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Extrair ID do operador
        match = re.match(r'select_operator_(\d+)', data)
        if not match:
            await callback.answer("❌ Erro na seleção")
            return
        
        operador_id = int(match.group(1))
        
        # Buscar operador na lista de candidatos
        operadores_candidatos = await obter_dados_temporarios(chat_id, 'operadores_candidatos', [])
        operador = next((op for op in operadores_candidatos if op.get('id') == operador_id), None)
        
        if not operador:
            await callback.answer("❌ Operador não encontrado")
            return
        
        await callback.answer()
        await definir_dados_temporarios(chat_id, 'operador_candidato', operador)
        
        await callback.message.answer(
            f"👤 **Operador selecionado:**\n"
            f"📋 Nome: {operador.get('nome')}\n"
            f"💼 Função: {operador.get('funcao', 'N/A')}\n\n"
            f"📅 **Informe sua data de nascimento** (DD/MM/AAAA):",
            parse_mode='Markdown'
        )
        
        await state.set_state(AuthStates.waiting_for_birth_date)
        
    except Exception as e:
        logger.error(f"Erro na seleção de operador: {e}")
        await callback.answer("❌ Erro interno")

async def handle_menu_callback(callback: CallbackQuery):
    """Handler para callbacks do menu principal"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await callback.answer("❌ Sessão expirada. Digite /start")
            return
        
        await callback.answer()
        
        if data == "menu_checklist":
            await show_checklist_menu(callback.message, operador)
            
        elif data == "menu_abastecimento":
            await show_abastecimento_menu(callback.message, operador)
            
        elif data == "menu_os":
            await show_os_menu(callback.message, operador)
            
        elif data == "menu_financeiro":
            await show_financeiro_menu(callback.message, operador)
            
        elif data == "menu_qrcode":
            await show_qrcode_menu(callback.message, operador)
            
        elif data == "menu_principal":
            await show_main_menu(callback.message, operador)
            
        elif data == "menu_ajuda":
            await show_help_menu(callback.message)
            
        else:
            await callback.message.answer(
                f"🚧 **{data.replace('menu_', '').title()}**\n\n"
                "Este módulo está em desenvolvimento.\n"
                "Em breve estará disponível!",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Erro no callback de menu: {e}")
        await callback.answer("❌ Erro interno")

async def handle_equipamento_callback(callback: CallbackQuery, state: FSMContext):
    """Handler para callbacks de ações do equipamento"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        # Extrair ID do equipamento e ação
        if data.startswith("eq_"):
            parts = data.split("_", 2)
            if len(parts) >= 3:
                acao = parts[1]
                equipamento_id = parts[2]
            else:
                await callback.message.answer("❌ Comando inválido")
                return
            
            if acao == "novo" and "checklist" in data:
                # Novo checklist
                await iniciar_novo_checklist(callback.message, equipamento_id, operador)
                
            elif acao == "abastecimento":
                # Registrar abastecimento
                await iniciar_abastecimento(callback.message, state, equipamento_id, operador)
                
            elif acao == "os":
                # Abrir OS
                await iniciar_ordem_servico(callback.message, state, equipamento_id, operador)
                
            elif acao == "horimetro":
                # Atualizar horímetro
                await iniciar_atualizacao_horimetro(callback.message, state, equipamento_id, operador)
                
            elif acao == "historico":
                # Ver histórico
                await mostrar_historico_equipamento(callback.message, equipamento_id, operador)
        
        elif data.startswith("cancelar_"):
            # Cancelar operação
            await callback.message.answer("❌ Operação cancelada.")
            await state.clear()
            
    except Exception as e:
        logger.error(f"Erro no callback de equipamento: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# MENUS E NAVEGAÇÃO
# ===============================================

def criar_menu_principal():
    """Cria o menu principal do bot"""
    keyboard = [
        [InlineKeyboardButton(text="📋 Checklist", callback_data="menu_checklist")],
        [InlineKeyboardButton(text="⛽ Abastecimento", callback_data="menu_abastecimento")],
        [InlineKeyboardButton(text="🔧 Ordem de Serviço", callback_data="menu_os")],
        [InlineKeyboardButton(text="💰 Financeiro", callback_data="menu_financeiro")],
        [InlineKeyboardButton(text="📱 QR Code", callback_data="menu_qrcode")],
        [InlineKeyboardButton(text="❓ Ajuda", callback_data="menu_ajuda")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def show_main_menu(message: Message, operador: dict):
    """Mostra o menu principal após autenticação"""
    keyboard = criar_menu_principal()
    
    is_admin = operador.get('is_admin', False)
    admin_text = "\n\n🔑 *Você tem privilégios de administrador!*\nUse /admin para acessar o painel." if is_admin else ""
    
    await message.answer(
        f"✅ **Login realizado com sucesso!**\n\n"
        f"👤 Operador: {operador['nome']}\n"
        f"💼 Função: {operador.get('funcao', 'Operador')}\n"
        f"🕐 Horário: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        f"{admin_text}\n\n"
        f"Escolha uma opção abaixo:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def mostrar_menu_equipamento(message: Message, equipamento_data: dict, operador: dict):
    """Mostra menu de ações para o equipamento"""
    try:
        equipamento_id = equipamento_data.get('id')
        nome = equipamento_data.get('nome', 'Equipamento')
        horimetro = equipamento_data.get('horimetro_atual', 0)
        status = equipamento_data.get('status_operacional', 'Desconhecido')
        
        # Criar menu
        keyboard = [
            [InlineKeyboardButton(text="📋 Novo Checklist NR12", callback_data=f"eq_novo_checklist_{equipamento_id}")],
            [InlineKeyboardButton(text="⛽ Registrar Abastecimento", callback_data=f"eq_abastecimento_{equipamento_id}")],
            [InlineKeyboardButton(text="🔧 Abrir Ordem de Serviço", callback_data=f"eq_os_{equipamento_id}")],
            [InlineKeyboardButton(text="⏱️ Atualizar Horímetro", callback_data=f"eq_horimetro_{equipamento_id}")],
            [InlineKeyboardButton(text="📊 Ver Histórico", callback_data=f"eq_historico_{equipamento_id}")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        mensagem = f"""🚜 **{nome}**

📊 **Status:** {status}
⏱️ **Horímetro:** {horimetro:,.0f}h
👤 **Operador:** {operador.get('nome', 'N/A')}

🎯 **O que você deseja fazer?**"""
        
        await message.answer(
            mensagem,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar menu do equipamento: {e}")
        await message.answer("❌ Erro ao carregar dados do equipamento")

# ===============================================
# MENUS ESPECÍFICOS DOS MÓDULOS
# ===============================================

async def show_checklist_menu(message: Message, operador: dict):
    """Mostra menu do módulo checklist"""
    keyboard = [
        [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
        [InlineKeyboardButton(text="🔗 Acessar Equipamentos", callback_data="checklist_links")],
        [InlineKeyboardButton(text="❓ Como Usar", callback_data="checklist_ajuda")],
        [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
    ]
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        "📋 **Módulo Checklist**\n\n"
        "🎯 **Opções disponíveis:**\n"
        "• Ver seus checklists\n"
        "• Acessar equipamentos\n"
        "• Aprender a usar\n\n"
        "Escolha uma opção:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

async def show_abastecimento_menu(message: Message, operador: dict):
    """Mostra menu do módulo abastecimento"""
    await message.answer(
        "⛽ **Módulo Abastecimento**\n\n"
        "🚧 Este módulo está em desenvolvimento.\n"
        "Em breve você poderá:\n\n"
        "• Registrar abastecimentos\n"
        "• Ver histórico de combustível\n"
        "• Controlar consumo\n\n"
        "Para registrar um abastecimento, escaneie o QR code do equipamento.",
        parse_mode='Markdown'
    )

async def show_os_menu(message: Message, operador: dict):
    """Mostra menu do módulo OS"""
    await message.answer(
        "🔧 **Módulo Ordem de Serviço**\n\n"
        "🚧 Este módulo está em desenvolvimento.\n"
        "Em breve você poderá:\n\n"
        "• Abrir ordens de serviço\n"
        "• Acompanhar status\n"
        "• Ver histórico de manutenções\n\n"
        "Para abrir uma OS, escaneie o QR code do equipamento.",
        parse_mode='Markdown'
    )

async def show_financeiro_menu(message: Message, operador: dict):
    """Mostra menu do módulo financeiro"""
    await message.answer(
        "💰 **Módulo Financeiro**\n\n"
        "🚧 Este módulo está em desenvolvimento.\n"
        "Em breve você poderá:\n\n"
        "• Ver relatórios de custos\n"
        "• Acompanhar orçamentos\n"
        "• Controlar despesas\n\n"
        "Aguarde as próximas versões!",
        parse_mode='Markdown'
    )

async def show_qrcode_menu(message: Message, operador: dict):
    """Mostra menu do módulo QR Code"""
    await message.answer(
        "📱 **Módulo QR Code**\n\n"
        "🎯 **Como usar:**\n"
        "1. Aponte a câmera para o QR code do equipamento\n"
        "2. Toque no link que aparecer\n"
        "3. Acesse diretamente as funções do equipamento\n\n"
        "📋 **Funcionalidades via QR:**\n"
        "• Checklist NR12\n"
        "• Registro de abastecimento\n"
        "• Abertura de OS\n"
        "• Atualização de horímetro\n\n"
        "✅ Os QR codes estão disponíveis em cada equipamento.",
        parse_mode='Markdown'
    )

async def show_help_menu(message: Message):
    """Mostra menu de ajuda"""
    await message.answer(
        "❓ **Central de Ajuda**\n\n"
        "🤖 **Como usar o bot:**\n"
        "1. Faça login com /start\n"
        "2. Use os botões do menu\n"
        "3. Escaneie QR codes dos equipamentos\n\n"
        "📱 **Comandos disponíveis:**\n"
        "• /start - Fazer login\n"
        "• /admin - Painel administrativo (admins)\n\n"
        "🆘 **Precisa de ajuda?**\n"
        "Entre em contato com o suporte técnico.\n\n"
        "📞 Suporte: (11) 99999-9999",
        parse_mode='Markdown'
    )

# ===============================================
# HANDLERS DE EQUIPAMENTO (FSM)
# ===============================================

async def iniciar_abastecimento(message: Message, state: FSMContext, equipamento_id: str, operador: dict):
    """Inicia o processo de registro de abastecimento"""
    try:
        await definir_dados_temporarios(str(message.chat.id), 'equipamento_id_ativo', equipamento_id)
        
        await message.answer(
            "⛽ **Registrar Abastecimento**\n\n"
            "📊 Informe a quantidade abastecida em litros:\n"
            "*(ex: 45.5)*",
            parse_mode='Markdown'
        )
        
        await state.set_state(EquipmentStates.waiting_for_fuel_quantity)
        
    except Exception as e:
        logger.error(f"Erro ao iniciar abastecimento: {e}")
        await message.answer("❌ Erro ao iniciar registro de abastecimento")

async def process_fuel_quantity(message: Message, state: FSMContext):
    """Processa quantidade de combustível"""
    try:
        chat_id = str(message.chat.id)
        
        try:
            quantidade = float(message.text.replace(',', '.'))
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva")
        except ValueError:
            await message.answer("❌ Valor inválido. Digite apenas números (ex: 45.5):")
            return
        
        await definir_dados_temporarios(chat_id, 'abastecimento_quantidade', quantidade)
        
        await message.answer(
            f"⛽ **Quantidade:** {quantidade:.1f} litros\n\n"
            f"💰 Agora informe o valor total pago:\n"
            f"*(ex: 250.75)*",
            parse_mode='Markdown'
        )
        
        await state.set_state(EquipmentStates.waiting_for_fuel_value)
        
    except Exception as e:
        logger.error(f"Erro ao processar quantidade: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

async def process_fuel_value(message: Message, state: FSMContext):
    """Processa valor do abastecimento"""
    try:
        chat_id = str(message.chat.id)
        
        try:
            valor = float(message.text.replace(',', '.'))
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            await message.answer("❌ Valor inválido. Digite apenas números (ex: 250.75):")
            return
        
        # Buscar dados salvos
        quantidade = await obter_dados_temporarios(chat_id, 'abastecimento_quantidade')
        equipamento_id = await obter_dados_temporarios(chat_id, 'equipamento_id_ativo')
        operador = await obter_operador_sessao(chat_id)
        
        if not all([quantidade, equipamento_id, operador]):
            await message.answer("❌ Erro na sessão. Tente novamente.")
            await state.clear()
            return
        
        # Registrar abastecimento
        resultado = await registrar_abastecimento(
            equipamento_id=int(equipamento_id),
            operador_id=operador.get('id'),
            quantidade_litros=quantidade,
            valor_total=valor
        )
        
        if resultado:
            preco_litro = valor / quantidade
            
            await message.answer(
                f"✅ **Abastecimento Registrado!**\n\n"
                f"⛽ Quantidade: {quantidade:.1f} litros\n"
                f"💰 Valor: R$ {valor:.2f}\n"
                f"💲 Preço/litro: R$ {preco_litro:.3f}\n"
                f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"Registro salvo com sucesso!",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer(
                "❌ **Erro ao registrar abastecimento**\n\n"
                "Não foi possível salvar os dados. Tente novamente.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao processar valor: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

async def iniciar_ordem_servico(message: Message, state: FSMContext, equipamento_id: str, operador: dict):
    """Inicia processo de abertura de OS"""
    try:
        await definir_dados_temporarios(str(message.chat.id), 'equipamento_id_ativo', equipamento_id)
        
        # Criar teclado com tipos de problema
        keyboard = [
            [InlineKeyboardButton(text="🔧 Manutenção Preventiva", callback_data="os_tipo_PREVENTIVA")],
            [InlineKeyboardButton(text="⚠️ Manutenção Corretiva", callback_data="os_tipo_CORRETIVA")],
            [InlineKeyboardButton(text="⚡ Problema Elétrico", callback_data="os_tipo_ELETRICO")],
            [InlineKeyboardButton(text="🔩 Problema Mecânico", callback_data="os_tipo_MECANICO")],
            [InlineKeyboardButton(text="🛠️ Outros", callback_data="os_tipo_OUTROS")],
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar_os")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "🔧 **Abrir Ordem de Serviço**\n\n"
            "Selecione o tipo de problema:",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao iniciar OS: {e}")
        await message.answer("❌ Erro ao iniciar abertura de OS")

async def handle_os_type_callback(callback: CallbackQuery, state: FSMContext):
    """Handler para tipo de OS selecionado"""
    try:
        data = callback.data
        chat_id = str(callback.from_user.id)
        
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data == "cancelar_os":
            await callback.message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        # Extrair tipo
        tipo = data.replace("os_tipo_", "")
        await definir_dados_temporarios(chat_id, 'os_tipo', tipo)
        
        tipos_dict = {
            'PREVENTIVA': 'Manutenção Preventiva',
            'CORRETIVA': 'Manutenção Corretiva',
            'ELETRICO': 'Problema Elétrico',
            'MECANICO': 'Problema Mecânico',
            'OUTROS': 'Outros'
        }
        
        await callback.message.answer(
            f"🔧 **Tipo:** {tipos_dict.get(tipo, tipo)}\n\n"
            f"📝 Agora descreva o problema detalhadamente:",
            parse_mode='Markdown'
        )
        
        await state.set_state(EquipmentStates.waiting_for_os_description)
        
    except Exception as e:
        logger.error(f"Erro no callback de tipo OS: {e}")
        await callback.answer("❌ Erro interno")

async def process_os_description(message: Message, state: FSMContext):
    """Processa descrição da OS"""
    try:
        chat_id = str(message.chat.id)
        descricao = message.text.strip()
        
        if len(descricao) < 10:
            await message.answer("❌ Descrição muito curta. Detalhe melhor o problema:")
            return
        
        # Buscar dados salvos
        equipamento_id = await obter_dados_temporarios(chat_id, 'equipamento_id_ativo')
        tipo = await obter_dados_temporarios(chat_id, 'os_tipo')
        operador = await obter_operador_sessao(chat_id)
        
        if not all([equipamento_id, tipo, operador]):
            await message.answer("❌ Erro na sessão. Tente novamente.")
            await state.clear()
            return
        
        # Criar OS
        resultado = await criar_ordem_servico(
            equipamento_id=int(equipamento_id),
            operador_id=operador.get('id'),
            descricao=descricao,
            tipo_problema=tipo
        )
        
        if resultado:
            await message.answer(
                f"✅ **Ordem de Serviço Criada!**\n\n"
                f"🔧 Tipo: {tipo}\n"
                f"🆔 Número: {resultado.get('id')}\n"
                f"📝 Descrição: {descricao}\n"
                f"📅 Abertura: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"A equipe de manutenção foi notificada!",
                parse_mode='Markdown'
            )
        else:
            await message.answer(
                "❌ **Erro ao criar OS**\n\n"
                "Não foi possível criar a ordem de serviço. Tente novamente."
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao processar descrição da OS: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

# ===============================================
# OUTRAS FUNÇÕES AUXILIARES
# ===============================================

async def iniciar_novo_checklist(message: Message, equipamento_id: str, operador: dict):
    """Placeholder para iniciar novo checklist"""
    await message.answer(
        "📋 **Novo Checklist**\n\n"
        "🚧 Esta funcionalidade será implementada em breve!\n"
        "Aguarde as próximas atualizações.",
        parse_mode='Markdown'
    )

async def iniciar_atualizacao_horimetro(message: Message, state: FSMContext, equipamento_id: str, operador: dict):
    """Placeholder para atualizar horímetro"""
    await message.answer(
        "⏱️ **Atualizar Horímetro**\n\n"
        "🚧 Esta funcionalidade será implementada em breve!\n"
        "Aguarde as próximas atualizações.",
        parse_mode='Markdown'
    )

async def mostrar_historico_equipamento(message: Message, equipamento_id: str, operador: dict):
    """Placeholder para mostrar histórico"""
    await message.answer(
        "📊 **Histórico do Equipamento**\n\n"
        "🚧 Esta funcionalidade será implementada em breve!\n"
        "Aguarde as próximas atualizações.",
        parse_mode='Markdown'
    )

# ===============================================
# REGISTRO DOS HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers principais"""
    
    # Comandos
    dp.message.register(start_handler, Command("start"))
    
    # Estados de autenticação
    dp.message.register(process_name, AuthStates.waiting_for_name)
    dp.message.register(process_birth_date, AuthStates.waiting_for_birth_date)
    
    # Estados de equipamento
    dp.message.register(process_fuel_quantity, EquipmentStates.waiting_for_fuel_quantity)
    dp.message.register(process_fuel_value, EquipmentStates.waiting_for_fuel_value)
    dp.message.register(process_os_description, EquipmentStates.waiting_for_os_description)
    
    # Callbacks principais
    dp.callback_query.register(handle_operator_selection, F.data.startswith("select_operator_"))
    dp.callback_query.register(handle_menu_callback, F.data.startswith("menu_"))
    dp.callback_query.register(handle_equipamento_callback, F.data.startswith("eq_"))
    dp.callback_query.register(handle_os_type_callback, F.data.startswith("os_tipo_"))
    
    logger.info("Handlers principais registrados com sucesso")