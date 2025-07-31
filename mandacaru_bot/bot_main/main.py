# ===============================================
# ARQUIVO FASE 2: mandacaru_bot/bot_main/main.py
# Versão com módulos corrigidos
# ===============================================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Imports do core
from core.config import TELEGRAM_TOKEN
from core.session import limpar_sessoes_expiradas

# Imports dos handlers principais
from bot_main.handlers import register_handlers as register_main_handlers

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar instâncias do bot e dispatcher GLOBALMENTE
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
        
        # Tentar carregar módulos específicos
        modules_loaded = 0
        
        # Admin handlers
        try:
            from bot_main.admin_handlers import register_admin_handlers
            register_admin_handlers(dp)
            logger.info("✅ Handlers administrativos registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ Admin handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar admin handlers: {e}")
        
        # Checklist handlers (FASE 2)
        try:
            from bot_checklist.handlers import register_handlers as register_checklist_handlers
            register_checklist_handlers(dp)
            logger.info("✅ Handlers de checklist registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ Checklist handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar checklist handlers: {e}")
        
        # Abastecimento handlers
        try:
            from bot_abastecimento.handlers import register_handlers as register_abastecimento_handlers
            register_abastecimento_handlers(dp)
            logger.info("✅ Handlers de abastecimento registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ Abastecimento handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar abastecimento handlers: {e}")
        
        # OS handlers
        try:
            from bot_os.handlers import register_handlers as register_os_handlers
            register_os_handlers(dp)
            logger.info("✅ Handlers de OS registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ OS handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar OS handlers: {e}")
        
        # Financeiro handlers
        try:
            from bot_financeiro.handlers import register_handlers as register_financeiro_handlers
            register_financeiro_handlers(dp)
            logger.info("✅ Handlers financeiros registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ Financeiro handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar financeiro handlers: {e}")
        
        # QR Code handlers
        try:
            from bot_qrcode.handlers import register_handlers as register_qrcode_handlers
            register_qrcode_handlers(dp)
            logger.info("✅ Handlers de QR Code registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ QR Code handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar QR Code handlers: {e}")
        
        # Equipamento handlers
        try:
            from bot_equipamento.handlers import register_handlers as register_equipamento_handlers
            register_equipamento_handlers(dp)
            logger.info("✅ Handlers de equipamento registrados")
            modules_loaded += 1
        except ImportError:
            logger.info("⚠️ Equipamento handlers não encontrados")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar equipamento handlers: {e}")
        
        logger.info(f"🎉 Handlers registrados: 1 principal + {modules_loaded} módulos específicos")
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar handlers: {e}")
        raise

async def cleanup_task():
    """Task de limpeza periódica"""
    while True:
        try:
            await asyncio.sleep(3600)  # Executar a cada hora
            removed = limpar_sessoes_expiradas(24)
            if removed > 0:
                logger.info(f"🧹 Limpeza: {removed} sessões expiradas removidas")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")

async def main():
    """Função principal do bot"""
    try:
        logger.info("🤖 Iniciando Bot Telegram Mandacaru - FASE 2...")
        
        # Registrar handlers
        await register_all_handlers()
        
        # Iniciar task de limpeza
        cleanup_task_handle = asyncio.create_task(cleanup_task())
        
        # Iniciar bot
        logger.info("🚀 Bot FASE 2 iniciado com sucesso!")
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