# backend/apps/bot_telegram/utils/qr_utils.py
import json
from pyzbar import decode
from PIL import Image

def ler_qr_code(image_path):
    """Lê QR code de uma imagem"""
    try:
        image = Image.open(image_path)
        decoded_objects = decode(image)
        
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            
            # Tentar como JSON
            try:
                return json.loads(qr_data)
            except:
                # Retornar como string
                return {"codigo": qr_data}
                
    except Exception as e:
        print(f"Erro ao ler QR: {e}")
        return None