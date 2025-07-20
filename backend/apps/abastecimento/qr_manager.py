import os
import qrcode
from django.conf import settings

class QRCodeManager:
    def __init__(self):
        self.qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(self.qr_dir, exist_ok=True)

    def gerar_qr_equipamento(self, equipamento, tamanho='medium'):
        """Gera QR code PNG para o equipamento"""
        qr_text = equipamento.bot_link
        filename = f"eq_{equipamento.id}_{tamanho}.png"
        pasta = os.path.join(self.qr_dir, 'equipamentos')
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, filename)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size_por_tamanho(tamanho),
            border=2,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(caminho)

        return caminho

    def box_size_por_tamanho(self, tamanho):
        """Define tamanho do box do QR"""
        return {
            'small': 4,
            'medium': 6,
            'large': 10
        }.get(tamanho, 6)
