#!/usr/bin/env python3
"""
Script para corrigir o erro de sintaxe no session.py
Remove async duplicado
"""

import os
import re

# Caminho do arquivo
file_path = "mandacaru_bot/core/session.py"

print("🔧 Corrigindo erro de sintaxe em session.py...")

try:
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(file_path + '.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Backup criado: session.py.backup")
    
    # Corrigir async duplicado
    # Procurar por "async async def" e substituir por "async def"
    content = re.sub(r'async\s+async\s+def', 'async def', content)
    
    # Procurar especificamente pela linha problemática
    content = content.replace('async async def limpar_sessoes_expiradas', 'async def limpar_sessoes_expiradas')
    
    # Salvar correção
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Correção aplicada com sucesso!")
    print("\n📝 Verifique se a função está correta:")
    print("   async def limpar_sessoes_expiradas(timeout_hours: int = 24) -> int:")
    
except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {file_path}")
    print("Certifique-se de executar o script no diretório correto")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n🚀 Agora tente executar o bot novamente:")
print("   python manage.py run_telegram_bot --debug")