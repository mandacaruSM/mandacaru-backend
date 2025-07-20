# backend/apps/bot_telegram/utils/qrcode_utils.py
# Gera QR Codes com link direto para o bot do Telegram com ID do equipamento

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


def gerar_qrcode_para_equipamento(equipamento_id: int, base_url_bot: str) -> ContentFile:
    """
    Gera QR Code com link para o bot contendo ID do equipamento como parâmetro
    Exemplo de URL: https://t.me/SeuBotMandacaruBot?start=eq123
    """
    url = f"{base_url_bot}?start=eq{equipamento_id}"

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    nome_arquivo = f"qrcode_eq{equipamento_id}.png"
    return ContentFile(buffer.getvalue(), name=nome_arquivo)


def gerar_qrcode_base64(equipamento_id: int, base_url_bot: str) -> str:
    """
    Retorna a imagem do QR Code codificada em base64 (para API REST, frontend etc.)
    """
    import base64
    url = f"{base_url_bot}?start=eq{equipamento_id}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
