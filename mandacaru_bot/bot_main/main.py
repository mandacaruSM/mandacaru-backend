# ===============================================
# ARQUIVO: mandacaru_bot/bot_main/main.py
# Loop principal do bot - VERSÃO CORRIGIDA
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
    
    # Registrar handlers principais
    register_handlers(dp)
    
    # Registrar handlers de checklist
    try:
        from bot_checklist.handlers import register_handlers as register_checklist_handlers
        register_checklist_handlers(dp)
        logger.info("✅ Handlers de checklist registrados")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar módulo checklist: {e}")
    
    # Registrar handlers de QR Code
    try:
        from bot_qr.handlers import register_handlers as register_qr_handlers
        register_qr_handlers(dp)
        logger.info("✅ Handlers de QR Code registrados")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao carregar módulo QR: {e}")
    
    # Registrar handlers de relatórios
    try:
        from bot_reports.handlers import register_handlers as register_reports_handlers
        register_reports_handlers(dp)
        logger.info("✅ Handlers de relatórios registrados")
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
    
    # Obter informações do bot
    try:
        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
        logger.info(f"🆔 ID: {bot_info.id}")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível obter informações do bot: {e}")
    
    # Iniciar tarefa de limpeza
    asyncio.create_task(cleanup_task())
    logger.info("✅ Tarefa de limpeza iniciada")

async def on_shutdown(bot: Bot):
    """Executado quando o bot é encerrado"""
    logger.info("🛑 Encerrando bot...")
    
    # Fechar sessão do bot
    await bot.session.close()
    logger.info("✅ Sessão do bot fechada")

# ===============================================
# FUNÇÃO PRINCIPAL DE EXECUÇÃO
# ===============================================

async def run_bot():
    """Executa o bot principal"""
    logger.info("🔄 Configurando bot...")
    
    # Criar bot e dispatcher
    bot, dp = await create_bot()
    
    # Configurar eventos de startup e shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        # Iniciar polling
        logger.info("📡 Iniciando polling...")
        await dp.start_polling(
            bot,
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no polling: {e}")
        raise
    finally:
        # Garantir que o bot seja fechado
        await bot.session.close()
        logger.info("👋 Bot encerrado")

# ===============================================
# FUNÇÃO DE TESTE
# ===============================================

async def test_bot_connection():
    """Testa a conexão com o bot do Telegram"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot_info = await bot.get_me()
        await bot.session.close()
        
        logger.info(f"✅ Conexão testada: @{bot_info.username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False

# ===============================================
# MODO DEBUG
# ===============================================

if DEBUG:
    # Configurar logging mais detalhado em modo debug
    logging.getLogger('aiogram').setLevel(logging.INFO)
    logger.info("🔧 Modo DEBUG ativado")