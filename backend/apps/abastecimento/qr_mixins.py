# backend/apps/abastecimento/qr_mixins.py
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models

class EquipamentoQRMixin(models.Model):
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name="QR Code")

    class Meta:
        abstract = True

    def gerar_qr_png(self):
        if not self.id:
            return  # Garante que o ID já existe

        qr_text = f"https://t.me/{self.bot_nome()}?start=eq{self.id}"
        qr_img = qrcode.make(qr_text)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        file_name = f"qr_equipamento_{self.id}.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=["qr_code"])

    def bot_nome(self):
        from django.conf import settings
        return getattr(settings, "TELEGRAM_BOT_USERNAME", "mandacaru_bot")
