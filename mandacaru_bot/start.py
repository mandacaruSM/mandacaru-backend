# =============================
# start.py (melhorado)
# =============================

import asyncio
import sys
import logging
import signal
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot_main.main import main
from core.config import config, LOG_LEVEL, LOG_FILE

def setup_logging():
    """Configura o sistema de logging"""
    # Criar diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configurar logging específico para aiogram
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

def signal_handler(signum, frame):
    """Handler para sinais do sistema"""
    logger = logging.getLogger(__name__)
    logger.info(f"🛑 Recebido sinal {signum}. Encerrando bot...")
    sys.exit(0)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'aiogram',
        'httpx', 
        'python-dotenv',
        'psutil'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Pacotes faltando:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Instale com: pip install " + " ".join(missing_packages))
        sys.exit(1)

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

async def pre_startup_checks():
    """Verificações antes da inicialização"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 Executando verificações pré-inicialização...")
    
    try:
        # Verificar conectividade com API
        from core.db import verificar_status_api
        api_status = await verificar_status_api()
        
        if api_status:
            logger.info("✅ API respondendo corretamente")
        else:
            logger.warning("⚠️ API não está respondendo - continuando mesmo assim")
        
        # Verificar configurações
        from core.config import validar_configuracoes
        validar_configuracoes()
        logger.info("✅ Configurações validadas")
        
        # Limpar sessões antigas na inicialização
        from core.session import limpar_sessoes_expiradas
        sessoes_removidas = limpar_sessoes_expiradas(24)
        if sessoes_removidas > 0:
            logger.info(f"🧹 Removidas {sessoes_removidas} sessões antigas")
        
        logger.info("✅ Verificações pré-inicialização concluídas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nas verificações: {e}")
        return False

def main_wrapper():
    """Wrapper principal com tratamento de erros"""
    logger = logging.getLogger(__name__)
    
    try:
        # Banner de inicialização
        print_startup_banner()
        
        # Configurar logging
        setup_logging()
        logger.info("🚀 Iniciando Bot Mandacaru...")
        
        # Verificar dependências
        check_dependencies()
        logger.info("✅ Dependências verificadas")
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Executar verificações pré-inicialização
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        startup_ok = loop.run_until_complete(pre_startup_checks())
        if not startup_ok:
            logger.error("❌ Falha nas verificações. Abortando inicialização.")
            sys.exit(1)
        
        # Iniciar bot
        logger.info("🔄 Iniciando polling do bot...")
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("👋 Bot encerrado")

if __name__ == "__main__":
    main_wrapper()