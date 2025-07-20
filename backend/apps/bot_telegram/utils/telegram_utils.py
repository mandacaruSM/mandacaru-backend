# backend/apps/bot_telegram/utils/telegram_utils.py
# Funções auxiliares para criar botões e mensagens

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def build_inline_keyboard(buttons: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    """
    Constrói um teclado inline com botões.
    Exemplo de input:
    [ [('Iniciar Checklist', 'menu_checklist')], [('Finalizar OS', 'menu_os')] ]
    """
    keyboard = [[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in buttons]
    return InlineKeyboardMarkup(keyboard)


def build_reply_keyboard(options: list[str], resize: bool = True) -> ReplyKeyboardMarkup:
    """
    Cria teclado de resposta simples (ReplyKeyboard)
    """
    keyboard = [[KeyboardButton(text=opt)] for opt in options]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=resize)


def format_checklist_message(equipamento_nome: str, checklist_data: dict) -> str:
    """
    Formata mensagem de checklist finalizado para envio
    """
    msg = f"\n📅 Checklist NR12 - {equipamento_nome}\n"
    for item, status in checklist_data.items():
        status_icon = '✅' if status else '❌'
        msg += f"{status_icon} {item}\n"
    return msg


def format_os_finalizada(os_data: dict) -> str:
    """
    Formata mensagem para OS finalizada
    """
    return (
        f"🔧 Ordem de Serviço Finalizada:\n"
        f"Equipamento: {os_data['equipamento']}\n"
        f"Serviço: {os_data['descricao']}\n"
        f"Técnico: {os_data['tecnico']}\n"
        f"Data: {os_data['data']}\n"
    )


def format_abastecimento_msg(equipamento: str, quantidade: float, tipo: str, horimetro: float) -> str:
    return (
        f"⛽ Abastecimento registrado:\n"
        f"Equipamento: {equipamento}\n"
        f"Combustível: {tipo}\n"
        f"Quantidade: {quantidade} litros\n"
        f"Horímetro: {horimetro}\n"
    )
