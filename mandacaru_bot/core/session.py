# =====================
# core/session.py
# =====================

sessions = {}  # chave: chat_id, valor: dict com estado e dados temporários

def iniciar_sessao(chat_id):
    sessions[chat_id] = {"estado": "AGUARDANDO_NOME"}

def atualizar_sessao(chat_id, chave, valor):
    if chat_id in sessions:
        sessions[chat_id][chave] = valor

def obter_sessao(chat_id):
    return sessions.get(chat_id, {})

def limpar_sessao(chat_id):
    sessions.pop(chat_id, None)