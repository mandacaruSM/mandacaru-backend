import qrcode
from io import BytesIO
import base64
from django.conf import settings

def gerar_qr_code_base64(checklist):
    """Gera QR Code em base64 para um checklist"""
    
    # URL completa do checklist
    base_url = "http://127.0.0.1:8000"
    url = f"{base_url}/api/nr12/checklist/{checklist.uuid}/"
    
    # Criar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Gerar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        'qr_code_base64': f"data:image/png;base64,{img_str}",
        'url': url,
        'equipamento': checklist.equipamento.nome,
        'data': checklist.data_checklist,
        'turno': checklist.turno
    }