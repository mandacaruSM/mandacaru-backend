# backend/apps/abastecimento/qr_mixins.py

import os
import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

class EquipamentoQRMixin(models.Model):
    """
    Mixin abstrato que adiciona ao Equipamento um campo qr_code
    e gera automaticamente um PNG com QR apontando para BASE_URL/equipamentos/<id>/
    """
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name='QR Code do Equipamento'
    )

    class Meta:
        abstract = True

    def gerar_qr_png(self):
        # URL que o QR deve apontar
        url = f"{settings.BASE_URL}/equipamentos/{self.id}/"

        # tamanho da célula do QR
        box_size = {
            'small': 4,
            'medium': 8,
            'large': 12
        }.get(getattr(settings, 'QR_DEFAULT_SIZE', 'medium'), 8)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=4
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # insere logo se for o caso
        if getattr(settings, 'QR_INCLUDE_LOGO', False):
            logo_path = getattr(settings, 'QR_LOGO_PATH', None)
            if logo_path and os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                # dimensiona o logo para 1/4 do QR
                w, h = img.size
                logo.thumbnail((w//4, h//4), Image.ANTIALIAS)
                pos = ((w - logo.width) // 2, (h - logo.height) // 2)
                img.paste(logo, pos, mask=logo)

        # salva em memória
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"equip_{self.id}.png"

        # atualiza o campo qr_code sem disparar novo save completo
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

        # persiste apenas o campo qr_code
        super().save(update_fields=['qr_code'])
