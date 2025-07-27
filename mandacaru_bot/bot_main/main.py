# =============================
# bot_main/main.py (corrigido com bot_equipamento)
# =============================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from core.config import TELEGRAM_TOKEN
from core.session import limpar_sessoes_expiradas
from bot_main.handlers import register_handlers as register_main_handlers
from bot_main.admin_handlers import register_admin_handlers
from bot_checklist.handlers import register_handlers as register_checklist_handlers
from bot_abastecimento.handlers import register_handlers as register_abastecimento_handlers
from bot_os.handlers import register_handlers as register_os_handlers
from bot_financeiro.handlers import register_handlers as register_financeiro_handlers
from bot_qrcode.handlers import register_handlers as register_qrcode_handlers
from bot_equipamento.handlers import register_handlers as register_equipamento_handlers  # ← ADICIONADO

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar instâncias do bot e dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def on_startup():
    """Função executada na inicialização do bot"""
    logger.info("🚀 Bot Mandacaru iniciando...")
    
    # Limpar sessões expiradas
    sessoes_removidas = limpar_sessoes_expiradas(24)  # Remove sessões > 24h
    if sessoes_removidas > 0:
        logger.info(f"🧹 Removidas {sessoes_removidas} sessões expiradas")
    
    logger.info("✅ Bot Mandacaru iniciado com sucesso!")

async def on_shutdown():
    """Função executada no encerramento do bot"""
    logger.info("🛑 Bot Mandacaru encerrando...")
    await bot.session.close()
    logger.info("✅ Bot encerrado com sucesso!")

async def periodic_cleanup():
    """Limpeza periódica de sessões (roda a cada hora)"""
    while True:
        await asyncio.sleep(3600)  # 1 hora
        try:
            sessoes_removidas = limpar_sessoes_expiradas(24)
            if sessoes_removidas > 0:
                logger.info(f"🧹 Limpeza automática: {sessoes_removidas} sessões removidas")
        except Exception as e:
            logger.error(f"Erro na limpeza automática: {e}")

def register_all_handlers():
    """Registra todos os handlers dos módulos"""
    logger.info("📝 Registrando handlers...")
    
    # Registrar handlers na ordem correta (main primeiro, admin depois)
    register_main_handlers(dp)
    register_admin_handlers(dp)
    register_checklist_handlers(dp)
    register_abastecimento_handlers(dp)
    register_os_handlers(dp)
    register_financeiro_handlers(dp)
    register_qrcode_handlers(dp)
    register_equipamento_handlers(dp)  # ← ADICIONADO
    
    logger.info("✅ Todos os handlers registrados")

async def main():
    """Função principal"""
    try:
        # Registrar handlers
        register_all_handlers()
        
        # Configurar eventos de startup e shutdown
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Iniciar limpeza automática em background
        cleanup_task = asyncio.create_task(periodic_cleanup())
        
        # Iniciar polling
        logger.info("🔄 Iniciando polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        raise
    finally:
        # Cancelar task de limpeza se ainda estiver rodando
        if 'cleanup_task' in locals():
            cleanup_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        raise