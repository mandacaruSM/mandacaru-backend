# ===============================================
# 1. ATUALIZAR qr_generator.py
# ===============================================

# backend/apps/nr12_checklist/qr_generator.py
import qrcode
import os
from django.conf import settings

def gerar_qr_equipamento_para_bot(equipamento, bot_username='Mandacarusmbot'):
    """
    Gera um QR Code com o link /start=eq:{uuid} para o bot Telegram
    ✅ ATUALIZADO para usar @Mandacarusmbot
    """
    if not equipamento.uuid:
        raise ValueError("Equipamento não possui UUID")

    # Link completo para Telegram
    qr_data = f"https://t.me/{bot_username}?start=eq_{equipamento.uuid}"

    # Caminho para salvar
    pasta = os.path.join('media', 'qr_codes', 'equipamentos')
    os.makedirs(pasta, exist_ok=True)
    caminho_png = os.path.join(pasta, f"{equipamento.uuid}.png")

    # Configurar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Gerar e salvar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(caminho_png)

    return {
        "uuid": equipamento.uuid,
        "url": f"/media/qr_codes/equipamentos/{equipamento.uuid}.png",
        "qr_data": qr_data,
        "equipamento_nome": equipamento.nome if hasattr(equipamento, 'nome') else str(equipamento)
    }