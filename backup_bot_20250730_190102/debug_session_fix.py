#!/usr/bin/env python3
# =============================
# debug_session_fix.py - Debug e correção da sessão
# =============================

import sys
from pathlib import Path

# Adicionar path
sys.path.insert(0, str(Path.cwd()))

def debug_session():
    """Debug da sessão atual"""
    from core.session import sessions, SessionState, esta_autenticado, obter_operador
    
    print("=== DEBUG SESSÕES ===")
    print(f"Total de sessões: {len(sessions)}")
    
    for chat_id, sessao in sessions.items():
        print(f"\nCHAT ID: {chat_id}")
        print(f"Estado: {sessao.get('estado')}")
        print(f"Operador: {sessao.get('operador', {}).get('nome', 'Nenhum')}")
        print(f"Último acesso: {sessao.get('ultimo_acesso')}")
        
        # Teste manual da função esta_autenticado
        estado = sessao.get("estado")
        operador = sessao.get("operador")
        
        print(f"Estado atual: {estado}")
        print(f"Estado AUTENTICADO: {SessionState.AUTENTICADO}")
        print(f"Estado CHECKLIST_ATIVO: {SessionState.CHECKLIST_ATIVO}")
        print(f"Operador existe: {operador is not None}")
        
        # Teste da função
        auth_result = esta_autenticado(chat_id)
        print(f"esta_autenticado() retorna: {auth_result}")
        
        # Teste manual
        estados_validos = [
            SessionState.AUTENTICADO,
            SessionState.CHECKLIST_ATIVO,
            SessionState.ABASTECIMENTO_ATIVO,
            SessionState.OS_ATIVO,
            SessionState.FINANCEIRO_ATIVO,
            SessionState.QRCODE_ATIVO
        ]
        
        manual_check = estado in estados_validos and operador is not None
        print(f"Verificação manual: {manual_check}")

def fix_session(chat_id_str):
    """Corrige uma sessão específica"""
    from core.session import sessions, SessionState, atualizar_sessao
    
    chat_id = str(chat_id_str)
    if chat_id in sessions:
        # Forçar estado autenticado se tem operador
        sessao = sessions[chat_id]
        if sessao.get('operador'):
            atualizar_sessao(chat_id, "estado", SessionState.AUTENTICADO)
            print(f"✅ Sessão {chat_id} corrigida para AUTENTICADO")
        else:
            print(f"❌ Sessão {chat_id} não tem operador")
    else:
        print(f"❌ Sessão {chat_id} não encontrada")

if __name__ == "__main__":
    debug_session()
    
    # Se há sessões, oferece correção
    from core.session import sessions
    if sessions:
        chat_id = list(sessions.keys())[0]
        resposta = input(f"\nCorrigir sessão {chat_id}? (s/N): ")
        if resposta.lower() in ['s', 'sim']:
            fix_session(chat_id)
            print("Sessão corrigida! Teste no bot agora.")