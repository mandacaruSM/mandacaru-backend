# ================================================================
# ARQUIVO: backend/apps/bot_telegram/utils/qr_reader.py
# Implementação do leitor de QR Code para o bot Telegram
# ================================================================

import io
import logging
from typing import Optional, Dict, Any, List
from telegram import PhotoSize
from PIL import Image
import cv2
import numpy as np
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import json
import re

logger = logging.getLogger(__name__)


class QRCodeReader:
    """Classe para leitura e processamento de QR Codes"""
    
    def __init__(self):
        self.max_file_size = 20 * 1024 * 1024  # 20MB
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'WEBP']
    
    async def process_photo(self, photo: PhotoSize) -> Optional[str]:
        """Processa uma foto do Telegram e extrai QR Code"""
        try:
            # Baixar arquivo
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Verificar tamanho
            if len(photo_bytes) > self.max_file_size:
                raise ValueError("Arquivo muito grande (máx 20MB)")
            
            # Converter para imagem
            image = Image.open(io.BytesIO(photo_bytes))
            
            # Tentar múltiplos métodos de detecção
            qr_data = self._detect_qr_basic(image)
            if qr_data:
                return qr_data
            
            qr_data = self._detect_qr_preprocessed(image)
            if qr_data:
                return qr_data
            
            qr_data = self._detect_qr_rotated(image)
            if qr_data:
                return qr_data
            
            logger.info("Nenhum QR Code detectado na imagem")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar foto: {e}")
            return None
    
    def _detect_qr_basic(self, image: Image) -> Optional[str]:
        """Detecção básica de QR Code"""
        try:
            decoded_objects = pyzbar.decode(image, symbols=[ZBarSymbol.QRCODE])
            
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            logger.debug(f"Erro na detecção básica: {e}")
        
        return None
    
    def _detect_qr_preprocessed(self, image: Image) -> Optional[str]:
        """Detecção com pré-processamento da imagem"""
        try:
            # Converter para numpy array
            img_array = np.array(image)
            
            # Converter para escala de cinza se necessário
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Aplicar threshold adaptivo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Detectar QR codes
            decoded_objects = pyzbar.decode(thresh, symbols=[ZBarSymbol.QRCODE])
            
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            logger.debug(f"Erro no pré-processamento: {e}")
        
        return None
    
    def _detect_qr_rotated(self, image: Image) -> Optional[str]:
        """Detecção com rotações da imagem"""
        try:
            for angle in [0, 90, 180, 270]:
                rotated = image.rotate(angle, expand=True)
                decoded_objects = pyzbar.decode(
                    np.array(rotated), 
                    symbols=[ZBarSymbol.QRCODE]
                )
                
                if decoded_objects:
                    return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            logger.debug(f"Erro na rotação: {e}")
        
        return None

    def decode_qr_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """Decodifica QR Code diretamente de bytes"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return self._detect_qr_basic(image)
        except Exception as e:
            logger.error(f"Erro ao decodificar QR de bytes: {e}")
            return None

    def decode_qr_from_file(self, file_path: str) -> Optional[str]:
        """Decodifica QR Code de um arquiv"""
        try:
            image = Image.open(file_path)
            return self._detect_qr_basic(image)
        except Exception as e:
            logger.error(f"Erro ao decodificar QR do arquivo: {e}")
            return None


class QRDataProcessor:
    """Processa e interpreta dados extraídos de QR Codes"""
    
    def __init__(self):
        self.qr_reader = QRCodeReader()
    
    def process_qr_data(self, qr_data: str) -> Dict[str, Any]:
        """Processa e identifica o tipo de QR Code"""
        
        # Tentar JSON primeiro
        try:
            data = json.loads(qr_data)
            return self._process_json_qr(data)
        except json.JSONDecodeError:
            pass
        
        # Processar como string
        return self._process_string_qr(qr_data)
    
    def _process_json_qr(self, data: Dict) -> Dict[str, Any]:
        """Processa QR Code no formato JSON"""
        
        # Identificar tipo baseado nas chaves
        if 'operador_id' in data or 'operador' in data:
            return {
                'tipo': 'operador',
                'dados': data,
                'operador_id': data.get('operador_id') or data.get('operador')
            }
        
        elif 'equipamento_id' in data or 'equipamento' in data:
            return {
                'tipo': 'equipamento',
                'dados': data,
                'equipamento_id': data.get('equipamento_id') or data.get('equipamento')
            }
        
        elif 'checklist_id' in data or 'checklist' in data:
            return {
                'tipo': 'checklist',
                'dados': data,
                'checklist_id': data.get('checklist_id') or data.get('checklist')
            }
        
        else:
            return {
                'tipo': 'json_generico',
                'dados': data
            }
    
    def _process_string_qr(self, qr_data: str) -> Dict[str, Any]:
        """Processa QR Code no formato string"""
        
        # Verificar se é URL
        if qr_data.startswith(('http://', 'https://')):
            return self._process_url_qr(qr_data)
        
        # Verificar padrões específicos
        patterns = {
            r'^OP(\d+)$': ('operador', 'operador_id'),
            r'^EQ(\d+)$': ('equipamento', 'equipamento_id'),
            r'^CL(\d+)$': ('checklist', 'checklist_id'),
            r'^OPERADOR:(\d+)$': ('operador', 'operador_id'),
            r'^EQUIPAMENTO:(\d+)$': ('equipamento', 'equipamento_id'),
        }
        
        for pattern, (tipo, campo) in patterns.items():
            match = re.match(pattern, qr_data, re.IGNORECASE)
            if match:
                return {
                    'tipo': tipo,
                    campo: int(match.group(1)),
                    'valor_original': qr_data
                }
        
        # QR Code genérico
        return {
            'tipo': 'texto',
            'valor': qr_data
        }
    
    def _process_url_qr(self, url: str) -> Dict[str, Any]:
        """Processa QR Code que contém URL"""
        
        # Padrões de URL do sistema
        patterns = {
            r'/operador/(\d+)': ('operador', 'operador_id'),
            r'/equipamento/(\d+)': ('equipamento', 'equipamento_id'),
            r'/checklist/(\d+)': ('checklist', 'checklist_id'),
            r'[?&]op=(\w+)': ('operador', 'codigo'),
            r'[?&]eq=(\w+)': ('equipamento', 'codigo'),
        }
        
        for pattern, (tipo, campo) in patterns.items():
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                value = match.group(1)
                # Tentar converter para int se possível
                try:
                    value = int(value)
                except ValueError:
                    pass
                
                return {
                    'tipo': tipo,
                    campo: value,
                    'url_original': url
                }
        
        return {
            'tipo': 'url',
            'valor': url
        }

    def extract_ids_from_qr(self, qr_data: str) -> Dict[str, Optional[int]]:
        """Extrai IDs específicos do QR Code"""
        processed = self.process_qr_data(qr_data)
        
        ids = {
            'operador_id': None,
            'equipamento_id': None,
            'checklist_id': None
        }
        
        if processed['tipo'] in ids.keys():
            key = f"{processed['tipo']}_id"
            if key in processed:
                ids[key] = processed[key]
        
        return ids


# Instância global para facilitar uso
qr_reader = QRCodeReader()
qr_processor = QRDataProcessor()


# Funções de conveniência
async def read_qr_from_photo(photo: PhotoSize) -> Optional[str]:
    """Função de conveniência para ler QR de foto do Telegram"""
    return await qr_reader.process_photo(photo)


def process_qr_content(qr_data: str) -> Dict[str, Any]:
    """Função de conveniência para processar conteúdo do QR"""
    return qr_processor.process_qr_data(qr_data)


def extract_equipment_id(qr_data: str) -> Optional[int]:
    """Extrai ID do equipamento do QR Code"""
    ids = qr_processor.extract_ids_from_qr(qr_data)
    return ids.get('equipamento_id')


def extract_operator_id(qr_data: str) -> Optional[int]:
    """Extrai ID do operador do QR Code"""
    ids = qr_processor.extract_ids_from_qr(qr_data)
    return ids.get('operador_id')


def extract_checklist_id(qr_data: str) -> Optional[int]:
    """Extrai ID do checklist do QR Code"""
    ids = qr_processor.extract_ids_from_qr(qr_data)
    return ids.get('checklist_id')