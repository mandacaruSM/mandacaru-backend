# =============================
# ARQUIVO CORRIGIDO: mandacaru_bot/bot_main/main.py
# =============================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Imports do core
from core.config import TELEGRAM_TOKEN
from core.session import limpar_sessoes_expiradas

# Imports dos handlers (apenas os que existem)
from bot_main.handlers import register_handlers as register_main_handlers

# Imports opcionais (apenas se existirem)
try:
    from bot_main.admin_handlers import register_admin_handlers
    ADMIN_HANDLERS_AVAILABLE = True
except ImportError:
    ADMIN_HANDLERS_AVAILABLE = False

try:
    from bot_checklist.handlers import register_handlers as register_checklist_handlers
    CHECKLIST_HANDLERS_AVAILABLE = True
except ImportError:
    CHECKLIST_HANDLERS_AVAILABLE = False

try:
    from bot_abastecimento.handlers import register_handlers as register_abastecimento_handlers
    ABASTECIMENTO_HANDLERS_AVAILABLE = True
except ImportError:
    ABASTECIMENTO_HANDLERS_AVAILABLE = False

try:
    from bot_os.handlers import register_handlers as register_os_handlers
    OS_HANDLERS_AVAILABLE = True
except ImportError:
    OS_HANDLERS_AVAILABLE = False

try:
    from bot_financeiro.handlers import register_handlers as register_financeiro_handlers
    FINANCEIRO_HANDLERS_AVAILABLE = True
except ImportError:
    FINANCEIRO_HANDLERS_AVAILABLE = False

try:
    from bot_qrcode.handlers import register_handlers as register_qrcode_handlers
    QRCODE_HANDLERS_AVAILABLE = True
except ImportError:
    QRCODE_HANDLERS_AVAILABLE = False

try:
    from bot_equipamento.handlers import register_handlers as register_equipamento_handlers
    EQUIPAMENTO_HANDLERS_AVAILABLE = True
except ImportError:
    EQUIPAMENTO_HANDLERS_AVAILABLE = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar instâncias do bot e dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

async def register_all_handlers():
    """Registra todos os handlers disponíveis"""
    try:
        logger.info("📝 Registrando handlers...")
        
        # Handler principal (sempre necessário)
        register_main_handlers(dp)
        logger.info("✅ Handlers principais registrados")
        
        # Handlers opcionais
        if ADMIN_HANDLERS_AVAILABLE:
            register_admin_handlers(dp)
            logger.info("✅ Handlers administrativos registrados")
        
        if CHECKLIST_HANDLERS_AVAILABLE:
            register_checklist_handlers(dp)
            logger.info("✅ Handlers de checklist registrados")
        
        if ABASTECIMENTO_HANDLERS_AVAILABLE:
            register_abastecimento_handlers(dp)
            logger.info("✅ Handlers de abastecimento registrados")
        
        if OS_HANDLERS_AVAILABLE:
            register_os_handlers(dp)
            logger.info("✅ Handlers de OS registrados")
        
        if FINANCEIRO_HANDLERS_AVAILABLE:
            register_financeiro_handlers(dp)
            logger.info("✅ Handlers financeiros registrados")
        
        if QRCODE_HANDLERS_AVAILABLE:
            register_qrcode_handlers(dp)
            logger.info("✅ Handlers de QR Code registrados")
        
        if EQUIPAMENTO_HANDLERS_AVAILABLE:
            register_equipamento_handlers(dp)
            logger.info("✅ Handlers de equipamento registrados")
        
        logger.info("🎉 Todos os handlers disponíveis foram registrados!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar handlers: {e}")
        raise

async def cleanup_task():
    """Task de limpeza periódica"""
    while True:
        try:
            await asyncio.sleep(3600)  # Executar a cada hora
            removed = await limpar_sessoes_expiradas(24)
            if removed > 0:
                logger.info(f"🧹 Limpeza: {removed} sessões expiradas removidas")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")

async def main():
    """Função principal do bot"""
    try:
        logger.info("🤖 Iniciando Bot Telegram Mandacaru...")
        
        # Registrar handlers
        await register_all_handlers()
        
        # Iniciar task de limpeza
        cleanup_task_handle = asyncio.create_task(cleanup_task())
        
        # Iniciar bot
        logger.info("🚀 Bot iniciado com sucesso!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        raise
    finally:
        # Limpeza
        await bot.session.close()
        logger.info("🛑 Bot finalizado")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        exit(1)