# ===============================================
# ARQUIVO: mandacaru_bot/core/middleware.py
# Middleware de autenticação para handlers
# ===============================================

import logging
from functools import wraps
from core.session import verificar_autenticacao, obter_operador_sessao
from core.templates import MessageTemplates

logger = logging.getLogger(__name__)

def require_auth(handler):
    """
    Decorator que exige autenticação para handlers do bot
    
    Uso:
    @require_auth
    async def meu_handler(callback: CallbackQuery, operador=None):
        # operador será injetado automaticamente
        pass
    """
    @wraps(handler)
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
            if hasattr(obj, 'answer'):
                await obj.answer(MessageTemplates.unauthorized_access())
            elif hasattr(obj, 'message'):
                await obj.message.answer(MessageTemplates.unauthorized_access())
            return
        
        # Adicionar operador aos argumentos
        operador = obter_operador_sessao(chat_id)
        kwargs['operador'] = operador
        
        return await handler(obj, *args, **kwargs)
    
    return wrapper

def require_admin(handler):
    """
    Decorator que exige privilégios de admin
    
    Uso:
    @require_admin
    async def admin_handler(callback: CallbackQuery, operador=None):
        # Só executará se o operador for admin
        pass
    """
    @wraps(handler)
    async def wrapper(obj, *args, **kwargs):
        # Primeiro verificar autenticação
        if hasattr(obj, 'chat'):
            chat_id = str(obj.chat.id)
        elif hasattr(obj, 'message') and hasattr(obj.message, 'chat'):
            chat_id = str(obj.message.chat.id)
        else:
            logger.error("❌ Não foi possível determinar chat_id")
            return
        
        # Verificar autenticação
        if not verificar_autenticacao(chat_id):
            if hasattr(obj, 'answer'):
                await obj.answer(MessageTemplates.unauthorized_access())
            elif hasattr(obj, 'message'):
                await obj.message.answer(MessageTemplates.unauthorized_access())
            return
        
        # Verificar se é admin
        operador = obter_operador_sessao(chat_id)
        
        # Verificar se tem permissões de admin (ajuste conforme sua lógica)
        is_admin = (
            operador.get('funcao', '').upper() in ['ADMIN', 'SUPERVISOR'] or
            operador.get('is_supervisor', False) or
            operador.get('admin', False)
        )
        
        if not is_admin:
            if hasattr(obj, 'answer'):
                await obj.answer("⛔ Acesso negado. Privilégios de administrador necessários.")
            elif hasattr(obj, 'message'):
                await obj.message.answer("⛔ Acesso negado. Privilégios de administrador necessários.")
            return
        
        # Adicionar operador aos argumentos
        kwargs['operador'] = operador
        
        return await handler(obj, *args, **kwargs)
    
    return wrapper

def log_handler_call(handler):
    """
    Decorator para logar chamadas de handlers (útil para debug)
    
    Uso:
    @log_handler_call
    async def meu_handler(callback: CallbackQuery):
        pass
    """
    @wraps(handler)
    async def wrapper(obj, *args, **kwargs):
        handler_name = handler.__name__
        
        if hasattr(obj, 'data'):
            logger.info(f"📱 Handler chamado: {handler_name} - Data: {obj.data}")
        elif hasattr(obj, 'text'):
            logger.info(f"💬 Handler chamado: {handler_name} - Texto: {obj.text[:50]}...")
        else:
            logger.info(f"🔧 Handler chamado: {handler_name}")
        
        try:
            result = await handler(obj, *args, **kwargs)
            logger.debug(f"✅ Handler {handler_name} executado com sucesso")
            return result
        except Exception as e:
            logger.error(f"❌ Erro no handler {handler_name}: {e}")
            raise
    
    return wrapper