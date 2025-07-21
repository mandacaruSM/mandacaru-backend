#!/usr/bin/env python3
# =============================
# diagnose.py - Diagnóstico do Bot Mandacaru
# =============================

import os
import sys
import subprocess
from pathlib import Path
import importlib.util

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_python_version():
    """Verifica versão do Python"""
    print_header("VERIFICAÇÃO DO PYTHON")
    
    version = sys.version_info
    print(f"📍 Versão atual: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERRO: Versão do Python muito antiga")
        print("✅ SOLUÇÃO: Instale Python 3.8 ou superior")
        return False
    else:
        print("✅ Versão do Python adequada")
        return True

def check_file_structure():
    """Verifica estrutura de arquivos"""
    print_header("ESTRUTURA DE ARQUIVOS")
    
    required_files = [
        "core/__init__.py",
        "core/config.py",
        "core/db.py",
        "core/session.py",
        "core/middleware.py",
        "core/utils.py",
        "core/templates.py",
        "bot_main/__init__.py",
        "bot_main/main.py",
        "bot_main/handlers.py",
        "bot_main/admin_handlers.py",
        "start.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} arquivo(s) faltando")
        return False
    else:
        print("\n✅ Todos os arquivos necessários estão presentes")
        return True

def check_directories():
    """Verifica e cria diretórios necessários"""
    print_header("DIRETÓRIOS")
    
    required_dirs = ["logs", "temp", "data"]
    created_dirs = []
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (criando...)")
            dir_path.mkdir(exist_ok=True)
            (dir_path / ".gitkeep").touch()
            created_dirs.append(dir_name)
            print(f"✅ {dir_name}/ criado")
    
    if created_dirs:
        print(f"\n📁 Criados: {', '.join(created_dirs)}")
    
    return True

def check_env_file():
    """Verifica arquivo .env"""
    print_header("ARQUIVO .ENV")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        
        if env_example.exists():
            print("📋 Copiando .env.example para .env...")
            content = env_example.read_text(encoding='utf-8')
            env_file.write_text(content, encoding='utf-8')
            print("✅ Arquivo .env criado")
        else:
            print("❌ .env.example também não encontrado")
            return False
    else:
        print("✅ Arquivo .env encontrado")
    
    # Verificar variáveis essenciais
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "API_BASE_URL",
        "BASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mascarar token para segurança
            if "TOKEN" in var:
                display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
            else:
                display_value = value
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} não configurado")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Configure as variáveis: {', '.join(missing_vars)}")
        return False
    
    return True

def check_dependencies():
    """Verifica dependências"""
    print_header("DEPENDÊNCIAS")
    
    required_packages = {
        "aiogram": "3.4.1",
        "httpx": "0.26.0",
        "python-dotenv": "1.0.0",
        "psutil": "5.9.8"
    }
    
    missing_packages = []
    
    for package, version in required_packages.items():
        try:
            module_name = package.replace('-', '_')
            spec = importlib.util.find_spec(module_name)
            if spec:
                print(f"✅ {package}")
            else:
                print(f"❌ {package}")
                missing_packages.append(f"{package}=={version}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(f"{package}=={version}")
    
    if missing_packages:
        print(f"\n📦 Para instalar: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_imports():
    """Verifica imports do projeto"""
    print_header("IMPORTS DO PROJETO")
    
    import_tests = [
        ("core.config", "TELEGRAM_TOKEN, API_BASE_URL"),
        ("core.session", "iniciar_sessao, obter_sessao"),
        ("core.db", "buscar_operador_por_nome"),
        ("core.utils", "Validators, MessageFormatter"),
        ("bot_main.main", "main")
    ]
    
    failed_imports = []
    
    for module, items in import_tests:
        try:
            exec(f"from {module} import {items}")
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"⚠️ {module}: {e}")
    
    if failed_imports:
        print(f"\n⚠️ Problemas de import em: {', '.join(failed_imports)}")
        return False
    
    return True

def test_configuration():
    """Testa configuração básica"""
    print_header("TESTE DE CONFIGURAÇÃO")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        
        # Teste básico de config
        from core.config import TELEGRAM_TOKEN, API_BASE_URL, ADMIN_IDS
        
        print(f"✅ Token configurado: {'Sim' if TELEGRAM_TOKEN else 'Não'}")
        print(f"✅ API URL: {API_BASE_URL}")
        print(f"✅ Admins configurados: {len(ADMIN_IDS)} usuário(s)")
        
        # Teste de sessão
        from core.session import iniciar_sessao, obter_sessao
        test_chat = "test_123"
        iniciar_sessao(test_chat)
        sessao = obter_sessao(test_chat)
        print(f"✅ Sistema de sessões: {'OK' if sessao else 'ERRO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro de configuração: {e}")
        return False

def suggest_fixes():
    """Sugere correções"""
    print_header("SUGESTÕES DE CORREÇÃO")
    
    print("🔧 PASSOS RECOMENDADOS:")
    print()
    print("1. 🐍 Verificar Python:")
    print("   python --version")
    print()
    print("2. 📦 Instalar dependências:")
    print("   pip install -r requirements.txt")
    print()
    print("3. 🔑 Configurar .env:")
    print("   • Obter token: @BotFather no Telegram")
    print("   • Obter ID admin: @userinfobot no Telegram")
    print("   • Configurar API_BASE_URL")
    print()
    print("4. 🌐 Verificar API Django:")
    print("   curl http://127.0.0.1:8000/api/operadores/")
    print()
    print("5. 🚀 Executar bot:")
    print("   python start.py")

def run_diagnostic():
    """Executa diagnóstico completo"""
    print("🤖 DIAGNÓSTICO DO BOT MANDACARU")
    print("Este script irá verificar se tudo está configurado corretamente.")
    
    checks = [
        ("Python", check_python_version),
        ("Estrutura", check_file_structure),
        ("Diretórios", check_directories),
        ("Arquivo .env", check_env_file),
        ("Dependências", check_dependencies),
        ("Imports", check_imports),
        ("Configuração", test_configuration)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Erro no teste {name}: {e}")
            results[name] = False
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    for name, passed in results.items():
        status = "✅ OK" if passed else "❌ PROBLEMA"
        print(f"{status} {name}")
    
    print(f"\n📊 RESULTADO: {passed_checks}/{total_checks} verificações passaram")
    
    if passed_checks == total_checks:
        print("\n🎉 PARABÉNS! Tudo está configurado corretamente!")
        print("🚀 Execute: python start.py")
    else:
        print(f"\n⚠️ {total_checks - passed_checks} problema(s) encontrado(s)")
        suggest_fixes()
    
    return passed_checks == total_checks

if __name__ == "__main__":
    run_diagnostic()