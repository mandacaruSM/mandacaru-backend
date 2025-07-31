#!/usr/bin/env python3
"""
Script de correção automática para o Bot Mandacaru
Corrige os problemas de funções assíncronas não aguardadas
"""

import os
import shutil
from datetime import datetime
import sys

# Diretório base do bot
BOT_DIR = "mandacaru_bot"

# Backup antes de modificar
def backup_files():
    backup_dir = f"backup_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(BOT_DIR):
        try:
            # Ignorar alguns diretórios problemáticos
            ignore_patterns = shutil.ignore_patterns(
                '__pycache__', '*.pyc', '*.pyo', '.git', 
                'venv', 'env', '.env', '*.log', '*.db'
            )
            shutil.copytree(BOT_DIR, backup_dir, ignore=ignore_patterns)
            print(f"✅ Backup criado em: {backup_dir}")
            return True
        except Exception as e:
            print(f"⚠️  Erro no backup: {e}")
            print("Continuando sem backup completo...")
            return True
    else:
        print(f"❌ Diretório {BOT_DIR} não encontrado!")
        return False

# Correções para cada arquivo
corrections = {
    "bot_main/handlers.py": [
        # Corrigir limpar_sessao sem await
        ("limpar_sessao(chat_id)", "await limpar_sessao(chat_id)"),
        ("limpar_sessao(str(message.chat.id))", "await limpar_sessao(str(message.chat.id))"),
        # Corrigir obter_sessao sem await
        ("sessao = obter_sessao(chat_id)", "sessao = await obter_sessao(chat_id)"),
        ("sessao = obter_sessao(str(message.chat.id))", "sessao = await obter_sessao(str(message.chat.id))"),
    ],
    
    "core/middleware.py": [
        # Corrigir esta_autenticado sem await
        ("if not esta_autenticado(chat_id):", "if not await esta_autenticado(chat_id):"),
        # Corrigir obter_operador sem await
        ("operador = obter_operador(chat_id)", "operador = await obter_operador(chat_id)"),
        ("operador = obter_operador(str(message.chat.id))", "operador = await obter_operador(str(message.chat.id))"),
    ],
    
    "bot_equipamento/handlers.py": [
        # Corrigir atualizar_sessao com parâmetros incorretos
        ('atualizar_sessao(chat_id, "estado", SessionState.EQUIPAMENTO_ATIVO)', 
         'await atualizar_sessao(chat_id, {"estado": SessionState.EQUIPAMENTO_ATIVO})'),
        ('atualizar_sessao(str(message.chat.id), "estado", SessionState.EQUIPAMENTO_ATIVO)',
         'await atualizar_sessao(str(message.chat.id), {"estado": SessionState.EQUIPAMENTO_ATIVO})'),
    ],
    
    "core/session.py": [
        # Garantir que limpar_sessoes_expiradas seja async
        ("def limpar_sessoes_expiradas(", "async def limpar_sessoes_expiradas("),
    ],
    
    "bot_main/admin_handlers.py": [
        # Corrigir limpar_sessoes_expiradas sem await
        ("sessoes_removidas = limpar_sessoes_expiradas(24)", 
         "sessoes_removidas = await limpar_sessoes_expiradas(24)"),
    ]
}

def apply_corrections():
    """Aplica as correções em cada arquivo"""
    total_fixes = 0
    
    for file_path, fixes in corrections.items():
        full_path = os.path.join(BOT_DIR, file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️  Arquivo não encontrado: {full_path}")
            continue
            
        print(f"\n📝 Processando: {file_path}")
        
        try:
            # Ler arquivo
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_fixes = 0
            
            # Aplicar correções
            for find_text, replace_text in fixes:
                if find_text in content:
                    # Contar ocorrências
                    count = content.count(find_text)
                    content = content.replace(find_text, replace_text)
                    print(f"  ✅ Corrigido ({count}x): {find_text[:50]}...")
                    file_fixes += count
                    total_fixes += count
            
            # Salvar se houve mudanças
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  💾 Arquivo salvo com {file_fixes} correções")
            else:
                print(f"  ℹ️  Nenhuma alteração necessária")
                
        except Exception as e:
            print(f"  ❌ Erro ao processar arquivo: {e}")
    
    return total_fixes

def verify_structure():
    """Verifica se a estrutura de diretórios está correta"""
    required_dirs = [
        "bot_main",
        "core", 
        "bot_equipamento"
    ]
    
    missing = []
    for dir_name in required_dirs:
        dir_path = os.path.join(BOT_DIR, dir_name)
        if not os.path.exists(dir_path):
            missing.append(dir_name)
    
    if missing:
        print(f"⚠️  Diretórios faltando: {', '.join(missing)}")
        return False
    return True

def show_manual_fixes():
    """Mostra correções manuais importantes"""
    print("\n📋 Correções Manuais Importantes:")
    print("=" * 50)
    print("\n1. Em bot_main/handlers.py, adicione no topo:")
    print("   from aiogram.fsm.context import FSMContext")
    print("   from aiogram.fsm.state import State, StatesGroup")
    print("\n2. Crie a classe de estados:")
    print("   class AuthStates(StatesGroup):")
    print("       waiting_for_name = State()")
    print("       waiting_for_birth_date = State()")
    print("\n3. Adicione parse_mode nas mensagens:")
    print("   await message.answer('texto', parse_mode='Markdown')")
    print("\n4. Verifique se limpar_sessoes_expiradas retorna int")

def main():
    """Função principal"""
    print("🤖 Script de Correção do Bot Mandacaru")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists(BOT_DIR):
        print(f"❌ Diretório '{BOT_DIR}' não encontrado!")
        print(f"📁 Diretório atual: {os.getcwd()}")
        print("\nCertifique-se de executar o script no diretório pai do 'mandacaru_bot'")
        return
    
    # Verificar estrutura
    print("\n🔍 Verificando estrutura...")
    if not verify_structure():
        response = input("\nContinuar mesmo assim? (s/N): ")
        if response.lower() != 's':
            print("❌ Operação cancelada")
            return
    
    # Fazer backup
    print("\n💾 Fazendo backup...")
    backup_files()
    
    # Aplicar correções
    print("\n🔧 Aplicando correções...")
    total_fixes = apply_corrections()
    
    if total_fixes > 0:
        print(f"\n✅ Total de {total_fixes} correções aplicadas com sucesso!")
    else:
        print("\n⚠️  Nenhuma correção foi necessária")
        print("Pode ser que as correções já foram aplicadas anteriormente")
    
    # Mostrar correções manuais
    show_manual_fixes()
    
    print("\n🚀 Próximos passos:")
    print("1. Revisar as correções aplicadas")
    print("2. Aplicar as correções manuais listadas acima")
    print("3. Testar o bot com: python start.py")
    print("4. Commitar as mudanças no Git")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)