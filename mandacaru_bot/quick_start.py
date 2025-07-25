#!/usr/bin/env python3
# =============================
# quick_start.py - Início Rápido do Bot Mandacaru
# =============================

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🚀 QUICK START - BOT MANDACARU                ║
║                                                              ║
║  Configuração automática e execução rápida                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def step(number, title, description=""):
    """Imprime passo formatado"""
    print(f"\n📍 PASSO {number}: {title}")
    if description:
        print(f"   {description}")

def run_command(command, description=""):
    """Executa comando e mostra resultado"""
    if description:
        print(f"   🔄 {description}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Sucesso")
            return True
        else:
            print(f"   ❌ Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def create_env_template():
    """Cria template do .env com valores padrão"""
    env_content = """# ================================================================
# Bot Telegram Mandacaru - Configuração
# ================================================================

# Token do Bot (obter no @BotFather)
TELEGRAM_BOT_TOKEN=

# URLs da API
BASE_URL=http://127.0.0.1:8000
API_BASE_URL=http://127.0.0.1:8000/api

# IDs de Administradores (separados por vírgula)
# Obter em: @userinfobot
ADMIN_IDS=

# Configurações opcionais
BOT_DEBUG=True
SESSION_TIMEOUT_HOURS=24
LOG_LEVEL=INFO

# Configurações do Django (se aplicável)
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content.strip(), encoding='utf-8')
        print("   ✅ Arquivo .env criado com template")
        return True
    else:
        print("   ℹ️ Arquivo .env já existe")
        return True

def quick_setup():
    """Configuração rápida"""
    print_banner()
    
    print("🎯 Este script irá:")
    print("   • Verificar dependências")
    print("   • Criar estrutura de diretórios")
    print("   • Configurar arquivo .env")
    print("   • Executar diagnóstico")
    print("   • Iniciar o bot")
    
    input("\n🔄 Pressione ENTER para continuar...")
    
    # Passo 1: Verificar Python
    step(1, "Verificando Python")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   ❌ Python {version.major}.{version.minor} muito antigo")
        print("   📋 Instale Python 3.8+")
        return False
    
    # Passo 2: Criar diretórios
    step(2, "Criando estrutura de diretórios")
    directories = ["logs", "temp", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        (Path(directory) / ".gitkeep").touch()
    print("   ✅ Diretórios criados")
    
    # Passo 3: Verificar requirements.txt
    step(3, "Verificando requirements.txt")
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("   ❌ requirements.txt não encontrado")
        
        # Criar requirements básico
        basic_requirements = """aiogram==3.4.1
httpx==0.26.0
python-dotenv==1.0.0
psutil==5.9.8
"""
        requirements_file.write_text(basic_requirements, encoding='utf-8')
        print("   ✅ requirements.txt criado")
    else:
        print("   ✅ requirements.txt encontrado")
    
    # Passo 4: Instalar dependências
    step(4, "Instalando dependências")
    if run_command("pip install -r requirements.txt", "Instalando pacotes..."):
        print("   ✅ Dependências instaladas")
    else:
        print("   ⚠️ Problema na instalação - continue manualmente")
    
    # Passo 5: Criar .env
    step(5, "Configurando arquivo .env")
    create_env_template()
    
    # Passo 6: Executar diagnóstico
    step(6, "Executando diagnóstico")
    if Path("diagnose.py").exists():
        run_command("python diagnose.py", "Verificando configuração...")
    else:
        print("   ℹ️ diagnose.py não encontrado, pulando")
    
    # Passo 7: Instruções finais
    step(7, "CONFIGURAÇÃO MANUAL NECESSÁRIA")
    print("""
   🔑 CONFIGURE O ARQUIVO .env:
   
   1. Token do Bot:
      • Abra o Telegram
      • Procure @BotFather
      • Digite /newbot
      • Copie o token para TELEGRAM_BOT_TOKEN
   
   2. ID de Administrador:
      • Envie mensagem para @userinfobot
      • Copie seu ID numérico para ADMIN_IDS
   
   3. API Django:
      • Certifique-se que Django está rodando
      • Teste: curl http://127.0.0.1:8000/api/operadores/
   """)
    
    # Perguntar se quer executar o bot
    print("\n" + "="*60)
    resposta = input("🤖 Deseja tentar executar o bot agora? (s/N): ").lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        step(8, "EXECUTANDO BOT")
        
        if Path("start.py").exists():
            print("   🚀 Iniciando bot...")
            print("   📋 Pressione Ctrl+C para parar")
            print("   📁 Logs em: logs/bot.log")
            print("\n" + "="*60)
            
            try:
                subprocess.run([sys.executable, "start.py"])
            except KeyboardInterrupt:
                print("\n🛑 Bot interrompido pelo usuário")
        else:
            print("   ❌ start.py não encontrado")
    else:
        print("\n📋 Para executar manualmente:")
        print("   python start.py")
    
    print("\n🎉 Quick Start concluído!")
    print("📖 Consulte INSTALLATION_GUIDE.md para mais detalhes")

if __name__ == "__main__":
    quick_setup()