from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

class QRCodeAdminMixin:
    """Mixin para adicionar QR codes no admin"""
    
    def qr_code_preview(self, obj):
        """Preview do QR code no admin"""
        if hasattr(obj, 'qr_code_png_url') and obj.qr_code_png_url:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;">',
                obj.qr_code_png_url
            )
        return "Não gerado"
    qr_code_preview.short_description = 'QR Code'
    
    def gerar_qr_action(self, obj):
        """Botão para gerar QR code"""
        if hasattr(obj, 'uuid'):  # Checklist
            url = reverse('admin:gerar_qr_checklist', args=[obj.id])
        else:  # Equipamento
            url = reverse('admin:gerar_qr_equipamento', args=[obj.id])
        
        return format_html(
            '<a class="button" href="{}">Gerar QR PNG</a>',
            url
        )
    gerar_qr_action.short_description = 'Ações'
