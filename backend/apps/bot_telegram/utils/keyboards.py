### File: backend/apps/bot_telegram/utils/keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 Identificar Operador", callback_data="identificar_operador")],
        [InlineKeyboardButton("🔧 Listar Equipamentos", callback_data="listar_equipamentos")],
        [InlineKeyboardButton("📋 Checklists", callback_data="listar_checklists")],
        [InlineKeyboardButton("📊 Relatórios", callback_data="menu_relatorios")],
    ]
    return InlineKeyboardMarkup(keyboard)


def help_text():
    return (
        "🤖 *Manual do Bot Mandacaru ERP*\n\n"
        "Use /start para iniciar o bot e /help para exibir esta mensagem."
    )