import qrcode
from io import BytesIO
import base64
from django.conf import settings

def gerar_qr_code_equipamento(equipamento):
    """Gera QR Code para um equipamento específico (não checklist)"""
    
    # URL que aponta para o equipamento, não checklist específico
    base_url = getattr(settings, 'BASE_URL', "http://127.0.0.1:8000")
    url = f"{base_url}/api/equipamento/{equipamento.id}/acesso/"
    
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
        'equipamento': {
            'id': equipamento.id,
            'nome': equipamento.nome,
            'codigo': getattr(equipamento, 'codigo', 'N/A'),
            'tipo': getattr(equipamento, 'tipo_nr12', {}).nome if hasattr(equipamento, 'tipo_nr12') and equipamento.tipo_nr12 else 'N/A'
        }
    }

def gerar_qr_codes_todos_equipamentos():
    """Gera QR Codes para todos os equipamentos ativos NR12"""
    try:
        from backend.apps.equipamentos.models import Equipamento
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
    except ImportError:
        return []
    
    resultados = []
    
    for equipamento in equipamentos:
        try:
            qr_data = gerar_qr_code_equipamento(equipamento)
            qr_data['status'] = 'sucesso'
            resultados.append(qr_data)
        except Exception as e:
            resultados.append({
                'equipamento': {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', 'N/A')
                },
                'status': 'erro',
                'erro': str(e)
            })
    
    return resultados

# Manter sua função original para compatibilidade
def gerar_qr_code_base64(checklist):
    """Função original mantida para compatibilidade"""
    # URL completa do checklist
    base_url = getattr(settings, 'BASE_URL', "http://127.0.0.1:8000")
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
        'equipamento': checklist.equipamento.nome if hasattr(checklist, 'equipamento') else 'N/A',
        'data': checklist.data_checklist,
        'turno': checklist.turno
    }

import qrcode
import os

def gerar_qr_equipamento_para_bot(equipamento, bot_username='SeuBotMandacaruBot'):
    """
    Gera um QR Code com o link /start=eq:{uuid} para o bot Telegram
    """
    if not equipamento.uuid:
        raise ValueError("Equipamento não possui UUID")

    # Link completo para Telegram
    qr_data = f"https://t.me/{bot_username}?start=eq:{equipamento.uuid}"

    # Caminho para salvar
    pasta = os.path.join('media', 'qr_codes', 'equipamentos')
    os.makedirs(pasta, exist_ok=True)
    caminho_png = os.path.join(pasta, f"{equipamento.uuid}.png")

    # Gerar QR
    img = qrcode.make(qr_data)
    img.save(caminho_png)

    return {
        "uuid": equipamento.uuid,
        "url": f"/media/qr_codes/equipamentos/{equipamento.uuid}.png",
        "qr_data": qr_data
    }
