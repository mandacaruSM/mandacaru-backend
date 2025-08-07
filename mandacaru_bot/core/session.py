# ===============================================
# ARQUIVO: mandacaru_bot/core/session.py
# Gerenciamento de sessões do bot
# ===============================================

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .config import SESSION_TIMEOUT_HOURS

logger = logging.getLogger(__name__)

# ===============================================
# ARMAZENAMENTO EM MEMÓRIA
# ===============================================

# Armazenamento das sessões (em produção use Redis)
_sessions: Dict[str, Dict[str, Any]] = {}
_temp_data: Dict[str, Dict[str, Any]] = {}

# ===============================================
# GERENCIAMENTO DE SESSÕES
# ===============================================

def iniciar_sessao(chat_id: str) -> Dict[str, Any]:
    """Inicia nova sessão para um chat_id"""
    chat_id = str(chat_id)
    
    sessao = {
        'chat_id': chat_id,
        'criada_em': datetime.now(),
        'ultimo_acesso': datetime.now(),
        'operador_id': None,
        'operador_nome': None,
        'operador_codigo': None,
        'autenticado': False,
        'equipamento_atual': None,
        'estado': 'inicio'
    }
    
    _sessions[chat_id] = sessao
    logger.info(f"✅ Sessão iniciada para chat_id: {chat_id}")
    return sessao

def obter_sessao(chat_id: str) -> Optional[Dict[str, Any]]:
    """Obtém sessão existente"""
    chat_id = str(chat_id)
    sessao = _sessions.get(chat_id)
    
    if sessao:
        # Verificar se não expirou
        if _sessao_expirou(sessao):
            limpar_sessao(chat_id)
            return None
        
        # Atualizar último acesso
        sessao['ultimo_acesso'] = datetime.now()
    
    return sessao

def atualizar_sessao(chat_id: str, dados: Dict[str, Any]) -> None:
    """Atualiza dados da sessão"""
    chat_id = str(chat_id)
    sessao = obter_sessao(chat_id)
    
    if not sessao:
        sessao = iniciar_sessao(chat_id)
    
    sessao.update(dados)
    sessao['ultimo_acesso'] = datetime.now()
    logger.debug(f"🔄 Sessão atualizada para {chat_id}: {list(dados.keys())}")

def limpar_sessao(chat_id: str) -> None:
    """Remove sessão e dados temporários"""
    chat_id = str(chat_id)
    
    if chat_id in _sessions:
        del _sessions[chat_id]
    
    if chat_id in _temp_data:
        del _temp_data[chat_id]
    
    logger.info(f"🧹 Sessão limpa para chat_id: {chat_id}")

def _sessao_expirou(sessao: Dict[str, Any]) -> bool:
    """Verifica se a sessão expirou"""
    limite = datetime.now() - timedelta(hours=SESSION_TIMEOUT_HOURS)
    return sessao['ultimo_acesso'] < limite

# ===============================================
# AUTENTICAÇÃO
# ===============================================

def autenticar_operador(chat_id: str, operador_data: Dict[str, Any]) -> None:
    """Autentica operador na sessão"""
    atualizar_sessao(chat_id, {
        'operador_id': operador_data['id'],
        'operador_nome': operador_data['nome'],
        'operador_codigo': operador_data['codigo'],
        'autenticado': True,
        'estado': 'menu_principal'
    })
    logger.info(f"🔐 Operador {operador_data['codigo']} autenticado no chat {chat_id}")

def verificar_autenticacao(chat_id: str) -> bool:
    """Verifica se o usuário está autenticado"""
    sessao = obter_sessao(chat_id)
    return sessao is not None and sessao.get('autenticado', False)

def obter_operador_sessao(chat_id: str) -> Optional[Dict[str, Any]]:
    """Obtém dados do operador autenticado"""
    sessao = obter_sessao(chat_id)
    
    if not sessao or not sessao.get('autenticado'):
        return None
    
    return {
        'id': sessao['operador_id'],
        'nome': sessao['operador_nome'],
        'codigo': sessao['operador_codigo']
    }

# ===============================================
# EQUIPAMENTO ATUAL
# ===============================================

def definir_equipamento_atual(chat_id: str, equipamento_data: Dict[str, Any]) -> None:
    """Define equipamento atual na sessão"""
    atualizar_sessao(chat_id, {
        'equipamento_atual': equipamento_data,
        'estado': 'menu_equipamento'
    })
    logger.info(f"🚜 Equipamento {equipamento_data.get('nome')} selecionado para {chat_id}")

def obter_equipamento_atual(chat_id: str) -> Optional[Dict[str, Any]]:
    """Obtém equipamento atual da sessão"""
    sessao = obter_sessao(chat_id)
    return sessao.get('equipamento_atual') if sessao else None

# ===============================================
# DADOS TEMPORÁRIOS
# ===============================================

def definir_dados_temporarios(chat_id: str, chave: str, valor: Any) -> None:
    """Armazena dados temporários"""
    chat_id = str(chat_id)
    
    if chat_id not in _temp_data:
        _temp_data[chat_id] = {}
    
    _temp_data[chat_id][chave] = valor
    logger.debug(f"💾 Dados temporários salvos: {chat_id}.{chave}")

def obter_dados_temporarios(chat_id: str, chave: str, padrao: Any = None) -> Any:
    """Obtém dados temporários"""
    chat_id = str(chat_id)
    return _temp_data.get(chat_id, {}).get(chave, padrao)

def limpar_dados_temporarios(chat_id: str, chave: str = None) -> None:
    """Limpa dados temporários"""
    chat_id = str(chat_id)
    
    if chave:
        if chat_id in _temp_data and chave in _temp_data[chat_id]:
            del _temp_data[chat_id][chave]
    else:
        if chat_id in _temp_data:
            del _temp_data[chat_id]

# ===============================================
# LIMPEZA AUTOMÁTICA
# ===============================================

def limpar_sessoes_expiradas() -> int:
    """Remove sessões expiradas"""
    removidas = 0
    chats_para_remover = []
    
    for chat_id, sessao in _sessions.items():
        if _sessao_expirou(sessao):
            chats_para_remover.append(chat_id)
    
    for chat_id in chats_para_remover:
        limpar_sessao(chat_id)
        removidas += 1
    
    if removidas > 0:
        logger.info(f"🧹 {removidas} sessões expiradas removidas")
    
    return removidas

def obter_estatisticas_sessoes() -> Dict[str, int]:
    """Obtém estatísticas das sessões"""
    total = len(_sessions)
    autenticadas = sum(1 for s in _sessions.values() if s.get('autenticado', False))
    
    return {
        'total': total,
        'autenticadas': autenticadas,
        'nao_autenticadas': total - autenticadas,
        'dados_temporarios': len(_temp_data)
    }