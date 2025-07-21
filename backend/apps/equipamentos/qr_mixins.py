# ================================================================
# QR MIXINS CORRIGIDO - URLs PADRONIZADAS PARA BOT
# backend/apps/equipamentos/qr_mixins.py (ou backend/apps/abastecimento/qr_mixins.py)
# ================================================================

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
    e gera automaticamente um PNG com QR apontando para URL padronizada do bot
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
        """Gera QR code PNG com URL padronizada para bot"""
        # ✅ URL PADRONIZADA PARA BOT
        url = f"{settings.BASE_URL}/bot/equipamento/{self.id}/"

        # Tamanho da célula do QR
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

        # Inserir logo se configurado
        if getattr(settings, 'QR_INCLUDE_LOGO', False):
            logo_path = getattr(settings, 'QR_LOGO_PATH', None)
            if logo_path and os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                # Dimensiona o logo para 1/4 do QR
                w, h = img.size
                logo.thumbnail((w//4, h//4), Image.Resampling.LANCZOS)
                pos = ((w - logo.width) // 2, (h - logo.height) // 2)
                img.paste(logo, pos, mask=logo)

        # Salvar em memória
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"equip_{self.id}.png"

        # Atualizar o campo qr_code sem disparar novo save completo
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

        # Persistir apenas o campo qr_code
        super().save(update_fields=['qr_code'])

    @property
    def qr_url_completa(self):
        """URL completa que o QR code aponta"""
        return f"{settings.BASE_URL}/bot/equipamento/{self.id}/"

    @property
    def qr_dados_bot(self):
        """Dados para o bot identificar o equipamento"""
        return {
            'tipo': 'equipamento',
            'id': self.id,
            'codigo': getattr(self, 'codigo', f'EQ{self.id}'),
            'nome': self.nome,
            'categoria': self.categoria.codigo if hasattr(self, 'categoria') else 'N/A'
        }