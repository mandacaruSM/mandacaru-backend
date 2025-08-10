# ===============================================
# ARQUIVO: mandacaru_bot/bot_main/handlers.py
# Handlers principais do bot - TODAS AS CORREÇÕES APLICADAS
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
# KEYBOARDS INLINE
# ===============================================

def criar_menu_principal():
    """Cria keyboard do menu principal"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="list_checklists")],
        [InlineKeyboardButton(text="🔧 Equipamentos", callback_data="list_equipamentos")],
        [InlineKeyboardButton(text="📱 Escanear QR", callback_data="scan_qr")],
        [InlineKeyboardButton(text="📊 Relatórios", callback_data="menu_reports")]
    ])

def criar_keyboard_voltar():
    """Cria keyboard simples de voltar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]
    ])

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
            await obj.answer("❌ Você precisa estar logado para usar esta funcionalidade.\n\nDigite /start para fazer login.")
            return
        
        # Adicionar operador aos argumentos
        operador = obter_operador_sessao(chat_id)
        kwargs['operador'] = operador
        
        return await handler(obj, *args, **kwargs)
    
    return wrapper

# ===============================================
# HANDLERS PRINCIPAIS
# ===============================================

async def start_handler(message: Message, state: FSMContext):
    """Handler do comando /start - CORRIGIDO"""
    try:
        chat_id = str(message.chat.id)
        
        # Verificar se usuário já está autenticado
        if verificar_autenticacao(chat_id):
            operador = obter_operador_sessao(chat_id)
            nome = operador.get('nome', 'Operador') if operador else 'Usuário'
            
            # CORRIGIDO: Mensagem direta ao invés de método inexistente
            await message.answer(
                f"🎉 **Bem-vindo de volta, {nome}!**\n\nVocê está logado com sucesso.\nSelecione uma opção:",
                reply_markup=criar_menu_principal()
            )
        else:
            # Tentar autenticação por chat_id
            operador = await buscar_operador_por_chat_id(chat_id)
            
            if operador:
                # Autenticar automaticamente - CORRIGIDO: removido terceiro argumento
                autenticar_operador(chat_id, operador)
                await message.answer(
                    f"🎉 **Bem-vindo de volta, {operador['nome']}!**\n\nLogin automático realizado.\nSelecione uma opção:",
                    reply_markup=criar_menu_principal()
                )
            else:
                # Solicitar autenticação - CORRIGIDO: Mensagens diretas
                await message.answer("🤖 **Bem-vindo ao Mandacaru Bot!**\n\nPara usar o sistema, você precisa se identificar.")
                await message.answer("👤 **Identificação**\n\nDigite seu nome completo (nome e sobrenome):")
                await state.set_state(AuthStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"❌ Erro no comando start: {e}")
        await message.answer("❌ Erro interno do sistema. Tente novamente em alguns instantes.")

async def processar_nome_operador(message: Message, state: FSMContext):
    """Processa o nome do operador - CORRIGIDO"""
    try:
        nome = message.text.strip()
        
        # Validação básica do nome
        if len(nome) < 3 or len(nome.split()) < 2:
            await message.answer("❌ **Nome Inválido**\n\nDigite seu nome completo (nome e sobrenome):")
            return
        
        # Buscar operador por nome
        operador = await buscar_operador_por_nome(nome)
        
        if not operador:
            await message.answer("❌ **Operador não encontrado**\n\nVerifique se o nome está correto e tente novamente.\n\nDigite seu nome completo:")
            return
        
        # Salvar operador encontrado
        await state.update_data(operador=operador)
        await message.answer("📅 **Confirmação de Identidade**\n\nDigite sua data de nascimento no formato DD/MM/AAAA:")
        await state.set_state(AuthStates.waiting_for_birth_date)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar nome: {e}")
        await message.answer("❌ Erro de conexão. Tente novamente.")
        await state.clear()

async def processar_data_nascimento(message: Message, state: FSMContext):
    """Processa a data de nascimento para autenticação - CORRIGIDO"""
    try:
        data_texto = message.text.strip()
        
        # Obter dados do estado
        state_data = await state.get_data()
        operador = state_data.get('operador')
        
        if not operador:
            await message.answer("❌ Erro interno. Digite /start para recomeçar.")
            await state.clear()
            return
        
        # Validar operador com data de nascimento
        if await validar_operador(operador['codigo'], data_texto):
            chat_id = str(message.chat.id)
            
            # Autenticar operador - CORRIGIDO: removido terceiro argumento
            autenticar_operador(chat_id, operador)
            
            # Atualizar chat_id no backend
            await atualizar_chat_id_operador(operador['id'], chat_id)
            
            await message.answer(
                f"✅ **Autenticação realizada com sucesso!**\n\nBem-vindo, {operador['nome']}!\n\nSelecione uma opção:",
                reply_markup=criar_menu_principal()
            )
            await state.clear()
        else:
            await message.answer("❌ **Data de nascimento incorreta**\n\nTente novamente ou digite /start para recomeçar.")
            await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar data de nascimento: {e}")
        await message.answer("❌ Erro interno. Digite /start para recomeçar.")
        await state.clear()

@require_auth
async def callback_handler(callback: CallbackQuery, operador=None):
    """Handler principal para callbacks do menu - CORRIGIDO"""
    try:
        await callback.answer()
        data = callback.data
        
        if data == "menu_refresh":
            await callback.message.edit_text(
                f"🏠 **Menu Principal**\n\nOlá, {operador['nome']}!\n\nSelecione uma opção:",
                reply_markup=criar_menu_principal()
            )
        
        elif data == "menu_checklists":
            await callback.message.edit_text(
                "📋 **Menu de Checklists**\n\nEscolha uma opção:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="list_checklists")],
                    [InlineKeyboardButton(text="🔧 Por Equipamento", callback_data="list_equipamentos")],
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_refresh")]
                ])
            )
        
        elif data == "menu_reports":
            await callback.message.edit_text(
                "📊 **Menu de Relatórios**\n\nEscolha uma opção:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Meus Relatórios", callback_data="my_reports")],
                    [InlineKeyboardButton(text="📈 Estatísticas", callback_data="stats_reports")],
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_refresh")]
                ])
            )
        
        elif data == "list_equipamentos":
            # Redirecionar para handler de equipamentos no módulo checklist
            try:
                from bot_checklist.handlers import listar_equipamentos_handler
                await listar_equipamentos_handler(callback, operador=operador)
            except ImportError:
                await callback.message.edit_text(
                    "⚠️ **Módulo de Equipamentos Indisponível**\n\nEsta funcionalidade está em manutenção.",
                    reply_markup=criar_keyboard_voltar()
                )
        
        elif data == "list_checklists":
            # Redirecionar para handler de checklists no módulo checklist
            try:
                from bot_checklist.handlers import listar_checklists_handler
                await listar_checklists_handler(callback, operador=operador)
            except ImportError:
                await callback.message.edit_text(
                    "⚠️ **Módulo de Checklists Indisponível**\n\nEsta funcionalidade está em manutenção.",
                    reply_markup=criar_keyboard_voltar()
                )
        
        elif data == "scan_qr":
            await callback.message.edit_text(
                "📱 **Escanear QR Code**\n\n"
                "Para escanear um QR Code de equipamento:\n\n"
                "1️⃣ Abra a câmera do seu celular\n"
                "2️⃣ Aponte para o QR Code\n"
                "3️⃣ Toque no link que aparecer\n"
                "4️⃣ O Telegram abrirá automaticamente\n\n"
                "💡 O QR Code geralmente está na plaqueta do equipamento.",
                reply_markup=criar_keyboard_voltar()
            )
        
        else:
            await callback.message.edit_text(
                "⚙️ **Funcionalidade em Desenvolvimento**\n\nEsta opção estará disponível em breve.",
                reply_markup=criar_keyboard_voltar()
            )
        
    except Exception as e:
        logger.error(f"❌ Erro no callback: {e}")
        await callback.message.edit_text(
            "❌ Erro interno. Tente novamente.",
            reply_markup=criar_keyboard_voltar()
        )

async def admin_handler(message: Message):
    """Handler do comando /admin (apenas para administradores)"""
    try:
        user_id = message.from_user.id
        
        if str(user_id) not in ADMIN_IDS:
            await message.answer("❌ Acesso negado. Você não é um administrador.")
            return
        
        stats = obter_estatisticas_sessoes()
        status_api = await verificar_status_api()
        
        texto = f"""
🔧 **PAINEL ADMINISTRATIVO**

📊 **Estatísticas do Sistema:**
• Sessões ativas: {stats.get('ativas', 0)}
• Total de logins: {stats.get('total_logins', 0)}
• API Status: {'🟢 Online' if status_api else '🔴 Offline'}

⚙️ **Ações Disponíveis:**
        """
        
        keyboard = [
            [InlineKeyboardButton(text="📊 Estatísticas Detalhadas", callback_data="admin_stats")],
            [InlineKeyboardButton(text="🧹 Limpar Sessões", callback_data="admin_cleanup")],
            [InlineKeyboardButton(text="🔄 Verificar API", callback_data="admin_api_check")]
        ]
        
        await message.answer(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no comando admin: {e}")
        await message.answer(f"❌ Erro: {e}")

async def admin_callback_handler(callback: CallbackQuery):
    """Handler para callbacks administrativos"""
    try:
        user_id = callback.from_user.id
        
        if str(user_id) not in ADMIN_IDS:
            await callback.answer("❌ Acesso negado", show_alert=True)
            return
        
        await callback.answer()
        data = callback.data
        
        if data == "admin_stats":
            stats = obter_estatisticas_sessoes()
            texto = f"""
📊 **Estatísticas Detalhadas**

🏃‍♂️ **Sessões Ativas:** {stats.get('ativas', 0)}
📈 **Total de Logins:** {stats.get('total_logins', 0)}
⏰ **Sessões Expiradas:** {stats.get('expiradas', 0)}
🕒 **Última Limpeza:** {stats.get('ultima_limpeza', 'N/A')}

🔧 **Sistema:** Funcionando
            """
        
        elif data == "admin_cleanup":
            from core.session import limpar_sessoes_expiradas
            removidas = limpar_sessoes_expiradas()
            texto = f"🧹 **Limpeza Executada**\n\n✅ {removidas} sessões removidas"
        
        elif data == "admin_api_check":
            status = await verificar_status_api()
            from core.config import API_BASE_URL
            texto = f"""
🔍 **Verificação da API**

Status: {'🟢 Online' if status else '🔴 Offline'}
URL: `{API_BASE_URL}`
Última verificação: Agora
            """
        
        else:
            texto = "❌ Ação não reconhecida"
        
        await callback.message.edit_text(texto)
            
    except Exception as e:
        logger.error(f"❌ Erro no admin callback: {e}")
        await callback.message.edit_text(f"❌ Erro: {e}")

# ===============================================
# REGISTRAR HANDLERS PRINCIPAIS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers principais no dispatcher"""
    
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
    
    logger.info("✅ Handlers principais registrados")