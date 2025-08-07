# ===============================================
# ARQUIVO: mandacaru_bot/start.py
# Script principal de inicialização do bot
# ===============================================

import asyncio
import sys
import logging
import signal
import os
from pathlib import Path

# ===============================================
# CONFIGURAÇÃO DE PATHS
# ===============================================

def setup_project_paths():
    """Configura paths do projeto corretamente"""
    # Diretório atual (mandacaru_bot)
    current_dir = Path(__file__).parent
    
    # Diretório raiz do projeto (mandacaru_erp)
    project_root = current_dir.parent
    
    # Adicionar ambos ao Python path
    sys.path.insert(0, str(current_dir))  # mandacaru_bot
    sys.path.insert(0, str(project_root))  # mandacaru_erp
    
    # Definir DJANGO_SETTINGS_MODULE se não estiver definido
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
    
    return current_dir, project_root

# Configurar paths antes de qualquer import
bot_dir, project_root = setup_project_paths()

# ===============================================
# CONFIGURAÇÃO DE LOGGING
# ===============================================

def setup_logging():
    """Configura o sistema de logging"""
    # Criar diretório de logs se não existir
    log_dir = bot_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "bot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configurar logging específico para aiogram
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

# ===============================================
# BANNER DE INICIALIZAÇÃO
# ===============================================

def print_startup_banner():
    """Exibe banner de inicialização"""
    banner = """
╔══════════════════════════════════════╗
║            MANDACARU BOT             ║
║        Sistema de Automação          ║
║         Telegram Bot v1.0            ║
╚══════════════════════════════════════╝
"""
    print(banner)
    print("🚀 Iniciando Mandacaru Bot...")
    print(f"📁 Diretório: {bot_dir}")
    print(f"🐍 Python: {sys.version.split()[0]}")

# ===============================================
# HANDLERS DE SINAL
# ===============================================

def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    logger = logging.getLogger(__name__)
    logger.info(f"🛑 Recebido sinal {signum}. Encerrando bot...")
    sys.exit(0)

# ===============================================
# FUNÇÃO PRINCIPAL
# ===============================================

async def main():
    """Função principal do bot"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar configuração
        logger.info("🔍 Verificando configuração...")
        from core.config import TELEGRAM_TOKEN, API_BASE_URL
        logger.info("✅ Configuração carregada")
        
        # Testar conexão com API
        logger.info("🔌 Testando conexão com API...")
        from core.db import verificar_status_api
        if await verificar_status_api():
            logger.info("✅ Conexão com API estabelecida")
        else:
            logger.warning("⚠️ API não está respondendo, mas continuando...")
        
        # Importar e executar o bot principal
        logger.info("🤖 Iniciando bot...")
        from bot_main.main import run_bot
        await run_bot()
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        raise

def main_wrapper():
    """Wrapper principal com tratamento de erros"""
    logger = logging.getLogger(__name__)
    
    try:
        # Banner de inicialização
        print_startup_banner()
        
        # Configurar logging
        setup_logging()
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Iniciar bot
        logger.info("🔄 Iniciando loop principal do bot...")
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        input("Pressione ENTER para sair...")
    finally:
        logger.info("👋 Bot encerrado")

# ===============================================
# PONTO DE ENTRADA
# ===============================================

if __name__ == "__main__":
    main_wrapper()