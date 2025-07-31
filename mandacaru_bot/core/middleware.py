# ===============================================
# ARQUIVO: mandacaru_bot/core/middleware.py
# Middleware para autenticação e controle de acesso
# SALVAR COMO: mandacaru_bot/core/middleware.py
# ===============================================

import logging
from functools import wraps
from typing import Optional, Dict, Any
from aiogram.types import Message, CallbackQuery
from .session import verificar_autenticacao, obter_operador_sessao
from .config import ADMIN_IDS

logger = logging.getLogger(__name__)

def require_auth(func):
    """
    Decorator que requer autenticação para executar o handler
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        chat_id = str(message.chat.id)
        
        # Verificar se está autenticado
        if not await verificar_autenticacao(chat_id):
            await message.answer(
                "🔒 Você precisa estar autenticado para usar este comando.\n\n"
                "Digite /start para fazer login."
            )
            return
        
        # Adiciona o operador aos kwargs para facilitar o acesso
        operador = await obter_operador_sessao(chat_id)
        if not operador:
            await message.answer(
                "❌ Erro de sessão. Digite /start para fazer login novamente."
            )
            return
        
        kwargs['operador'] = operador
        
        return await func(message, *args, **kwargs)
    
    return wrapper

def admin_required(func):
    """
    Decorator que requer privilégios de administrador
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        
        # Verificar se está autenticado
        if not await verificar_autenticacao(chat_id):
            await message.answer("🔒 Autenticação necessária.")
            return
        
        # Verificar se é admin (por ID do Telegram)
        if user_id not in ADMIN_IDS:
            await message.answer("❌ Acesso negado. Privilégios de administrador necessários.")
            return
        
        operador = await obter_operador_sessao(chat_id)
        kwargs['operador'] = operador
        return await func(message, *args, **kwargs)
    
    return wrapper

async def log_user_action(message: Message, action: str, details: str = ""):
    """
    Registra ações do usuário para auditoria
    """
    chat_id = str(message.chat.id)
    operador = await obter_operador_sessao(chat_id)
    
    log_entry = {
        "chat_id": chat_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "operador_id": operador.get('id') if operador else None,
        "operador_nome": operador.get('nome') if operador else 'Não autenticado',
        "action": action,
        "details": details,
        "timestamp": message.date.isoformat() if message.date else None
    }
    
    logger.info(f"USER_ACTION: {log_entry}")

def is_admin(user_id: int) -> bool:
    """
    Verifica se um usuário é administrador
    
    Args:
        user_id: ID do usuário no Telegram
        
    Returns:
        True se for administrador
    """
    return user_id in ADMIN_IDS

async def get_user_permissions(chat_id: str) -> Dict[str, Any]:
    """
    Obtém permissões do usuário
    
    Args:
        chat_id: ID do chat
        
    Returns:
        Dicionário com permissões
    """
    operador = await obter_operador_sessao(chat_id)
    
    if not operador:
        return {
            'authenticated': False,
            'is_admin': False,
            'can_create_os': False,
            'can_register_fuel': False,
            'can_do_checklist': False
        }
    
    user_id = int(chat_id)  # Assumindo que chat_id é igual ao user_id
    
    return {
        'authenticated': True,
        'is_admin': is_admin(user_id),
        'can_create_os': True,  # Todos operadores podem criar OS
        'can_register_fuel': True,  # Todos operadores podem registrar combustível
        'can_do_checklist': True,  # Todos operadores podem fazer checklist
        'operador_id': operador.get('id'),
        'operador_nome': operador.get('nome'),
        'operador_funcao': operador.get('funcao')
    }

# Middleware class para uso com aiogram
class AuthMiddleware:
    """Middleware de autenticação para aiogram"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def __call__(self, handler, event, data):
        """
        Processa eventos do bot
        """
        # Adicionar informações de usuário aos dados
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
            chat_id = str(event.chat.id if hasattr(event, 'chat') else user_id)
            
            # Adicionar permissões aos dados
            data['permissions'] = await get_user_permissions(chat_id)
            data['is_admin'] = is_admin(user_id)
            
            # Log da ação
            if hasattr(event, 'text') and event.text:
                await log_user_action(event, "message", event.text[:100])
        
        # Continuar processamento
        return await handler(event, data)

# Exportar funções principais
__all__ = [
    'require_auth',
    'admin_required', 
    'log_user_action',
    'is_admin',
    'get_user_permissions',
    'AuthMiddleware'
]