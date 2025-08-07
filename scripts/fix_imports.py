#!/usr/bin/env python3
# ===============================================
# SCRIPT PARA CORRIGIR IMPORTS PROBLEMÁTICOS
# Executar na pasta mandacaru_bot: python fix_imports.py
# ===============================================

import os
import re
from pathlib import Path

def find_problematic_imports():
    """Encontra imports problemáticos nos arquivos do bot"""
    
    problematic_functions = [
        'buscar_operador_por_chat_id',
        'buscar_operador_por_nome_legado', 
        'validar_login_operador',
        'listar_equipamentos_operador',
        'buscar_checklist_pendente',
    ]
    
    print("🔍 PROCURANDO IMPORTS PROBLEMÁTICOS...")
    
    # Procurar em todos os arquivos Python
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Procurar imports problemáticos
                    for func in problematic_functions:
                        if f'from core.db import' in content and func in content:
                            print(f"❌ ENCONTRADO: {file_path}")
                            print(f"   Função: {func}")
                            
                        if f'import {func}' in content:
                            print(f"❌ ENCONTRADO: {file_path}")
                            print(f"   Import direto: {func}")
                            
                except Exception as e:
                    print(f"⚠️ Erro ao ler {file_path}: {e}")

def check_core_db():
    """Verifica se todas as funções necessárias existem em core/db.py"""
    
    print("\n🔍 VERIFICANDO CORE/DB.PY...")
    
    try:
        with open('core/db.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_functions = [
            'buscar_operador_por_nome',
            'obter_operador_por_chat_id',
            'buscar_operador_por_chat_id',  # alias
            'validar_operador_login',
            'listar_equipamentos',
            'buscar_checklists_nr12',
            'atualizar_item_checklist_nr12',
            'verificar_status_api'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f'async def {func}' not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print("❌ FUNÇÕES FALTANDO EM CORE/DB.PY:")
            for func in missing_functions:
                print(f"   - {func}")
        else:
            print("✅ Todas as funções necessárias estão presentes!")
            
    except FileNotFoundError:
        print("❌ ARQUIVO core/db.py NÃO ENCONTRADO!")

def list_all_python_files():
    """Lista todos os arquivos Python para verificação manual"""
    
    print("\n📁 ARQUIVOS PYTHON ENCONTRADOS:")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                print(f"   {os.path.join(root, file)}")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO DE IMPORTS - BOT MANDACARU")
    print("="*50)
    
    find_problematic_imports()
    check_core_db() 
    list_all_python_files()
    
    print("\n" + "="*50)
    print("✅ DIAGNÓSTICO CONCLUÍDO!")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Corrigir imports problemáticos nos arquivos identificados")
    print("2. Atualizar core/db.py com aliases se necessário")
    print("3. Executar novamente: python start.py")