# =============================
# start.py (ajustado para estrutura mandacaru_erp)
# =============================

import asyncio
import sys
import logging
import signal
import os
from pathlib import Path

# Configurar paths para a estrutura mandacaru_erp/mandacaru_bot/
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

# Agora importar os módulos do bot
from bot_main.main import main
from core.config import config, LOG_LEVEL, LOG_FILE
from core.config import API_BASE_URL, ADMIN_IDS

def setup_logging():
    """Configura o sistema de logging"""
    # Criar diretório de logs se não existir
    log_dir = bot_dir / "logs"
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
    module_mapping = {
        'aiogram': 'aiogram',
        'httpx': 'httpx',
        'python-dotenv': 'dotenv',
        'psutil': 'psutil',
    }

    missing_packages = []
    installed_versions = []
    
    for package, module in module_mapping.items():
        try:
            imported_module = __import__(module)
            version = getattr(imported_module, '__version__', 'desconhecida')
            installed_versions.append(f"{package}=={version}")
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Pacotes faltando:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Instale com: pip install " + " ".join(missing_packages))
        sys.exit(1)
    else:
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Dependências OK: {', '.join(installed_versions)}")

def validate_environment():
    """Valida variáveis de ambiente obrigatórias"""
    logger = logging.getLogger(__name__)
    
    required_vars = {
        'TELEGRAM_TOKEN': 'Token do bot Telegram',
        'API_BASE_URL': 'URL base da API',
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = getattr(config, var, None) if hasattr(config, var) else None
        if not value:
            missing_vars.append(f"{var} ({description})")
        else:
            # Mascarar token nos logs
            if 'TOKEN' in var:
                logger.info(f"✅ {var}: {'*' * 20}...{value[-5:]}")
            else:
                logger.info(f"✅ {var}: {value}")
    
    if missing_vars:
        logger.error("❌ Variáveis de ambiente faltando:")
        for var in missing_vars:
            logger.error(f"   • {var}")
        logger.error("Configure o arquivo .env antes de continuar")
        sys.exit(1)

def print_startup_banner():
    """Exibe banner de inicialização com informações do projeto"""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 BOT MANDACARU                          ║
║                                                              ║
║  Sistema de automação para gestão empresarial               ║
║  Versão: 1.0.0                                              ║
║                                                              ║
║  📁 Projeto: {project_root.name}                              ║
║  🤖 Bot dir: {bot_dir.name}                                   ║
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

def print_startup_status():
    """Exibe status detalhado na inicialização"""
    logger = logging.getLogger(__name__)
    
    try:
        print("\n📊 STATUS DO SISTEMA:")
        print(f"   🏠 Projeto: {project_root}")
        print(f"   🤖 Bot: {bot_dir}")
        print(f"   🌐 API: {API_BASE_URL}")
        print(f"   👥 Admins: {len(ADMIN_IDS)} configurado(s)")
        print(f"   📁 Logs: {bot_dir}/logs/{LOG_FILE}")
        
        # Verificar recursos do sistema
        import psutil
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        
        print(f"   💾 Memória: {memory.available // 1024 // 1024}MB disponível")
        print(f"   🔥 CPU: {cpu_count} core(s)")
        print("")
        
    except Exception as e:
        logger.warning(f"⚠️ Erro ao exibir status: {e}")

async def pre_startup_checks():
    """Verificações antes da inicialização"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 Executando verificações pré-inicialização...")
    
    try:
        # 1. Validar configurações
        validate_environment()
        
        # 2. Verificar conectividade com API
        from core.db import verificar_status_api
        api_status = await verificar_status_api()
        
        if api_status:
            logger.info("✅ API respondendo corretamente")
        else:
            logger.warning("⚠️ API não está respondendo")
            
            # Tentar algumas vezes antes de continuar
            for tentativa in range(3):
                logger.info(f"🔄 Tentativa {tentativa + 1}/3 de reconexão...")
                await asyncio.sleep(2)
                api_status = await verificar_status_api()
                if api_status:
                    logger.info("✅ API respondeu após tentativa")
                    break
            else:
                logger.warning("⚠️ API indisponível - continuando mesmo assim")
        
        # 3. Verificar permissões de escrita
        log_dir = bot_dir / "logs"
        try:
            test_file = log_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✅ Permissões de escrita OK")
        except Exception as e:
            logger.error(f"❌ Erro de permissões: {e}")
            return False
        
        # 4. Limpar sessões antigas
        from core.session import limpar_sessoes_expiradas
        sessoes_removidas = limpar_sessoes_expiradas(24)
        if sessoes_removidas > 0:
            logger.info(f"🧹 Removidas {sessoes_removidas} sessões antigas")
        
        # 5. Verificar estrutura de arquivos
        required_files = [
            bot_dir / "core" / "config.py",
            bot_dir / "core" / "session.py", 
            bot_dir / "bot_main" / "main.py"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                logger.error(f"❌ Arquivo necessário não encontrado: {file_path}")
                return False
        
        logger.info("✅ Estrutura de arquivos OK")
        logger.info("✅ Todas as verificações passaram com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nas verificações: {e}", exc_info=True)
        return False

def main_wrapper():
    """Wrapper principal com tratamento de erros"""
    logger = logging.getLogger(__name__)
    
    try:
        # Banner de inicialização
        print_startup_banner()
        print_startup_status()
        
        # Configurar logging
        setup_logging()
        logger.info("🚀 Iniciando Bot Mandacaru...")
        logger.info(f"📁 Diretório do projeto: {project_root}")
        logger.info(f"🤖 Diretório do bot: {bot_dir}")
        
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
        logger.info("📋 Pressione Ctrl+C para parar o bot")
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}", exc_info=True)
        input("\n⏸️ Pressione ENTER para sair...")
        sys.exit(1)
    finally:
        logger.info("👋 Bot encerrado")

if __name__ == "__main__":
    main_wrapper()