#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================
# SCRIPT DE DEBUG DO MÓDULO CHECKLIST
# ===============================================

import asyncio
import sys
from pathlib import Path

async def debug_checklist_module():
    """Debug completo do módulo checklist"""
    print("🔍 DEBUG DO MÓDULO CHECKLIST")
    print("=" * 50)
    
    problemas = []
    
    # 1. Verificar se arquivo handlers.py existe
    print("\n📄 1. VERIFICANDO ARQUIVO HANDLERS")
    print("-" * 30)
    
    handlers_path = Path("bot_checklist/handlers.py")
    if not handlers_path.exists():
        problemas.append("❌ bot_checklist/handlers.py não existe")
        print("❌ Arquivo não encontrado")
    else:
        print("✅ Arquivo encontrado")
        
        # Verificar conteúdo
        try:
            with open(handlers_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar funções essenciais
            funcoes_essenciais = [
                "register_handlers",
                "handle_checklist_callback", 
                "comando_checklist",
                "mostrar_equipamentos_checklist"
            ]
            
            for funcao in funcoes_essenciais:
                if funcao in content:
                    print(f"✅ Função {funcao} encontrada")
                else:
                    print(f"❌ Função {funcao} FALTANDO")
                    problemas.append(f"Função {funcao} não encontrada")
                    
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            problemas.append(f"Erro ao ler handlers.py: {e}")
    
    # 2. Verificar imports do módulo
    print("\n📦 2. TESTANDO IMPORTS")
    print("-" * 30)
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        from bot_checklist.handlers import register_handlers
        print("✅ Import register_handlers OK")
    except ImportError as e:
        print(f"❌ Erro no import: {e}")
        problemas.append(f"Import error: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        problemas.append(f"Erro: {e}")
    
    # 3. Verificar core dependencies
    print("\n⚙️ 3. VERIFICANDO DEPENDÊNCIAS CORE")
    print("-" * 30)
    
    try:
        from core.db import buscar_equipamentos_com_nr12, buscar_checklists_nr12
        print("✅ Funções NR12 da API disponíveis")
    except ImportError as e:
        print(f"❌ Funções NR12 não encontradas: {e}")
        problemas.append(f"Core DB functions missing: {e}")
    
    try:
        from core.session import obter_operador_sessao, verificar_autenticacao
        print("✅ Funções de sessão disponíveis")
    except ImportError as e:
        print(f"❌ Funções de sessão não encontradas: {e}")
        problemas.append(f"Session functions missing: {e}")
    
    # 4. Verificar se está sendo registrado no main
    print("\n🔗 4. VERIFICANDO REGISTRO NO MAIN")
    print("-" * 30)
    
    main_path = Path("bot_main/main.py")
    if main_path.exists():
        try:
            with open(main_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            if "bot_checklist" in main_content:
                print("✅ Módulo checklist importado no main")
            else:
                print("❌ Módulo checklist NÃO registrado no main")
                problemas.append("Módulo não registrado no main.py")
                
        except Exception as e:
            print(f"❌ Erro ao verificar main.py: {e}")
    else:
        print("❌ bot_main/main.py não encontrado")
        problemas.append("main.py não encontrado")
    
    # 5. Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DO DEBUG")
    print("=" * 50)
    
    if not problemas:
        print("🎉 NENHUM PROBLEMA ENCONTRADO!")
        print("✅ Módulo checklist deve estar funcionando")
    else:
        print(f"❌ {len(problemas)} PROBLEMAS ENCONTRADOS:")
        for i, problema in enumerate(problemas, 1):
            print(f"   {i}. {problema}")
    
    return len(problemas) == 0

async def verificar_callback_checklist():
    """Verifica especificamente os callbacks de checklist"""
    print("\n🔍 VERIFICANDO CALLBACKS DE CHECKLIST")
    print("-" * 40)
    
    try:
        # Simular dados de callback
        callback_data_examples = [
            "checklist_equipamentos",
            "checklist_meus", 
            "checklist_pendentes",
            "iniciar_checklist_123",
            "continuar_checklist_456"
        ]
        
        print("📋 Callbacks que devem ser suportados:")
        for data in callback_data_examples:
            print(f"   • {data}")
        
        # Verificar se handler principal existe
        handlers_path = Path("bot_checklist/handlers.py")
        if handlers_path.exists():
            with open(handlers_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "handle_checklist_callback" in content:
                print("✅ Handler principal de callbacks encontrado")
            else:
                print("❌ Handler principal de callbacks NÃO encontrado")
                
            if "F.data.startswith(\"checklist_\")" in content:
                print("✅ Filtro de callbacks configurado")
            else:
                print("❌ Filtro de callbacks NÃO configurado")
        
    except Exception as e:
        print(f"❌ Erro ao verificar callbacks: {e}")

async def main():
    """Função principal"""
    print("🎯 INICIANDO DEBUG COMPLETO DO CHECKLIST")
    
    # Debug principal
    sucesso = await debug_checklist_module()
    
    # Debug específico de callbacks
    await verificar_callback_checklist()
    
    if sucesso:
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Testar o bot manualmente")
        print("2. Verificar logs do bot em execução")
        print("3. Executar: python start.py")
    else:
        print("\n🔧 CORREÇÕES NECESSÁRIAS:")
        print("1. Corrigir problemas listados acima")
        print("2. Verificar se módulo está registrado no main.py")
        print("3. Executar debug novamente")

if __name__ == "__main__":
    asyncio.run(main())