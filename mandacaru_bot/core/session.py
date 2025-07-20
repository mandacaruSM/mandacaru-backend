# =====================
# core/session.py (melhorado)
# =====================

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Armazenamento em memória das sessões
sessions: Dict[str, Dict[str, Any]] = {}

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

def iniciar_sessao(chat_id: str) -> None:
    """Inicia uma nova sessão para o chat_id"""
    sessions[chat_id] = {
        "estado": SessionState.AGUARDANDO_NOME,
        "criado_em": datetime.now(),
        "ultimo_acesso": datetime.now(),
        "operador": None,
        "dados_temporarios": {}
    }

def atualizar_sessao(chat_id: str, chave: str, valor: Any) -> None:
    """Atualiza um valor específico na sessão"""
    if chat_id in sessions:
        sessions[chat_id][chave] = valor
        sessions[chat_id]["ultimo_acesso"] = datetime.now()

def obter_sessao(chat_id: str) -> Dict[str, Any]:
    """Retorna os dados da sessão ou um dict vazio"""
    sessao = sessions.get(chat_id, {})
    if sessao:
        sessao["ultimo_acesso"] = datetime.now()
    return sessao

def limpar_sessao(chat_id: str) -> None:
    """Remove completamente uma sessão"""
    sessions.pop(chat_id, None)

def obter_operador(chat_id: str) -> Optional[Dict[str, Any]]:
    """Retorna os dados do operador autenticado"""
    sessao = sessions.get(chat_id, {})
    return sessao.get("operador")

def esta_autenticado(chat_id: str) -> bool:
    """Verifica se o usuário está autenticado"""
    sessao = sessions.get(chat_id, {})
    return sessao.get("estado") == SessionState.AUTENTICADO and sessao.get("operador") is not None

def definir_dados_temporarios(chat_id: str, dados: Dict[str, Any]) -> None:
    """Define dados temporários para o contexto atual"""
    if chat_id in sessions:
        sessions[chat_id]["dados_temporarios"] = dados
        sessions[chat_id]["ultimo_acesso"] = datetime.now()

def obter_dados_temporarios(chat_id: str) -> Dict[str, Any]:
    """Obtém dados temporários da sessão"""
    sessao = sessions.get(chat_id, {})
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

def obter_estatisticas_sessoes() -> Dict[str, int]:
    """Retorna estatísticas das sessões ativas"""
    total = len(sessions)
    autenticados = sum(1 for s in sessions.values() if s.get("estado") == SessionState.AUTENTICADO)
    
    return {
        "total_sessoes": total,
        "usuarios_autenticados": autenticados,
        "aguardando_autenticacao": total - autenticados
    }