from django import template
from django.utils.safestring import mark_safe
from ..qr_manager import QRCodeManager

register = template.Library()

@register.simple_tag
def qr_code_url(obj, tamanho='medium'):
    """Retorna URL do QR code PNG"""
    if hasattr(obj, 'qr_code_png_url'):
        return obj.qr_code_png_url
    return ''

@register.simple_tag
def qr_code_img(obj, tamanho='medium', css_class='qr-code'):
    """Retorna tag img do QR code"""
    url = qr_code_url(obj, tamanho)
    if url:
        return mark_safe(f'<img src="{url}" class="{css_class}" alt="QR Code">')
    return ''

@register.simple_tag
def gerar_qr_code(obj, tamanho='medium', incluir_logo=True):
    """Gera QR code se não existir e retorna URL"""
    if hasattr(obj, 'gerar_qr_png'):
        if not obj.tem_qr_png():
            obj.gerar_qr_png(tamanho, incluir_logo)
        return obj.qr_code_png_url
    return ''
