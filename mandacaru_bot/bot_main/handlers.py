# ===============================================
# ARQUIVO: mandacaru_bot/bot_main/handlers.py
# Handlers principais do bot
# ===============================================

import logging
import re
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.config import ADMIN_IDS
from core.session import (
    iniciar_sessao, obter_sessao, atualizar_sessao, limpar_sessao,
    autenticar_operador, verificar_autenticacao, obter_operador_sessao,
    obter_estatisticas_sessoes
)
from core.db import (
    buscar_operador_por_nome, buscar_operador_por_chat_id, 
    validar_operador, atualizar_chat_id_operador, 
    verificar_status_api
)
from core.templates import MessageTemplates
from core.utils import Validators, SystemUtils

logger = logging.getLogger(__name__)

# ===============================================
# ESTADOS FSM
# ===============================================

class AuthStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()

# ===============================================
# MIDDLEWARE DE AUTENTICAÇÃO
# ===============================================

def require_auth(handler):
    """Decorator que exige autenticação"""
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
async def mostrar_menu_checklists(message: Message, operador=None):
    """Mostra menu de checklists"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="list_checklists")],
        [InlineKeyboardButton(text="🔍 Buscar por QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="🏠 Voltar", callback_data="menu_refresh")]
    ])
    
    texto = "📋 **Menu de Checklists**\n\nEscolha uma opção:"
    
    try:
        await message.edit_text(texto, reply_markup=keyboard)
    except:
        await message.answer(texto, reply_markup=keyboard)

@require_auth
async def mostrar_menu_equipamentos(message: Message, operador=None):
    """Mostra menu de equipamentos"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚜 Listar Equipamentos", callback_data="list_equipamentos")],
        [InlineKeyboardButton(text="🔍 Buscar por QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="🏠 Voltar", callback_data="menu_refresh")]
    ])
    
    texto = "🚜 **Menu de Equipamentos**\n\nEscolha uma opção:"
    
    try:
        await message.edit_text(texto, reply_markup=keyboard)
    except:
        await message.answer(texto, reply_markup=keyboard)

        
# ===============================================
# HANDLERS DE COMANDO
# ===============================================

async def start_handler(message: Message, state: FSMContext):
    """Handler do comando /start"""
    chat_id = str(message.chat.id)
    
    try:
        # Limpar estado anterior se existir
        await state.clear()
        
        # Verificar se há parâmetro no comando (QR Code)
        comando_completo = message.text.strip()
        
        # Tentar processar QR Code primeiro
        from bot_qr.handlers import processar_qr_code_start
        qr_processado = await processar_qr_code_start(message, comando_completo)
        
        if qr_processado:
            # QR Code foi processado com sucesso
            return
        
        # Verificar se o usuário já está autenticado
        if verificar_autenticacao(chat_id):
            operador = obter_operador_sessao(chat_id)
            await mostrar_menu_principal(message, operador['nome'])
            return
        
        # Verificar se já existe operador com este chat_id
        operador_existente = await buscar_operador_por_chat_id(chat_id)
        if operador_existente:
            # Autenticar automaticamente
            autenticar_operador(chat_id, operador_existente)
            await message.answer(MessageTemplates.auth_success(operador_existente['nome']))
            await mostrar_menu_principal(message, operador_existente['nome'])
            return
        
        # Iniciar processo de autenticação
        await iniciar_processo_login(message, state)
        
    except Exception as e:
        logger.error(f"❌ Erro em start_handler: {e}")
        await message.answer(MessageTemplates.error_generic())

async def iniciar_processo_login(message: Message, state: FSMContext):
    """Inicia o processo de login"""
    chat_id = str(message.chat.id)
    
    # Iniciar sessão
    iniciar_sessao(chat_id)
    
    # Enviar mensagem de boas-vindas
    await message.answer(MessageTemplates.welcome_message())
    
    # Definir estado para aguardar nome
    await state.set_state(AuthStates.waiting_for_name)

async def processar_nome_operador(message: Message, state: FSMContext):
    """Processa o nome do operador"""
    chat_id = str(message.chat.id)
    nome = message.text.strip()
    
    try:
        # Validar formato do nome
        if not Validators.validar_nome(nome):
            await message.answer("❌ **Nome Inválido**\n\nDigite seu nome completo (nome e sobrenome):")
            return
        
        # Buscar operador na API
        operador = await buscar_operador_por_nome(nome)
        
        if not operador:
            await message.answer(MessageTemplates.operator_not_found())
            await state.set_state(AuthStates.waiting_for_name)
            return
        
        # Salvar dados do operador temporariamente
        await state.update_data(operador_encontrado=operador)
        
        # Verificar se tem data de nascimento cadastrada
        if operador.get('data_nascimento'):
            await message.answer(MessageTemplates.auth_birth_date_request())
            await state.set_state(AuthStates.waiting_for_birth_date)
        else:
            # Se não tem data cadastrada, autenticar direto
            await finalizar_autenticacao(message, state, operador)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar nome: {e}")
        await message.answer(MessageTemplates.error_api_connection())

async def processar_data_nascimento(message: Message, state: FSMContext):
    """Processa a data de nascimento"""
    data_texto = message.text.strip()
    
    try:
        # Obter dados salvos
        data = await state.get_data()
        operador = data.get('operador_encontrado')
        
        if not operador:
            await message.answer("❌ Erro interno. Digite /start para recomeçar.")
            await state.clear()
            return
        
        # Validar operador com data de nascimento
        operador_validado = await validar_operador(operador['nome'], data_texto)
        
        if operador_validado:
            await finalizar_autenticacao(message, state, operador_validado)
        else:
            await message.answer(MessageTemplates.auth_failed())
            await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar data: {e}")
        await message.answer(MessageTemplates.error_generic())

async def finalizar_autenticacao(message: Message, state: FSMContext, operador: dict):
    """Finaliza o processo de autenticação"""
    chat_id = str(message.chat.id)
    
    try:
        # Atualizar chat_id no sistema
        await atualizar_chat_id_operador(operador['id'], chat_id)
        
        # Autenticar na sessão
        autenticar_operador(chat_id, operador)
        
        # Mensagem de sucesso
        await message.answer(MessageTemplates.auth_success(operador['nome']))
        
        # Verificar se há equipamento pendente (UUID salvo de QR Code)
        from core.session import obter_dados_temporarios
        equipamento_uuid = obter_dados_temporarios(chat_id, 'equipamento_uuid_pendente')
        
        if equipamento_uuid:
            # Processar equipamento que estava pendente
            from bot_qr.handlers import processar_qr_equipamento
            await processar_qr_equipamento(message, equipamento_uuid)
        else:
            await mostrar_menu_principal(message, operador['nome'])
        
        # Limpar estado
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Erro ao finalizar autenticação: {e}")
        await message.answer(MessageTemplates.error_generic())

# ===============================================
# MENU PRINCIPAL
# ===============================================

# ===============================================
# CORREÇÃO: Substitua a função mostrar_menu_principal
# no arquivo mandacaru_bot/bot_main/handlers.py
# ===============================================

async def mostrar_menu_principal(message: Message, operador_nome: str):
    """Mostra o menu principal com botões funcionais"""
    
    # Criar keyboard inline
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Checklists", callback_data="menu_checklists"),
            InlineKeyboardButton(text="🚜 Equipamentos", callback_data="menu_equipamentos")
        ],
        [
            InlineKeyboardButton(text="❓ Ajuda", callback_data="menu_help"),
            InlineKeyboardButton(text="⚙️ Atualizar", callback_data="menu_refresh")
        ]
    ])
    
    texto = MessageTemplates.main_menu(operador_nome)
    
    try:
        # Tentar editar mensagem existente
        await message.edit_text(texto, reply_markup=keyboard)
    except:
        # Se não conseguir editar, enviar nova mensagem
        await message.answer(texto, reply_markup=keyboard)

# ===============================================
# CORREÇÃO: Atualize também a função callback_handler
# ===============================================

async def callback_handler(callback: CallbackQuery):
    """Handler geral para callbacks"""
    data = callback.data
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer()  # Confirmar callback
        
        if data == "menu_refresh":
            if verificar_autenticacao(chat_id):
                operador = obter_operador_sessao(chat_id)
                await mostrar_menu_principal(callback.message, operador['nome'])
            else:
                await callback.message.edit_text(MessageTemplates.unauthorized_access())
                
        elif data == "menu_checklists":
            await mostrar_menu_checklists(callback.message)
            
        elif data == "menu_equipamentos":
            await mostrar_menu_equipamentos(callback.message)
            
        elif data == "menu_help":
            await callback.message.edit_text(MessageTemplates.help_message())
            
    except Exception as e:
        logger.error(f"❌ Erro no callback: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

# ===============================================
# ADICIONE também estas funções se não existirem:
# ===============================================

def require_auth(handler):
    """Decorator que exige autenticação"""
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
async def mostrar_menu_checklists(message: Message, operador=None):
    """Mostra menu de checklists"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="list_checklists")],
        [InlineKeyboardButton(text="🔍 Buscar por QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="🏠 Voltar", callback_data="menu_refresh")]
    ])
    
    texto = "📋 **Menu de Checklists**\n\nEscolha uma opção:"
    
    try:
        await message.edit_text(texto, reply_markup=keyboard)
    except:
        await message.answer(texto, reply_markup=keyboard)

@require_auth
async def mostrar_menu_equipamentos(message: Message, operador=None):
    """Mostra menu de equipamentos"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚜 Listar Equipamentos", callback_data="list_equipamentos")],
        [InlineKeyboardButton(text="🔍 Buscar por QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="🏠 Voltar", callback_data="menu_refresh")]
    ])
    
    texto = "🚜 **Menu de Equipamentos**\n\nEscolha uma opção:"
    
    try:
        await message.edit_text(texto, reply_markup=keyboard)
    except:
        await message.answer(texto, reply_markup=keyboard)
# ===============================================
# HANDLERS DE CALLBACK
# ===============================================

async def callback_handler(callback: CallbackQuery):
    """Handler geral para callbacks"""
    data = callback.data
    chat_id = str(callback.message.chat.id)
    
    try:
        await callback.answer()  # Confirmar callback
        
        if data == "menu_refresh":
            if verificar_autenticacao(chat_id):
                operador = obter_operador_sessao(chat_id)
                await mostrar_menu_principal(callback.message, operador['nome'])
            else:
                await callback.message.edit_text(MessageTemplates.unauthorized_access())
                
        elif data == "menu_checklists":
            await mostrar_menu_checklists(callback.message)
            
        elif data == "menu_equipamentos":
            await mostrar_menu_equipamentos(callback.message)
            
        elif data == "menu_help":
            await callback.message.edit_text(MessageTemplates.help_message())
            
    except Exception as e:
        logger.error(f"❌ Erro no callback: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

# ===============================================
# MENUS ESPECÍFICOS
# ===============================================

@require_auth
async def mostrar_menu_checklists(message: Message, operador=None):
    """Mostra menu de checklists"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="list_checklists")],
        [InlineKeyboardButton(text="🔍 Buscar por QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="🏠 Voltar", callback_data="menu_refresh")]
    ])
    
    texto = "📋 **Menu de Checklists**\n\nEscolha uma opção:"
    await message.edit_text(texto, reply_markup=keyboard)

@require_auth
async def mostrar_menu_equipamentos(message: Message, operador=None):
    """Mostra menu de equipamentos"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚜 Listar Equipamentos", callback_data="list_equipamentos")],
        [InlineKeyboardButton(text="🔍 Buscar por QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="🏠 Voltar", callback_data="menu_refresh")]
    ])
    
    texto = "🚜 **Menu de Equipamentos**\n\nEscolha uma opção:"
    await message.edit_text(texto, reply_markup=keyboard)

# ===============================================
# PROCESSAMENTO DE QR CODE
# ===============================================

async def processar_equipamento_qr(message: Message, uuid: str):
    """Processa QR code de equipamento"""
    
    await message.answer(f"🔍 **Processando QR Code...**\n\nUUID: `{uuid}`")
    
    # TODO: Implementar busca de equipamento por UUID
    # Por enquanto, mostrar mensagem de desenvolvimento
    await message.answer(MessageTemplates.feature_under_development())

# ===============================================
# COMANDOS ADMINISTRATIVOS
# ===============================================

async def admin_handler(message: Message):
    """Handler para comandos administrativos"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await message.answer("🚫 **Acesso Negado**\n\nVocê não tem permissão para usar comandos administrativos.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Status", callback_data="admin_status"),
            InlineKeyboardButton(text="🧹 Limpeza", callback_data="admin_cleanup")
        ],
        [
            InlineKeyboardButton(text="🔄 Restart", callback_data="admin_restart"),
            InlineKeyboardButton(text="📋 Logs", callback_data="admin_logs")
        ]
    ])
    
    await message.answer(MessageTemplates.admin_menu(), reply_markup=keyboard)

async def admin_callback_handler(callback: CallbackQuery):
    """Handler para callbacks administrativos"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Acesso negado", show_alert=True)
        return
    
    data = callback.data
    
    try:
        await callback.answer()
        
        if data == "admin_status":
            # Obter estatísticas
            session_stats = obter_estatisticas_sessoes()
            api_status = await verificar_status_api()
            system_info = SystemUtils.get_memory_usage()
            
            stats = {
                'total_sessions': session_stats['total'],
                'authenticated_users': session_stats['autenticadas'],
                'api_status': api_status,
                **system_info
            }
            
            texto = MessageTemplates.system_status(stats)
            await callback.message.edit_text(texto)
            
        elif data == "admin_cleanup":
            from core.session import limpar_sessoes_expiradas
            removidas = limpar_sessoes_expiradas()
            
            texto = f"🧹 **Limpeza Executada**\n\n{removidas} sessões expiradas removidas."
            await callback.message.edit_text(texto)
            
    except Exception as e:
        logger.error(f"❌ Erro no admin callback: {e}")
        await callback.message.edit_text(f"❌ Erro: {e}")

# ===============================================
# REGISTRAR HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers no dispatcher"""
    
    # Comandos principais
    dp.message.register(start_handler, Command("start"))
    dp.message.register(admin_handler, Command("admin"))
    
    # Estados de autenticação
    dp.message.register(processar_nome_operador, AuthStates.waiting_for_name)
    dp.message.register(processar_data_nascimento, AuthStates.waiting_for_birth_date)
    
    # Callbacks gerais
    dp.callback_query.register(callback_handler, F.data.startswith("menu_"))
    dp.callback_query.register(admin_callback_handler, F.data.startswith("admin_"))
    
    # Callbacks de lista/navegação
    #dp.callback_query.register(callback_handler, F.data.startswith("list_"))
    #dp.callback_query.register(callback_handler, F.data.in_({"scan_qr"}))
    
    logger.info("✅ Handlers principais registrados")

def register_checklist_handlers(dp: Dispatcher):
    """Registra handlers de checklist separadamente"""
    try:
        from bot_checklist.handlers import register_handlers as register_checklist_handlers_internal
        register_checklist_handlers_internal(dp)
        logger.info("✅ Handlers de checklist registrados")
    except ImportError as e:
        logger.warning(f"⚠️ Módulo checklist não encontrado: {e}")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar handlers de checklist: {e}")

def register_qr_handlers(dp: Dispatcher):
    """Registra handlers de QR code separadamente"""
    try:
        from bot_qr.handlers import register_handlers as register_qr_handlers_internal
        register_qr_handlers_internal(dp)
        logger.info("✅ Handlers de QR Code registrados")
    except ImportError as e:
        logger.warning(f"⚠️ Módulo QR não encontrado: {e}")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar handlers de QR: {e}")

def register_reports_handlers(dp: Dispatcher):
    """Registra handlers de relatórios separadamente"""
    try:
        from bot_reports.handlers import register_handlers as register_reports_handlers_internal
        register_reports_handlers_internal(dp)
        logger.info("✅ Handlers de relatórios registrados")
    except ImportError as e:
        logger.warning(f"⚠️ Módulo relatórios não encontrado: {e}")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar handlers de relatórios: {e}")

# =============================================== 
# HANDLERS ESPECÍFICOS PARA CALLBACKS PRINCIPAIS
# ===============================================

@require_auth
async def handle_list_checklists(callback: CallbackQuery, operador=None):
    """Handler para botão 'Meus Checklists'"""
    try:
        await callback.answer()
        
        # Redirecionar para o handler do módulo checklist
        from bot_checklist.handlers import listar_checklists_handler
        await listar_checklists_handler(callback, operador=operador)
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar checklists: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth 
async def handle_list_equipamentos(callback: CallbackQuery, operador=None):
    """Handler para botão 'Listar Equipamentos'"""
    try:
        await callback.answer()
        
        # Redirecionar para o handler do módulo checklist  
        from bot_checklist.handlers import listar_equipamentos_handler
        await listar_equipamentos_handler(callback, operador=operador)
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar equipamentos: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def handle_scan_qr(callback: CallbackQuery, operador=None):
    """Handler para botão 'Buscar por QR'"""
    try:
        await callback.answer()
        
        # Redirecionar para o handler do módulo QR
        from bot_qr.handlers import scan_new_qr_handler
        await scan_new_qr_handler(callback, operador=operador)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar QR: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

# ===============================================
# MODIFICAR A FUNÇÃO register_handlers EXISTENTE
# ADICIONAR ESTAS LINHAS NO FINAL DA FUNÇÃO
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers no dispatcher"""
    
    # Comandos principais
    dp.message.register(start_handler, Command("start"))
    dp.message.register(admin_handler, Command("admin"))
    
    # Estados de autenticação
    dp.message.register(processar_nome_operador, AuthStates.waiting_for_name)
    dp.message.register(processar_data_nascimento, AuthStates.waiting_for_birth_date)
    
    # Callbacks gerais
    dp.callback_query.register(callback_handler, F.data.startswith("menu_"))
    dp.callback_query.register(admin_callback_handler, F.data.startswith("admin_"))
    
    # Callbacks de lista/navegação  
    dp.callback_query.register(callback_handler, F.data.startswith("list_"))
    dp.callback_query.register(callback_handler, F.data.in_({"scan_qr"}))
    
    # ===============================================
    # ADICIONAR ESTAS LINHAS (HANDLERS ESPECÍFICOS):
    # ===============================================
    
    # Handlers específicos para botões principais
    dp.callback_query.register(handle_list_checklists, F.data == "list_checklists")
    dp.callback_query.register(handle_list_equipamentos, F.data == "list_equipamentos") 
    dp.callback_query.register(handle_scan_qr, F.data == "scan_qr")
    
    logger.info("✅ Handlers principais registrados")