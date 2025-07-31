#!/usr/bin/env python3
# =============================
# diagnose_windows.py - Diagnóstico compatível com Windows
# =============================

import os
import sys
import subprocess
from pathlib import Path
import importlib.util

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f">> {title}")
    print('='*60)

def check_python_version():
    """Verifica versão do Python"""
    print_header("VERIFICACAO DO PYTHON")
    
    version = sys.version_info
    print(f"[INFO] Versao atual: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERRO] Versao do Python muito antiga")
        print("[ACAO] Instale Python 3.8 ou superior")
        return False
    else:
        print("[OK] Versao do Python adequada")
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
            print(f"[OK] {file_path}")
        else:
            print(f"[ERRO] {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n[AVISO] {len(missing_files)} arquivo(s) faltando")
        return False
    else:
        print("\n[OK] Todos os arquivos necessarios estao presentes")
        return True

def check_directories():
    """Verifica e cria diretórios necessários"""
    print_header("DIRETORIOS")
    
    required_dirs = ["logs", "temp", "data"]
    created_dirs = []
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"[OK] {dir_name}/")
        else:
            print(f"[INFO] {dir_name}/ (criando...)")
            dir_path.mkdir(exist_ok=True)
            (dir_path / ".gitkeep").touch()
            created_dirs.append(dir_name)
            print(f"[OK] {dir_name}/ criado")
    
    if created_dirs:
        print(f"\n[INFO] Criados: {', '.join(created_dirs)}")
    
    return True

def check_env_file():
    """Verifica arquivo .env"""
    print_header("ARQUIVO .ENV")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("[ERRO] Arquivo .env nao encontrado")
        
        if env_example.exists():
            print("[INFO] Copiando .env.example para .env...")
            content = env_example.read_text(encoding='utf-8')
            env_file.write_text(content, encoding='utf-8')
            print("[OK] Arquivo .env criado")
        else:
            print("[ERRO] .env.example tambem nao encontrado")
            return False
    else:
        print("[OK] Arquivo .env encontrado")
    
    # Verificar variáveis essenciais
    try:
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
                print(f"[OK] {var} = {display_value}")
            else:
                print(f"[ERRO] {var} nao configurado")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n[ACAO] Configure as variaveis: {', '.join(missing_vars)}")
            return False
            
    except ImportError:
        print("[ERRO] python-dotenv nao instalado")
        return False
    
    return True

def check_dependencies():
    """Verifica dependências"""
    print_header("DEPENDENCIAS")
    
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
                print(f"[OK] {package}")
            else:
                print(f"[ERRO] {package}")
                missing_packages.append(f"{package}=={version}")
        except ImportError:
            print(f"[ERRO] {package}")
            missing_packages.append(f"{package}=={version}")
    
    if missing_packages:
        print(f"\n[ACAO] Para instalar: pip install {' '.join(missing_packages)}")
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
            print(f"[OK] {module}")
        except ImportError as e:
            print(f"[ERRO] {module}: {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"[AVISO] {module}: {e}")
    
    if failed_imports:
        print(f"\n[ACAO] Problemas de import em: {', '.join(failed_imports)}")
        return False
    
    return True

def test_configuration():
    """Testa configuração básica"""
    print_header("TESTE DE CONFIGURACAO")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        
        # Teste básico de config
        from core.config import TELEGRAM_TOKEN, API_BASE_URL, ADMIN_IDS
        
        print(f"[INFO] Token configurado: {'Sim' if TELEGRAM_TOKEN else 'Nao'}")
        print(f"[INFO] API URL: {API_BASE_URL}")
        print(f"[INFO] Admins configurados: {len(ADMIN_IDS)} usuario(s)")
        
        # Teste de sessão
        from core.session import iniciar_sessao, obter_sessao
        test_chat = "test_123"
        iniciar_sessao(test_chat)
        sessao = obter_sessao(test_chat)
        print(f"[INFO] Sistema de sessoes: {'OK' if sessao else 'ERRO'}")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro de configuracao: {e}")
        return False

def suggest_fixes():
    """Sugere correções"""
    print_header("SUGESTOES DE CORRECAO")
    
    print("[AJUDA] PASSOS RECOMENDADOS:")
    print()
    print("1. Verificar Python:")
    print("   python --version")
    print()
    print("2. Instalar dependencias:")
    print("   pip install -r requirements.txt")
    print()
    print("3. Configurar .env:")
    print("   * Obter token: @BotFather no Telegram")
    print("   * Obter ID admin: @userinfobot no Telegram")
    print("   * Configurar API_BASE_URL")
    print()
    print("4. Verificar API Django:")
    print("   curl http://127.0.0.1:8000/api/operadores/")
    print()
    print("5. Executar bot:")
    print("   python start.py")

def run_diagnostic():
    """Executa diagnóstico completo"""
    print(">> DIAGNOSTICO DO BOT MANDACARU")
    print("Este script ira verificar se tudo esta configurado corretamente.")
    
    checks = [
        ("Python", check_python_version),
        ("Estrutura", check_file_structure),
        ("Diretorios", check_directories),
        ("Arquivo .env", check_env_file),
        ("Dependencias", check_dependencies),
        ("Imports", check_imports),
        ("Configuracao", test_configuration)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"[ERRO] Erro no teste {name}: {e}")
            results[name] = False
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    for name, passed in results.items():
        status = "[OK]" if passed else "[PROBLEMA]"
        print(f"{status} {name}")
    
    print(f"\n[RESULTADO] {passed_checks}/{total_checks} verificacoes passaram")
    
    if passed_checks == total_checks:
        print("\n[SUCESSO] Tudo esta configurado corretamente!")
        print("[ACAO] Execute: python start.py")
    else:
        print(f"\n[AVISO] {total_checks - passed_checks} problema(s) encontrado(s)")
        suggest_fixes()
    
    return passed_checks == total_checks

if __name__ == "__main__":
    # Configurar encoding para Windows
    if sys.platform.startswith('win'):
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.utf8')
        except:
            pass
    
    run_diagnostic()