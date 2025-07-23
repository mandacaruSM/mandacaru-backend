# ================================================================
# ARQUIVO: backend/apps/bot_telegram/utils/sessions.py
# Sistema de gerenciamento de sessões melhorado
# ================================================================

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import redis
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Configurar Redis (opcional, pode usar memória)
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=1,
        decode_responses=True
    )
    USE_REDIS = True
except:
    USE_REDIS = False
    logger.warning("Redis não disponível, usando memória para sessões")

# Armazenamento em memória como fallback
_memory_sessions = {}


class SessionManager:
    """Gerenciador de sessões do bot"""
    
    def __init__(self):
        self.timeout_hours = getattr(settings, 'SESSION_TIMEOUT_HOURS', 24)
        self.prefix = 'bot_session:'
    
    def save(self, chat_id: str, data: Dict[str, Any]) -> bool:
        """Salva dados da sessão"""
        try:
            # Adicionar timestamp
            data['ultimo_acesso'] = datetime.now().isoformat()
            
            if USE_REDIS:
                key = f"{self.prefix}{chat_id}"
                redis_client.setex(
                    key,
                    timedelta(hours=self.timeout_hours),
                    json.dumps(data)
                )
            else:
                _memory_sessions[chat_id] = data
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar sessão: {e}")
            return False
    
    def get(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Recupera dados da sessão"""
        try:
            if USE_REDIS:
                key = f"{self.prefix}{chat_id}"
                data = redis_client.get(key)
                if data:
                    return json.loads(data)
            else:
                data = _memory_sessions.get(chat_id)
                if data:
                    # Verificar timeout
                    ultimo_acesso = datetime.fromisoformat(data.get('ultimo_acesso', ''))
                    if datetime.now() - ultimo_acesso > timedelta(hours=self.timeout_hours):
                        self.clear(chat_id)
                        return None
                    return data
            
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar sessão: {e}")
            return None
    
    def clear(self, chat_id: str) -> bool:
        """Limpa sessão"""
        try:
            if USE_REDIS:
                key = f"{self.prefix}{chat_id}"
                redis_client.delete(key)
            else:
                _memory_sessions.pop(chat_id, None)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar sessão: {e}")
            return False
    
    def update(self, chat_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza dados da sessão"""
        data = self.get(chat_id) or {}
        data.update(updates)
        return self.save(chat_id, data)


# Instância global
_session_manager = SessionManager()

# Funções de conveniência
def save_session(chat_id: str, data: Dict[str, Any]) -> bool:
    return _session_manager.save(str(chat_id), data)

def get_session(chat_id: str) -> Optional[Dict[str, Any]]:
    return _session_manager.get(str(chat_id))

def clear_session(chat_id: str) -> bool:
    return _session_manager.clear(str(chat_id))

def update_session(chat_id: str, updates: Dict[str, Any]) -> bool:
    return _session_manager.update(str(chat_id), updates)
