# ===============================================
# ARQUIVO LIMPO: mandacaru_bot/core/session.py
# Sistema de sessões unificado e sem duplicações
# ===============================================

import logging
from typing import Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
from .config import SESSION_TIMEOUT_HOURS

logger = logging.getLogger(__name__)

# ===============================================
# ESTADOS E CONSTANTES
# ===============================================

class SessionState(Enum):
    """Estados possíveis da sessão"""
    AGUARDANDO_NOME = "AGUARDANDO_NOME"
    AGUARDANDO_DATA_NASCIMENTO = "AGUARDANDO_DATA_NASCIMENTO"
    AUTENTICADO = "AUTENTICADO"
    CHECKLIST_ATIVO = "CHECKLIST_ATIVO"
    ABASTECIMENTO_ATIVO = "ABASTECIMENTO_ATIVO"
    OS_ATIVO = "OS_ATIVO"
    AGUARDANDO_BROADCAST = "AGUARDANDO_BROADCAST"

# Constantes para compatibilidade (strings)
AGUARDANDO_NOME = "AGUARDANDO_NOME"
AGUARDANDO_DATA_NASCIMENTO = "AGUARDANDO_DATA_NASCIMENTO"
AUTENTICADO = "AUTENTICADO"

# ===============================================
# ARMAZENAMENTO DE SESSÕES (EM MEMÓRIA)
# ===============================================

# Dicionário principal de sessões
_sessions: Dict[int, Dict[str, Any]] = {}

# Alias para compatibilidade com código existente
sessions = _sessions

# ===============================================
# FUNÇÕES PRINCIPAIS DE SESSÃO
# ===============================================

async def iniciar_sessao(user_id: Union[int, str], operador_data: Dict[str, Any], estado: str = 'AUTENTICADO') -> None:
    """
    Inicia uma nova sessão para o usuário
    
    Args:
        user_id: ID do usuário (int ou str)
        operador_data: Dados do operador
        estado: Estado inicial da sessão
    """
    user_id = int(user_id)
    
    _sessions[user_id] = {
        'estado': estado,
        'operador': operador_data.copy(),
        'operador_id': operador_data.get('id'),
        'operador_nome': operador_data.get('nome'),
        'ativo': True,
        'criado_em': datetime.now(),
        'ultimo_acesso': datetime.now(),
        'dados_temporarios': {},
        'equipamento_atual': None
    }
    
    logger.info(f"Sessão iniciada para usuário {user_id}: {operador_data.get('nome')}")

async def obter_sessao(user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    """
    Obtém dados completos da sessão do usuário
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Dados da sessão ou None se não existir
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    
    if sessao:
        # Atualizar último acesso
        sessao['ultimo_acesso'] = datetime.now()
        return sessao.copy()
    
    return None

async def obter_operador_sessao(user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    """
    Obtém dados do operador autenticado
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Dados do operador ou None se não autenticado
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    
    if sessao and sessao.get('estado') == 'AUTENTICADO':
        # Atualizar último acesso
        sessao['ultimo_acesso'] = datetime.now()
        return sessao.get('operador', {}).copy()
    
    return None

async def atualizar_sessao(user_id: Union[int, str], dados_ou_chave: Union[Dict[str, Any], str], valor: Any = None) -> None:
    """
    Atualiza dados da sessão
    
    Args:
        user_id: ID do usuário
        dados_ou_chave: Dicionário com dados OU nome da chave
        valor: Valor (se dados_ou_chave for string)
    """
    user_id = int(user_id)
    
    # Criar sessão se não existir
    if user_id not in _sessions:
        _sessions[user_id] = {
            'criado_em': datetime.now(),
            'ultimo_acesso': datetime.now(),
            'dados_temporarios': {},
            'ativo': True
        }
    
    # Atualizar dados
    if isinstance(dados_ou_chave, dict):
        _sessions[user_id].update(dados_ou_chave)
    else:
        _sessions[user_id][dados_ou_chave] = valor
    
    # Sempre atualizar último acesso
    _sessions[user_id]['ultimo_acesso'] = datetime.now()
    
    logger.debug(f"Sessão atualizada para usuário {user_id}")

async def limpar_sessao(user_id: Union[int, str]) -> None:
    """
    Remove completamente uma sessão
    
    Args:
        user_id: ID do usuário
    """
    user_id = int(user_id)
    
    if user_id in _sessions:
        operador_nome = _sessions[user_id].get('operador', {}).get('nome', 'Desconhecido')
        del _sessions[user_id]
        logger.info(f"Sessão removida para {operador_nome} (ID: {user_id})")

# ===============================================
# FUNÇÕES DE ESTADO DA SESSÃO
# ===============================================

async def verificar_autenticacao(user_id: Union[int, str]) -> bool:
    """
    Verifica se o usuário está autenticado
    
    Args:
        user_id: ID do usuário
        
    Returns:
        True se autenticado
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    return sessao is not None and sessao.get('estado') == 'AUTENTICADO'

async def obter_estado_sessao(user_id: Union[int, str]) -> Optional[str]:
    """
    Obtém o estado atual da sessão
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Estado da sessão ou None
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    return sessao.get('estado') if sessao else None

async def definir_estado_sessao(user_id: Union[int, str], estado: str) -> None:
    """
    Define o estado da sessão
    
    Args:
        user_id: ID do usuário
        estado: Novo estado
    """
    await atualizar_sessao(user_id, 'estado', estado)

# ===============================================
# DADOS TEMPORÁRIOS
# ===============================================

async def definir_dados_temporarios(user_id: Union[int, str], chave: str, valor: Any) -> None:
    """
    Define dados temporários na sessão
    
    Args:
        user_id: ID do usuário
        chave: Chave dos dados
        valor: Valor a armazenar
    """
    user_id = int(user_id)
    
    if user_id not in _sessions:
        await atualizar_sessao(user_id, {})
    
    if 'dados_temporarios' not in _sessions[user_id]:
        _sessions[user_id]['dados_temporarios'] = {}
    
    _sessions[user_id]['dados_temporarios'][chave] = valor
    _sessions[user_id]['ultimo_acesso'] = datetime.now()

async def obter_dados_temporarios(user_id: Union[int, str], chave: str, padrao: Any = None) -> Any:
    """
    Obtém dados temporários da sessão
    
    Args:
        user_id: ID do usuário
        chave: Chave dos dados
        padrao: Valor padrão se não encontrado
        
    Returns:
        Valor armazenado ou padrão
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    
    if sessao and 'dados_temporarios' in sessao:
        return sessao['dados_temporarios'].get(chave, padrao)
    
    return padrao

async def limpar_dados_temporarios(user_id: Union[int, str], chave: Optional[str] = None) -> None:
    """
    Limpa dados temporários
    
    Args:
        user_id: ID do usuário
        chave: Chave específica ou None para limpar tudo
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    
    if sessao and 'dados_temporarios' in sessao:
        if chave:
            sessao['dados_temporarios'].pop(chave, None)
        else:
            sessao['dados_temporarios'] = {}

# ===============================================
# EQUIPAMENTO ATUAL
# ===============================================

async def definir_equipamento_atual(user_id: Union[int, str], equipamento_data: Dict[str, Any]) -> None:
    """
    Define o equipamento atual da sessão
    
    Args:
        user_id: ID do usuário
        equipamento_data: Dados do equipamento
    """
    await atualizar_sessao(user_id, 'equipamento_atual', equipamento_data.copy())
    logger.info(f"Equipamento atual definido para usuário {user_id}: {equipamento_data.get('nome')}")

async def obter_equipamento_atual(user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    """
    Obtém o equipamento atual da sessão
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Dados do equipamento ou None
    """
    user_id = int(user_id)
    sessao = _sessions.get(user_id)
    
    if sessao:
        sessao['ultimo_acesso'] = datetime.now()
        return sessao.get('equipamento_atual')
    
    return None

async def limpar_equipamento_atual(user_id: Union[int, str]) -> None:
    """
    Remove o equipamento atual da sessão
    
    Args:
        user_id: ID do usuário
    """
    await atualizar_sessao(user_id, 'equipamento_atual', None)

# ===============================================
# LIMPEZA E MANUTENÇÃO
# ===============================================

def limpar_sessoes_expiradas(timeout_hours: int = None) -> int:
    """
    Remove sessões expiradas (versão síncrona para compatibilidade)
    
    Args:
        timeout_hours: Horas para considerar expirada
        
    Returns:
        Número de sessões removidas
    """
    if timeout_hours is None:
        timeout_hours = SESSION_TIMEOUT_HOURS
    
    agora = datetime.now()
    limite = timedelta(hours=timeout_hours)
    sessoes_expiradas = []
    
    for user_id, sessao in _sessions.items():
        ultimo_acesso = sessao.get('ultimo_acesso', sessao.get('criado_em', agora))
        if agora - ultimo_acesso > limite:
            sessoes_expiradas.append(user_id)
    
    for user_id in sessoes_expiradas:
        operador_nome = _sessions[user_id].get('operador', {}).get('nome', 'Desconhecido')
        del _sessions[user_id]
        logger.info(f"Sessão expirada removida: {operador_nome} (ID: {user_id})")
    
    return len(sessoes_expiradas)

async def limpar_sessoes_expiradas_async(timeout_hours: int = None) -> int:
    """
    Versão assíncrona de limpeza de sessões expiradas
    
    Args:
        timeout_hours: Horas para considerar expirada
        
    Returns:
        Número de sessões removidas
    """
    return limpar_sessoes_expiradas(timeout_hours)

# ===============================================
# ESTATÍSTICAS E INFORMAÇÕES
# ===============================================

def listar_sessoes_ativas() -> int:
    """
    Retorna número de sessões ativas
    
    Returns:
        Quantidade de sessões ativas
    """
    return len(_sessions)

def obter_estatisticas_sessoes() -> Dict[str, Any]:
    """
    Obtém estatísticas detalhadas das sessões
    
    Returns:
        Dicionário com estatísticas
    """
    agora = datetime.now()
    
    estatisticas = {
        'total_sessoes': len(_sessions),
        'sessoes_autenticadas': 0,
        'sessoes_aguardando_login': 0,
        'sessoes_ativas_1h': 0,
        'sessoes_ativas_24h': 0,
        'usuarios_ativos': []
    }
    
    for user_id, sessao in _sessions.items():
        estado = sessao.get('estado', '')
        
        if estado == 'AUTENTICADO':
            estatisticas['sessoes_autenticadas'] += 1
            operador = sessao.get('operador', {})
            estatisticas['usuarios_ativos'].append({
                'user_id': user_id,
                'nome': operador.get('nome', 'N/A'),
                'ultimo_acesso': sessao.get('ultimo_acesso')
            })
        elif estado in ['AGUARDANDO_NOME', 'AGUARDANDO_DATA_NASCIMENTO']:
            estatisticas['sessoes_aguardando_login'] += 1
        
        ultimo_acesso = sessao.get('ultimo_acesso', sessao.get('criado_em', agora))
        
        if agora - ultimo_acesso <= timedelta(hours=1):
            estatisticas['sessoes_ativas_1h'] += 1
        
        if agora - ultimo_acesso <= timedelta(hours=24):
            estatisticas['sessoes_ativas_24h'] += 1
    
    return estatisticas

# ===============================================
# ALIASES PARA COMPATIBILIDADE
# ===============================================

# Funções com nomes alternativos para compatibilidade com código existente
async def esta_autenticado(user_id: Union[int, str]) -> bool:
    """Alias para verificar_autenticacao"""
    return await verificar_autenticacao(user_id)

async def obter_operador(user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    """Alias para obter_operador_sessao"""
    return await obter_operador_sessao(user_id)

async def criar_sessao(user_id: Union[int, str], operador_data: Dict[str, Any], estado: str = 'AUTENTICADO') -> None:
    """Alias para iniciar_sessao"""
    await iniciar_sessao(user_id, operador_data, estado)

async def iniciar_nova_sessao(user_id: Union[int, str], estado: str = 'AGUARDANDO_NOME') -> None:
    """Inicia uma nova sessão vazia"""
    await limpar_sessao(user_id)
    await atualizar_sessao(user_id, {'estado': estado})

def obter_sessoes_ativas() -> int:
    """Alias para listar_sessoes_ativas"""
    return listar_sessoes_ativas()

async def limpar_sessao_usuario(user_id: Union[int, str]) -> None:
    """Alias para limpar_sessao"""
    await limpar_sessao(user_id)

def get_session_count() -> int:
    """Alias em inglês para listar_sessoes_ativas"""
    return listar_sessoes_ativas()

async def cleanup_expired_sessions(timeout_hours: int = None) -> int:
    """Alias em inglês para limpar_sessoes_expiradas_async"""
    return await limpar_sessoes_expiradas_async(timeout_hours)

def get_session_stats() -> Dict[str, Any]:
    """Alias em inglês para obter_estatisticas_sessoes"""
    return obter_estatisticas_sessoes()

# ===============================================
# INICIALIZAÇÃO E CONFIGURAÇÃO
# ===============================================

def inicializar_sistema_sessoes() -> None:
    """Inicializa o sistema de sessões"""
    logger.info("Sistema de sessões inicializado")
    logger.info(f"Timeout de sessão: {SESSION_TIMEOUT_HOURS} horas")

# Chamar inicialização ao importar o módulo
inicializar_sistema_sessoes()