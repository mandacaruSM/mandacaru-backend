#!/usr/bin/env python3
# =============================
# setup.py - Configuração inicial do Bot Mandacaru
# =============================

import os
import sys
from pathlib import Path
import subprocess

def print_banner():
    """Exibe banner de setup"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🛠️  SETUP BOT MANDACARU                       ║
║                                                              ║
║  Script de configuração inicial                             ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def create_directory_structure():
    """Cria estrutura de diretórios necessária"""
    print("📁 Criando estrutura de diretórios...")
    
    directories = [
        "logs",
        "logs/archived",
        "data",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    # Criar .gitkeep nos diretórios vazios
    for directory in directories:
        gitkeep = Path(directory) / ".gitkeep"
        gitkeep.touch()

def create_env_file():
    """Cria arquivo .env se não existir"""
    print("\n🔧 Configurando arquivo de ambiente...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("   ℹ️ Arquivo .env já existe")
        return
    
    if env_example.exists():
        # Copiar .env.example para .env
        content = env_example.read_text(encoding='utf-8')
        env_file.write_text(content, encoding='utf-8')
        print("   ✅ Arquivo .env criado a partir do .env.example")
        print("   ⚠️ LEMBRE-SE: Configure as variáveis no arquivo .env")
    else:
        print("   ❌ Arquivo .env.example não encontrado")

def check_python_version():
    """Verifica versão do Python"""
    print("\n🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python {version.major}.{version.minor} não suportado")
        print("   📋 Versão mínima requerida: Python 3.8+")
        return False
    else:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} OK")
        return True

def install_dependencies():
    """Instala dependências"""
    print("\n📦 Instalando dependências...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("   ❌ Arquivo requirements.txt não encontrado")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print("   ✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro ao instalar dependências: {e}")
        return False

def check_required_packages():
    """Verifica se os pacotes necessários estão instalados"""
    print("\n🔍 Verificando pacotes necessários...")
    
    required_packages = [
        "aiogram",
        "httpx",
        "python-dotenv",
        "psutil"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_configuration():
    """Testa configuração básica"""
    print("\n🧪 Testando configuração...")
    
    try:
        # Adicionar o diretório atual ao path
        sys.path.insert(0, str(Path.cwd()))
        
        # Testar imports básicos
        from core.config import TELEGRAM_TOKEN, API_BASE_URL
        
        if not TELEGRAM_TOKEN:
            print("   ❌ TELEGRAM_BOT_TOKEN não configurado no .env")
            return False
        
        if not API_BASE_URL:
            print("   ❌ API_BASE_URL não configurado no .env")
            return False
        
        print("   ✅ Configuração básica OK")
        return True
        
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro de configuração: {e}")
        return False

def create_gitignore():
    """Cria .gitignore se não existir"""
    print("\n📝 Configurando .gitignore...")
    
    gitignore_content = """
# Logs
logs/*.log
logs/*.txt
!logs/.gitkeep

# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
temp/
*.tmp
*.temp

# Bot specific
data/sessions.json
data/cache/
    """.strip()
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print("   ✅ Arquivo .gitignore criado")
    else:
        print("   ℹ️ Arquivo .gitignore já existe")

def print_next_steps():
    """Exibe próximos passos"""
    print("\n" + "="*60)
    print("🎉 SETUP CONCLUÍDO!")
    print("="*60)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1. 🔑 Configure o arquivo .env:")
    print("   • TELEGRAM_BOT_TOKEN=seu_token_aqui")
    print("   • API_BASE_URL=http://127.0.0.1:8000/api")
    print("   • ADMIN_IDS=seu_id_telegram")
    
    print("\n2. 🤖 Obtenha o token do bot:")
    print("   • Abra o Telegram")
    print("   • Procure por @BotFather")
    print("   • Digite /newbot e siga as instruções")
    
    print("\n3. 👤 Obtenha seu ID do Telegram:")
    print("   • Envie uma mensagem para @userinfobot")
    print("   • Copie o ID numérico")
    
    print("\n4. 🚀 Execute o bot:")
    print("   • python start.py")
    print("   • Ou: python manage.py run_telegram_bot (Django)")
    
    print("\n5. ✅ Teste o bot:")
    print("   • Procure seu bot no Telegram")
    print("   • Digite /start")
    print("   • Faça login com nome e data de nascimento")
    
    print("\n" + "="*60)

def main():
    """Função principal do setup"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Criar estrutura
    create_directory_structure()
    create_env_file()
    create_gitignore()
    
    # Instalar dependências
    if not install_dependencies():
        print("\n⚠️ Falha na instalação de dependências")
        print("Execute manualmente: pip install -r requirements.txt")
    
    # Verificar pacotes
    if not check_required_packages():
        print("\n⚠️ Alguns pacotes estão faltando")
        print("Execute: pip install -r requirements.txt")
    
    # Testar configuração
    test_configuration()
    
    # Próximos passos
    print_next_steps()

if __name__ == "__main__":
    main()