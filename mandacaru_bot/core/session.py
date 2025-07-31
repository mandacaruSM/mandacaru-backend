# ===============================================
# ARQUIVO COMPLETO: mandacaru_bot/core/session.py
# ===============================================

import logging
from typing import Dict, Optional
from enum import Enum
from datetime import datetime, timedelta
from .db import buscar_equipamento_por_chat_id

logger = logging.getLogger(__name__)

class SessionState(Enum):
    AGUARDANDO_NOME = "AGUARDANDO_NOME"
    AGUARDANDO_DATA_NASCIMENTO = "AGUARDANDO_DATA_NASCIMENTO"
    AUTENTICADO = "AUTENTICADO"

# Armazenamento em memória das sessões
_sessions: Dict[int, Dict] = {}

async def iniciar_sessao(user_id: int, operador_data: dict, estado: str = 'AUTENTICADO'):
    """Inicia uma nova sessão para o usuário"""
    _sessions[user_id] = {
        'estado': estado,
        'operador': operador_data,
        'operador_id': operador_data.get('id'),
        'operador_nome': operador_data.get('nome'),
        'ativo': True,
        'criado_em': datetime.now(),
        'ultimo_acesso': datetime.now()
    }
    logger.info(f"Sessão iniciada para usuário {user_id}: {operador_data.get('nome')}")

async def obter_sessao(user_id: int) -> Optional[dict]:
    """Obtém dados da sessão do usuário"""
    sessao = _sessions.get(user_id)
    if sessao:
        # Atualizar último acesso
        sessao['ultimo_acesso'] = datetime.now()
    return sessao

async def obter_operador_sessao(user_id: int) -> Optional[dict]:
    """Obtém dados do operador autenticado"""
    sessao = _sessions.get(user_id)
    if sessao and sessao.get('estado') == 'AUTENTICADO':
        # Atualizar último acesso
        sessao['ultimo_acesso'] = datetime.now()
        return sessao.get('operador')
    return None

async def atualizar_sessao(user_id: int, dados: dict):
    """Atualiza dados da sessão"""
    if user_id not in _sessions:
        _sessions[user_id] = {
            'criado_em': datetime.now(),
            'ultimo_acesso': datetime.now()
        }
    
    _sessions[user_id].update(dados)
    _sessions[user_id]['ultimo_acesso'] = datetime.now()
    logger.debug(f"Sessão atualizada para usuário {user_id}")

async def limpar_sessao(user_id: int):
    """Remove sessão do usuário"""
    if user_id in _sessions:
        del _sessions[user_id]
        logger.info(f"Sessão removida para usuário {user_id}")

async def verificar_autenticacao(user_id: int) -> bool:
    """Verifica se usuário está autenticado"""
    sessao = _sessions.get(user_id)
    return sessao and sessao.get('estado') == 'AUTENTICADO'

async def obter_estado_sessao(user_id: int) -> Optional[str]:
    """Obtém estado atual da sessão"""
    sessao = _sessions.get(user_id)
    return sessao.get('estado') if sessao else None

def listar_sessoes_ativas() -> int:
    """Retorna número de sessões ativas"""
    return len(_sessions)

def limpar_todas_sessoes():
    """Remove todas as sessões (para limpeza)"""
    global _sessions
    _sessions.clear()
    logger.info("Todas as sessões foram removidas")

async def limpar_sessoes_expiradas(timeout_hours: int = 24):
    """Remove sessões expiradas - FUNÇÃO QUE ESTAVA FALTANDO"""
    agora = datetime.now()
    timeout_delta = timedelta(hours=timeout_hours)
    
    sessoes_para_remover = []
    
    for user_id, sessao in _sessions.items():
        ultimo_acesso = sessao.get('ultimo_acesso', sessao.get('criado_em', agora))
        
        if agora - ultimo_acesso > timeout_delta:
            sessoes_para_remover.append(user_id)
    
    for user_id in sessoes_para_remover:
        del _sessions[user_id]
        logger.info(f"Sessão expirada removida para usuário {user_id}")
    
    if sessoes_para_remover:
        logger.info(f"Removidas {len(sessoes_para_remover)} sessões expiradas")
    
    return len(sessoes_para_remover)

def obter_estatisticas_sessoes() -> dict:
    """Retorna estatísticas das sessões"""
    agora = datetime.now()
    
    estatisticas = {
        'total_sessoes': len(_sessions),
        'autenticadas': 0,
        'aguardando_nome': 0,
        'aguardando_data': 0,
        'sessoes_ativas_1h': 0,
        'sessoes_ativas_24h': 0
    }
    
    for sessao in _sessions.values():
        estado = sessao.get('estado', '')
        
        if estado == 'AUTENTICADO':
            estatisticas['autenticadas'] += 1
        elif estado == 'AGUARDANDO_NOME':
            estatisticas['aguardando_nome'] += 1
        elif estado == 'AGUARDANDO_DATA_NASCIMENTO':
            estatisticas['aguardando_data'] += 1
        
        ultimo_acesso = sessao.get('ultimo_acesso', sessao.get('criado_em', agora))
        
        if agora - ultimo_acesso <= timedelta(hours=1):
            estatisticas['sessoes_ativas_1h'] += 1
        
        if agora - ultimo_acesso <= timedelta(hours=24):
            estatisticas['sessoes_ativas_24h'] += 1
    
    return estatisticas

# Função adicional para compatibilidade
async def iniciar_nova_sessao(user_id: int, estado: str = 'AGUARDANDO_NOME'):
    """Inicia uma nova sessão vazia"""
    await limpar_sessao(user_id)
    await atualizar_sessao(user_id, {'estado': estado})

# FUNÇÕES ADICIONAIS QUE PODEM ESTAR SENDO IMPORTADAS
async def esta_autenticado(user_id: int) -> bool:
    """Verifica se usuário está autenticado - ALIAS para verificar_autenticacao"""
    return await verificar_autenticacao(user_id)

async def obter_operador(user_id: int) -> Optional[dict]:
    """Obtém operador da sessão - ALIAS para obter_operador_sessao"""
    return await obter_operador_sessao(user_id)

async def criar_sessao(user_id: int, operador_data: dict, estado: str = 'AUTENTICADO'):
    """Cria sessão - ALIAS para iniciar_sessao"""
    return await iniciar_sessao(user_id, operador_data, estado)

def obter_sessoes_ativas() -> int:
    """Retorna número de sessões ativas - ALIAS"""
    return listar_sessoes_ativas()

async def limpar_sessao_usuario(user_id: int):
    """Remove sessão do usuário - ALIAS"""
    return await limpar_sessao(user_id)

def get_session_count() -> int:
    """Conta sessões - ALIAS em inglês"""
    return len(_sessions)

async def cleanup_expired_sessions(timeout_hours: int = 24) -> int:
    """Limpa sessões expiradas - ALIAS em inglês"""
    return await limpar_sessoes_expiradas(timeout_hours)

def get_session_stats() -> dict:
    """Estatísticas - ALIAS em inglês"""
    return obter_estatisticas_sessoes()

# Estados da sessão como strings (para compatibilidade)
AGUARDANDO_NOME = "AGUARDANDO_NOME"
AGUARDANDO_DATA_NASCIMENTO = "AGUARDANDO_DATA_NASCIMENTO"
AUTENTICADO = "AUTENTICADO"

# Variável sessions para compatibilidade com admin_handlers
sessions = _sessions

async def atualizar_sessao(user_id: int, chave_ou_dados, valor=None):
    """
    Atualiza dados da sessão - VERSÃO COMPATÍVEL
    Aceita tanto atualizar_sessao(user_id, dados_dict) quanto atualizar_sessao(user_id, chave, valor)
    """
    if user_id not in _sessions:
        _sessions[user_id] = {
            'criado_em': datetime.now(),
            'ultimo_acesso': datetime.now()
        }
    
    # Se valor foi passado, é o formato antigo: atualizar_sessao(user_id, "chave", valor)
    if valor is not None:
        _sessions[user_id][chave_ou_dados] = valor
    else:
        # Formato novo: atualizar_sessao(user_id, {"chave": valor})
        if isinstance(chave_ou_dados, dict):
            _sessions[user_id].update(chave_ou_dados)
        else:
            # Fallback: tratar como chave com valor None
            _sessions[user_id][chave_ou_dados] = None
    
    _sessions[user_id]['ultimo_acesso'] = datetime.now()
    logger.debug(f"Sessão atualizada para usuário {user_id}")

async def limpar_sessao(user_id: int):
    """Remove sessão do usuário"""
    if user_id in _sessions:
        del _sessions[user_id]
        logger.info(f"Sessão removida para usuário {user_id}")
        return True
    return False

# Função que estava sendo importada mas não existia
async def remover_sessao(user_id: int):
    """Remove sessão do usuário - ALIAS para limpar_sessao"""
    return await limpar_sessao(user_id)

# Função síncrona para compatibilidade com admin_handlers
async def limpar_sessoes_expiradas(timeout_hours: int = 24) -> int:
    """Remove sessões expiradas - VERSÃO SÍNCRONA"""
    agora = datetime.now()
    timeout_delta = timedelta(hours=timeout_hours)
    
    sessoes_para_remover = []
    
    for user_id, sessao in _sessions.items():
        ultimo_acesso = sessao.get('ultimo_acesso', sessao.get('criado_em', agora))
        
        if agora - ultimo_acesso > timeout_delta:
            sessoes_para_remover.append(user_id)
    
    for user_id in sessoes_para_remover:
        del _sessions[user_id]
        logger.info(f"Sessão expirada removida para usuário {user_id}")
    
    if sessoes_para_remover:
        logger.info(f"Removidas {len(sessoes_para_remover)} sessões expiradas")
    
    return len(sessoes_para_remover)

async def obter_equipamento_atual(chat_id: str) -> dict:
    """Obtém o equipamento atual vinculado ao chat"""
    return await buscar_equipamento_por_chat_id(chat_id)