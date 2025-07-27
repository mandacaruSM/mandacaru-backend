# mandacaru_bot/bot_equipamento/handlers.py

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from backend.apps.equipamentos.models import Equipamento
from django.core.exceptions import ObjectDoesNotExist

async def handler_qr_code(message: Message, command: CommandStart):
    """Handler para acesso via QR Code: /start=eq:<uuid>"""
    args = command.args  # args depois de /start=
    chat_id = str(message.chat.id)

    if args and args.startswith("eq:"):
        uuid_str = args.split("eq:")[1]

        try:
            equipamento = Equipamento.objects.get(uuid=uuid_str)
            texto = (
                f"🔍 Equipamento encontrado:\n\n"
                f"📌 Nome: {equipamento.nome}\n"
                f"🏷️ Categoria: {equipamento.categoria}\n"
                f"👨‍🔧 Cliente: {equipamento.cliente.razao_social}\n"
                f"🌐 Empreendimento: {equipamento.empreendimento.nome}\n"
                f"⚙️ Status: {equipamento.status_operacional}\n"
                f"⏱️ Horímetro: {equipamento.horimetro} h\n\n"
                f"Escolha uma opção:\n"
                f"/checklist\n"
                f"/abastecimento\n"
                f"/relatorio"
            )
            await message.answer(texto)
        except ObjectDoesNotExist:
            await message.answer("❌ Equipamento não encontrado.")
        return

# REGISTRAR HANDLER
def registrar_handler_qr_code(dp: Dispatcher):
    dp.message.register(handler_qr_code, CommandStart(deep_link=True))
