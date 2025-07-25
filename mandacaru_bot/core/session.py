# =====================
# core/session.py (com timeout automático)
# =====================

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Armazenamento em memória das sessões
sessions: Dict[str, Dict[str, Any]] = {}

# Configuração de timeout (10 minutos)
SESSION_TIMEOUT_MINUTES = 10

class SessionState:
    """Estados possíveis da sessão"""
    AGUARDANDO_NOME = "AGUARDANDO_NOME"
    AGUARDANDO_DATA = "AGUARDANDO_DATA"
    AUTENTICADO = "AUTENTICADO"
    CHECKLIST_ATIVO = "CHECKLIST_ATIVO"
    ABASTECIMENTO_ATIVO = "ABASTECIMENTO_ATIVO"
    OS_ATIVO = "OS_ATIVO"
    FINANCEIRO_ATIVO = "FINANCEIRO_ATIVO"
    QRCODE_ATIVO = "QRCODE_ATIVO"
    EXPIRADA = "EXPIRADA"

def iniciar_sessao(chat_id: str) -> None:
    """Inicia uma nova sessão para o chat_id"""
    sessions[chat_id] = {
        "estado": SessionState.AGUARDANDO_NOME,
        "criado_em": datetime.now(),
        "ultimo_acesso": datetime.now(),
        "operador": None,
        "dados_temporarios": {},
        "timeout_notificado": False
    }

def atualizar_sessao(chat_id: str, chave: str, valor: Any) -> None:
    """Atualiza um valor específico na sessão"""
    if chat_id in sessions:
        sessions[chat_id][chave] = valor
        sessions[chat_id]["ultimo_acesso"] = datetime.now()
        # Reset do timeout quando há atividade
        sessions[chat_id]["timeout_notificado"] = False

def obter_sessao(chat_id: str) -> Dict[str, Any]:
    """Retorna os dados da sessão ou um dict vazio"""
    sessao = sessions.get(chat_id, {})
    if sessao:
        # Verificar se a sessão expirou
        if is_session_expired(chat_id):
            limpar_sessao(chat_id)
            return {}
        else:
            sessao["ultimo_acesso"] = datetime.now()
    return sessao

def limpar_sessao(chat_id: str) -> None:
    """Remove completamente uma sessão"""
    sessions.pop(chat_id, None)

def obter_operador(chat_id: str) -> Optional[Dict[str, Any]]:
    """Retorna os dados do operador autenticado"""
    sessao = sessions.get(chat_id, {})
    if is_session_expired(chat_id):
        return None
    return sessao.get("operador")

def esta_autenticado(chat_id: str) -> bool:
    """Verifica se o usuário está autenticado e a sessão não expirou"""
    if is_session_expired(chat_id):
        return False
    sessao = sessions.get(chat_id, {})
    return sessao.get("estado") == SessionState.AUTENTICADO and sessao.get("operador") is not None

def is_session_expired(chat_id: str) -> bool:
    """Verifica se a sessão expirou (10 minutos de inatividade)"""
    if chat_id not in sessions:
        return True
    
    sessao = sessions[chat_id]
    ultimo_acesso = sessao.get("ultimo_acesso", datetime.now())
    tempo_limite = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    
    return ultimo_acesso < tempo_limite

def get_session_time_remaining(chat_id: str) -> int:
    """Retorna os minutos restantes até a sessão expirar"""
    if chat_id not in sessions:
        return 0
    
    sessao = sessions[chat_id]
    ultimo_acesso = sessao.get("ultimo_acesso", datetime.now())
    tempo_limite = ultimo_acesso + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    tempo_restante = tempo_limite - datetime.now()
    
    return max(0, int(tempo_restante.total_seconds() / 60))

def marcar_timeout_notificado(chat_id: str) -> None:
    """Marca que o usuário foi notificado sobre o timeout"""
    if chat_id in sessions:
        sessions[chat_id]["timeout_notificado"] = True

def ja_foi_notificado_timeout(chat_id: str) -> bool:
    """Verifica se o usuário já foi notificado sobre o timeout"""
    if chat_id not in sessions:
        return False
    return sessions[chat_id].get("timeout_notificado", False)

def definir_dados_temporarios(chat_id: str, dados: Dict[str, Any]) -> None:
    """Define dados temporários para o contexto atual"""
    if chat_id in sessions:
        sessions[chat_id]["dados_temporarios"] = dados
        sessions[chat_id]["ultimo_acesso"] = datetime.now()

def obter_dados_temporarios(chat_id: str) -> Dict[str, Any]:
    """Obtém dados temporários da sessão"""
    sessao = sessions.get(chat_id, {})
    if is_session_expired(chat_id):
        return {}
    return sessao.get("dados_temporarios", {})

def limpar_dados_temporarios(chat_id: str) -> None:
    """Limpa apenas os dados temporários, mantendo a sessão"""
    if chat_id in sessions:
        sessions[chat_id]["dados_temporarios"] = {}
        sessions[chat_id]["ultimo_acesso"] = datetime.now()

def limpar_sessoes_expiradas(tempo_limite_horas: int = 24) -> int:
    """Remove sessões antigas (útil para limpeza periódica)"""
    agora = datetime.now()
    limite = agora - timedelta(hours=tempo_limite_horas)
    
    sessoes_para_remover = []
    for chat_id, sessao in sessions.items():
        ultimo_acesso = sessao.get("ultimo_acesso", agora)
        if ultimo_acesso < limite:
            sessoes_para_remover.append(chat_id)
    
    for chat_id in sessoes_para_remover:
        sessions.pop(chat_id, None)
    
    return len(sessoes_para_remover)

def obter_sessoes_proximas_expiracao() -> list:
    """Retorna lista de chat_ids com sessões que expiram em 2 minutos"""
    sessoes_proximas = []
    agora = datetime.now()
    
    for chat_id, sessao in sessions.items():
        if sessao.get("estado") == SessionState.AUTENTICADO:
            ultimo_acesso = sessao.get("ultimo_acesso", agora)
            tempo_limite = ultimo_acesso + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
            tempo_restante = tempo_limite - agora
            
            # Se restam menos de 2 minutos e ainda não foi notificado
            if 0 < tempo_restante.total_seconds() < 120 and not ja_foi_notificado_timeout(chat_id):
                sessoes_proximas.append(chat_id)
    
    return sessoes_proximas

def obter_estatisticas_sessoes() -> Dict[str, int]:
    """Retorna estatísticas das sessões ativas"""
    total = len(sessions)
    autenticados = sum(1 for s in sessions.values() if s.get("estado") == SessionState.AUTENTICADO)
    expiradas = sum(1 for chat_id in sessions.keys() if is_session_expired(chat_id))
    
    return {
        "total_sessoes": total,
        "usuarios_autenticados": autenticados - expiradas,
        "aguardando_autenticacao": total - autenticados,
        "sessoes_expiradas": expiradas
    }