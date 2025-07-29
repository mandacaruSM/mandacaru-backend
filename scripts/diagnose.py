#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO DO BOT TELEGRAM MANDACARU
Execute este script na raiz do projeto mandacaru_erp
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import importlib.util

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print('='*70)

def print_status(status, message):
    """Imprime status formatado"""
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def check_project_structure():
    """Verifica estrutura do projeto"""
    print_header("ESTRUTURA DO PROJETO")
    
    # Verificar se estamos na raiz do projeto Django
    manage_py = Path("manage.py")
    if not manage_py.exists():
        print_status(False, "Arquivo manage.py não encontrado - execute na raiz do projeto")
        return False
    
    print_status(True, "Arquivo manage.py encontrado")
    
    # Verificar estrutura básica
    essential_paths = {
        "backend/": "Diretório backend",
        "backend/settings.py": "Configurações Django", 
        "backend/apps/": "Apps Django",
        ".env": "Arquivo de configuração",
        "requirements.txt": "Dependências Python"
    }
    
    all_ok = True
    for path, description in essential_paths.items():
        exists = Path(path).exists()
        print_status(exists, f"{description}: {path}")
        if not exists:
            all_ok = False
    
    return all_ok

def check_bot_structure():
    """Verifica estrutura do bot"""
    print_header("ESTRUTURA DO BOT TELEGRAM")
    
    bot_path = Path("mandacaru_bot")
    
    if not bot_path.exists():
        print_status(False, f"Pasta do bot não encontrada: {bot_path}")
        print("   📝 Solução: Verificar se bot está em mandacaru_erp/mandacaru_bot/")
        return False
    
    print_status(True, f"Pasta do bot encontrada: {bot_path}")
    
    # Verificar arquivos essenciais do bot
    bot_files = {
        "start.py": "Script principal do bot",
        "core/__init__.py": "Módulo core",
        "core/config.py": "Configurações do bot",
        "core/db.py": "Acesso à API", 
        "core/session.py": "Gerenciamento de sessões",
        "bot_main/__init__.py": "Módulo principal",
        "bot_main/main.py": "Main do bot",
        "bot_main/handlers.py": "Handlers principais"
    }
    
    all_ok = True
    for file_path, description in bot_files.items():
        full_path = bot_path / file_path
        exists = full_path.exists()
        print_status(exists, f"{description}: {file_path}")
        if not exists:
            all_ok = False
    
    return all_ok

def check_python_dependencies():
    """Verifica dependências Python"""
    print_header("DEPENDÊNCIAS PYTHON")
    
    # Verificar versão do Python
    version = sys.version_info
    python_ok = version.major >= 3 and version.minor >= 8
    print_status(python_ok, f"Python {version.major}.{version.minor}.{version.micro}")
    
    if not python_ok:
        print("   📝 Solução: Instale Python 3.8 ou superior")
        return False
    
    # Verificar dependências do bot
    bot_deps = [
        ("aiogram", "Bot framework"),
        ("httpx", "Cliente HTTP"),
        ("python-dotenv", "Variáveis de ambiente")
    ]
    
    deps_ok = True
    for dep, description in bot_deps:
        try:
            spec = importlib.util.find_spec(dep.replace('-', '_'))
            exists = spec is not None
            print_status(exists, f"{description}: {dep}")
            if not exists:
                deps_ok = False
        except ImportError:
            print_status(False, f"{description}: {dep}")
            deps_ok = False
    
    if not deps_ok:
        print("\n   📝 Solução: pip install aiogram httpx python-dotenv psutil")
    
    return deps_ok

def check_env_configuration():
    """Verifica configuração do .env"""
    print_header("CONFIGURAÇÃO DO AMBIENTE")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_status(False, "Arquivo .env não encontrado")
        print("   📝 Solução: Copie .env.example para .env e configure")
        return False
    
    print_status(True, "Arquivo .env encontrado")
    
    # Verificar variáveis essenciais
    essential_vars = [
        "TELEGRAM_BOT_TOKEN",
        "API_BASE_URL", 
        "ADMIN_IDS"
    ]
    
    try:
        # Carregar variáveis do .env
        env_vars = {}
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        all_vars_ok = True
        for var in essential_vars:
            exists = var in env_vars and env_vars[var]
            print_status(exists, f"Variável {var}")
            if not exists:
                all_vars_ok = False
        
        return all_vars_ok
        
    except Exception as e:
        print_status(False, f"Erro ao ler .env: {e}")
        return False

def check_django_setup():
    """Verifica configuração do Django"""
    print_header("CONFIGURAÇÃO DO DJANGO")
    
    try:
        # Verificar se consegue importar Django
        import django
        print_status(True, f"Django {django.get_version()} importado")
        
        # Tentar configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        
        try:
            django.setup()
            print_status(True, "Django configurado com sucesso")
            
            # Verificar apps instalados
            from django.conf import settings
            
            # Verificar app operadores
            operadores_installed = any('operadores' in app for app in settings.INSTALLED_APPS)
            print_status(operadores_installed, "App operadores instalado")
            
            return True
            
        except Exception as e:
            print_status(False, f"Erro ao configurar Django: {e}")
            return False
            
    except ImportError:
        print_status(False, "Django não instalado")
        print("   📝 Solução: pip install django")
        return False

def check_bot_imports():
    """Verifica imports do bot"""
    print_header("IMPORTS DO BOT")
    
    bot_path = Path("mandacaru_bot")
    if not bot_path.exists():
        print_status(False, "Bot não encontrado - pule esta verificação")
        return False
    
    # Adicionar bot ao path temporariamente
    sys.path.insert(0, str(bot_path))
    
    try:
        # Tentar importar módulos do bot
        imports_to_test = [
            ("core.config", "Configurações do bot"),
            ("core.session", "Sistema de sessões"),
            ("core.db", "Acesso à API"),
            ("bot_main.main", "Main do bot")
        ]
        
        all_imports_ok = True
        for module, description in imports_to_test:
            try:
                importlib.import_module(module)
                print_status(True, f"{description}: {module}")
            except ImportError as e:
                print_status(False, f"{description}: {module} - {e}")
                all_imports_ok = False
            except Exception as e:
                print_status(False, f"{description}: {module} - Erro: {e}")
                all_imports_ok = False
        
        return all_imports_ok
        
    finally:
        # Remover do path
        if str(bot_path) in sys.path:
            sys.path.remove(str(bot_path))

def check_api_endpoints():
    """Verifica endpoints da API"""
    print_header("ENDPOINTS DA API")
    
    try:
        import requests
        
        # URLs para testar
        base_url = "http://127.0.0.1:8000"
        endpoints = [
            "/api/operadores/",
            "/admin/",
            "/bot/operador/login/"
        ]
        
        api_running = False
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                status_ok = response.status_code in [200, 302, 401, 403]  # códigos aceitáveis
                print_status(status_ok, f"Endpoint {endpoint}: {response.status_code}")
                if status_ok:
                    api_running = True
            except requests.exceptions.ConnectionError:
                print_status(False, f"Endpoint {endpoint}: Conexão recusada")
            except Exception as e:
                print_status(False, f"Endpoint {endpoint}: {e}")
        
        if not api_running:
            print("\n   📝 Solução: Inicie o Django com 'python manage.py runserver'")
        
        return api_running
        
    except ImportError:
        print_status(False, "requests não instalado - teste manual necessário")
        print("   📝 Teste manual: curl http://127.0.0.1:8000/api/operadores/")
        return None

def generate_action_plan(results):
    """Gera plano de ação baseado nos resultados"""
    print_header("PLANO DE AÇÃO")
    
    if all(results.values()):
        print("🎉 PARABÉNS! Todos os componentes estão funcionando!")
        print("\n🚀 Próximos passos:")
        print("   1. Execute: python manage.py run_telegram_bot --debug")
        print("   2. Teste o bot no Telegram")
        print("   3. Verifique os logs em mandacaru_bot/logs/")
        return
    
    print("🔧 Itens que precisam ser corrigidos:")
    
    if not results.get('structure'):
        print("\n1. 📁 ESTRUTURA DO PROJETO:")
        print("   • Verifique se está na raiz do projeto Django")
        print("   • Confirme existência dos arquivos essenciais")
    
    if not results.get('bot_structure'):
        print("\n2. 🤖 ESTRUTURA DO BOT:")
        print("   • Mova bot para mandacaru_erp/mandacaru_bot/")
        print("   • Verifique se todos os arquivos do bot existem")
    
    if not results.get('dependencies'):
        print("\n3. 📦 DEPENDÊNCIAS:")
        print("   • Execute: pip install -r requirements.txt")
        print("   • Adicione dependências do bot ao requirements.txt")
    
    if not results.get('env_config'):
        print("\n4. 🔑 CONFIGURAÇÃO:")
        print("   • Configure variáveis no arquivo .env")
        print("   • Obtenha token do bot no @BotFather")
        print("   • Configure ADMIN_IDS com seu ID do Telegram")
    
    if not results.get('django'):
        print("\n5. 🌐 DJANGO:")
        print("   • Verifique configuração do Django")
        print("   • Execute migrações se necessário")
    
    if not results.get('imports'):
        print("\n6. 🔗 IMPORTS:")
        print("   • Corrija erros de importação no bot")
        print("   • Verifique implementação das funções faltantes")
    
    if results.get('api') is False:
        print("\n7. 🌍 API:")
        print("   • Inicie o servidor Django: python manage.py runserver")
        print("   • Verifique se URLs estão configuradas corretamente")

def main():
    """Execução principal do diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO - BOT TELEGRAM MANDACARU")
    print("Este script irá verificar todos os componentes necessários")
    
    # Executar todas as verificações
    results = {
        'structure': check_project_structure(),
        'bot_structure': check_bot_structure(), 
        'dependencies': check_python_dependencies(),
        'env_config': check_env_configuration(),
        'django': check_django_setup(),
        'imports': check_bot_imports(),
        'api': check_api_endpoints()
    }
    
    # Resumo dos resultados
    print_header("RESUMO DO DIAGNÓSTICO")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"⚠️ Pulado: {skipped}")
    
    # Gerar plano de ação
    generate_action_plan(results)
    
    print(f"\n{'='*70}")
    print("🎯 Execute as correções sugeridas e rode o diagnóstico novamente")
    print("📞 Em caso de dúvidas, consulte o plano de correção detalhado")

if __name__ == "__main__":
    main()