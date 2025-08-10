# ===============================================
# ARQUIVO: mandacaru_bot/bot_main/main.py
# Loop principal do bot - CORRIGIDO
# ===============================================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import TELEGRAM_TOKEN, DEBUG
from core.session import limpar_sessoes_expiradas
from .handlers import register_handlers

logger = logging.getLogger(__name__)

# ===============================================
# CONFIGURAÇÃO DO BOT
# ===============================================

async def create_bot() -> tuple[Bot, Dispatcher]:
    """Cria instâncias do bot e dispatcher"""
    
    # Configurar bot com propriedades padrão
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN
        )
    )
    
    # Criar dispatcher
    dp = Dispatcher()
    
    # Registrar handlers
    register_handlers(dp)
    
    # Registrar handlers de checklist - CORREÇÃO AQUI
    try:
        from .handlers import register_checklist_handlers
        register_checklist_handlers(dp)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar módulo checklist: {e}")
    
    # Registrar handlers de QR Code
    try:
        from .handlers import register_qr_handlers
        register_qr_handlers(dp)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar módulo QR: {e}")
    
    # Registrar handlers de relatórios
    try:
        from .handlers import register_reports_handlers
        register_reports_handlers(dp)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar módulo relatórios: {e}")
    
    logger.info("✅ Bot e dispatcher configurados")
    return bot, dp


# ===============================================
# TAREFAS EM BACKGROUND
# ===============================================

async def cleanup_task():
    """Tarefa de limpeza que roda em background"""
    while True:
        try:
            # Limpar sessões expiradas a cada 30 minutos
            await asyncio.sleep(1800)  # 30 minutos
            
            removidas = limpar_sessoes_expiradas()
            if removidas > 0:
                logger.info(f"🧹 Limpeza automática: {removidas} sessões removidas")
                
        except Exception as e:
            logger.error(f"❌ Erro na tarefa de limpeza: {e}")
            await asyncio.sleep(300)  # Tentar novamente em 5 minutos

# ===============================================
# HANDLERS DE EVENTOS
# ===============================================

async def on_startup(bot: Bot):
    """Executado quando o bot inicia"""
    logger.info("🚀 Bot iniciado com sucesso!")

async def on_shutdown(bot: Bot):
    """Executado quando o bot encerra"""
    logger.info("🛑 Bot sendo encerrado...")

# ===============================================
# FUNÇÃO PRINCIPAL DO BOT
# ===============================================

async def run_bot():
    """Função principal para execução do bot"""
    try:
        # Criar bot e dispatcher
        bot, dp = await create_bot()
        
        # Configurar eventos de inicialização/encerramento
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Iniciar tarefa de limpeza em background
        cleanup_task_handle = asyncio.create_task(cleanup_task())
        
        # Iniciar polling
        logger.info("🔄 Iniciando polling do bot...")
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Erro crítico no bot: {e}")
        raise
    finally:
        # Cancelar tarefa de limpeza
        if 'cleanup_task_handle' in locals():
            cleanup_task_handle.cancel()
        
        # Fechar sessão do bot
        if 'bot' in locals():
            await bot.session.close()
            logger.info("🔒 Sessão do bot fechada")

# ===============================================
# PONTO DE ENTRADA (se executado diretamente)
# ===============================================

if __name__ == "__main__":
    asyncio.run(run_bot())