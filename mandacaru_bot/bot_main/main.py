# ===============================================
# ARQUIVO: mandacaru_bot/bot_main/main.py
# Loop principal do bot - CORRIGIDO E ROBUSTO
# ===============================================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import TELEGRAM_TOKEN, DEBUG
from core.session import limpar_sessoes_expiradas

# Núcleo
from bot_main.handlers import register_handlers as register_main_handlers

# Admin (opcional, com fallback)
try:
    from bot_main.admin_handlers import register_handlers as register_admin_handlers
except Exception:
    def register_admin_handlers(_):  # no-op se módulo não existir
        pass

# Módulos
from bot_checklist.handlers import register_handlers as register_checklist_handlers
from bot_abastecimento.handlers import register_handlers as register_abastecimento_handlers
from bot_os.handlers import register_handlers as register_os_handlers
from bot_financeiro.handlers import register_handlers as register_financeiro_handlers
from bot_qrcode.handlers import register_handlers as register_qrcode_handlers

logger = logging.getLogger(__name__)

# ===============================================
# CONFIGURAÇÃO DO BOT
# ===============================================

async def create_bot() -> tuple[Bot, Dispatcher]:
    """Cria instâncias do bot e dispatcher"""
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Registro único e ordenado dos handlers
    register_main_handlers(dp)
    register_admin_handlers(dp)            # seguro (fallback no-op)
    register_checklist_handlers(dp)
    register_abastecimento_handlers(dp)
    register_os_handlers(dp)
    register_financeiro_handlers(dp)
    register_qrcode_handlers(dp)

    logger.info("✅ Bot e dispatcher configurados")
    return bot, dp

# ===============================================
# TAREFAS EM BACKGROUND
# ===============================================

async def cleanup_task():
    """Limpa sessões expiradas periodicamente."""
    while True:
        try:
            await asyncio.sleep(1800)  # 30 min
            removidas = limpar_sessoes_expiradas()
            if removidas > 0:
                logger.info(f"🧹 Limpeza automática: {removidas} sessões removidas")
        except Exception as e:
            logger.error(f"❌ Erro na tarefa de limpeza: {e}")
            await asyncio.sleep(300)

# ===============================================
# HANDLERS DE EVENTOS
# ===============================================

async def on_startup(bot: Bot):
    logger.info("🚀 Bot iniciado com sucesso! DEBUG=%s", DEBUG)

async def on_shutdown(bot: Bot):
    logger.info("🛑 Bot sendo encerrado...")

# ===============================================
# FUNÇÃO PRINCIPAL DO BOT
# ===============================================

async def run_bot():
    """Função principal para execução do bot"""
    cleanup_task_handle = None
    bot = None
    try:
        bot, dp = await create_bot()
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        cleanup_task_handle = asyncio.create_task(cleanup_task())

        logger.info("🔄 Iniciando polling do bot...")
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logger.error(f"❌ Erro crítico no bot: {e}")
        raise
    finally:
        if cleanup_task_handle:
            cleanup_task_handle.cancel()
        if bot:
            await bot.session.close()
            logger.info("🔒 Sessão do bot fechada")

# ===============================================
# ENTRYPOINT
# ===============================================

if __name__ == "__main__":
    asyncio.run(run_bot())
