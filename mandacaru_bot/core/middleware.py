# =====================
# core/middleware.py
# =====================

from functools import wraps
from aiogram.types import Message
from core.session import esta_autenticado, obter_operador

def require_auth(func):
    """
    Decorator que requer autenticação para executar o handler
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        chat_id = str(message.chat.id)
        
        # Verificar se está autenticado
        if not await esta_autenticado(chat_id):
            await message.answer(
                "🔒 Você precisa estar autenticado para usar este comando.\n\n"
                "Digite /start para fazer login."
            )
            return
        
        # Adiciona o operador aos kwargs para facilitar o acesso
        operador = await obter_operador(chat_id)
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
        
        if not await esta_autenticado(chat_id):
            await message.answer("🔒 Autenticação necessária.")
            return
        
        operador = await obter_operador(chat_id)
        if not operador or not operador.get('is_admin', False):
            await message.answer("❌ Acesso negado. Privilégios de administrador necessários.")
            return
        
        kwargs['operador'] = operador
        return await func(message, *args, **kwargs)
    
    return wrapper

async def log_user_action(message: Message, action: str, details: str = ""):
    """
    Registra ações do usuário para auditoria
    """
    chat_id = str(message.chat.id)
    operador = await obter_operador(chat_id)
    
    log_entry = {
        "chat_id": chat_id,
        "operador_id": operador.get('id') if operador else None,
        "operador_nome": operador.get('nome') if operador else 'Não autenticado',
        "action": action,
        "details": details,
        "timestamp": message.date.isoformat() if message.date else None
    }
    
    # Aqui você pode implementar o logging para banco de dados
    # ou arquivo, conforme necessário
    print(f"LOG: {log_entry}")