#!/usr/bin/env python3
# =============================
# start_venv.py - Versão corrigida para venv
# =============================

import asyncio
import sys
import logging
from pathlib import Path

def print_startup_banner():
    """Exibe banner de inicialização"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 BOT MANDACARU                          ║
║                                                              ║
║  Sistema de automação para gestão empresarial               ║
║  Versão: 1.0.0                                              ║
║                                                              ║
║  Módulos disponíveis:                                       ║
║  • 📋 Checklist                                             ║
║  • ⛽ Abastecimento                                          ║
║  • 🔧 Ordem de Serviço                                      ║
║  • 💰 Financeiro                                            ║
║  • 📱 QR Code                                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def setup_logging():
    """Configura o sistema de logging"""
    # Criar diretório de logs se não existir
    log_dir = Path("logs")
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

def setup_paths():
    """Configura caminhos necessários"""
    # Adicionar o diretório do projeto ao path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

async def main():
    """Função principal"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Iniciando Bot Mandacaru...")
        
        # Verificar imports básicos
        try:
            from core.config import TELEGRAM_TOKEN, API_BASE_URL
            logger.info("✅ Configuração carregada")
        except Exception as e:
            logger.error(f"❌ Erro na configuração: {e}")
            return
        
        # Importar e executar o bot
        from bot_main.main import main as bot_main
        await bot_main()
        
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
        
        # Configurar paths
        setup_paths()
        
        # Iniciar bot
        logger.info("🔄 Iniciando polling do bot...")
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        input("Pressione ENTER para sair...")
    finally:
        logger.info("👋 Bot encerrado")

if __name__ == "__main__":
    main_wrapper()