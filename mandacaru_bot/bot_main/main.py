# bot_main/main.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from core.config import TELEGRAM_TOKEN
from bot_main.handlers import register_handlers as register_main_handlers
from bot_checklist.handlers import register_handlers as register_checklist_handlers
from bot_abastecimento.handlers import register_handlers as register_abastecimento_handlers
from bot_os.handlers import register_handlers as register_os_handlers

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
    print("🚀 Bot Mandacaru iniciado com estrutura modular.")

    register_main_handlers(dp)
    register_checklist_handlers(dp)
    register_abastecimento_handlers(dp)
    register_os_handlers(dp)

    await dp.start_polling(bot)
