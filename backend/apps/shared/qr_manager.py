# backend/apps/shared/qr_manager.py - TOTALMENTE PADRONIZADO

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class UnifiedQRManager:
    """Gerenciador PADRONIZADO de QR codes para todo o sistema"""
    
    def __init__(self):
        # PADRÃO UNIFICADO: media/qr_codes/{tipo}/
        self.base_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Garante que todos os diretórios padronizados existem"""
        subdirs = ['operadores', 'equipamentos', 'checklists', 'temp']
        
        os.makedirs(self.base_dir, exist_ok=True)
        for subdir in subdirs:
            os.makedirs(os.path.join(self.base_dir, subdir), exist_ok=True)
    
    def gerar_qr_operador(self, operador, tamanho='medium'):
        """Gera QR code PADRONIZADO para operador"""
        try:
            # Dados do QR em JSON padronizado
            qr_data = {
                'tipo': 'operador',
                'codigo': operador.codigo,
                'nome': operador.nome,
                'data': getattr(operador, 'qr_code_data', f'OP_{operador.codigo}_{datetime.now().strftime("%Y%m%d")}')
            }
            
            # Configurações
            config = self._get_config(tamanho)
            
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=config['box_size'],
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # Gerar imagem
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # Adicionar informações do operador
            qr_img = self._add_operador_info(qr_img, operador, config)
            
            # PADRÃO: qr_codes/operadores/op_{codigo}_{tamanho}.png
            filename = f"op_{operador.codigo}_{tamanho}.png"
            filepath = os.path.join(self.base_dir, 'operadores', filename)
            qr_img.save(filepath, 'PNG', quality=95)
            
            # URL relativa padronizada
            relative_url = f"qr_codes/operadores/{filename}"
            full_url = settings.MEDIA_URL + relative_url
            
            return {
                'filename': filename,
                'filepath': filepath,
                'url': full_url,
                'relative_path': relative_url,
                'data': qr_data,
                'size': f"{qr_img.width}x{qr_img.height}",
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR operador: {e}")
            raise
    
    def gerar_qr_equipamento(self, equipamento, tamanho='medium'):
        """Gera QR code PADRONIZADO para equipamento"""
        try:
            # URL do bot padronizada
            base_url = getattr(settings, 'TELEGRAM_BOT_URL', 'https://t.me/Mandacarusmbot')
            bot_url = f"{base_url}?start=eq{equipamento.id}"
            
            # Configurações
            config = self._get_config(tamanho)
            
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=config['box_size'],
                border=4,
            )
            qr.add_data(bot_url)
            qr.make(fit=True)
            
            # Gerar imagem
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # Adicionar informações do equipamento
            qr_img = self._add_equipamento_info(qr_img, equipamento, config)
            
            # PADRÃO: qr_codes/equipamentos/eq_{id}_{tamanho}.png
            filename = f"eq_{equipamento.id}_{tamanho}.png"
            filepath = os.path.join(self.base_dir, 'equipamentos', filename)
            qr_img.save(filepath, 'PNG', quality=95)
            
            # URL relativa padronizada
            relative_url = f"qr_codes/equipamentos/{filename}"
            full_url = settings.MEDIA_URL + relative_url
            
            return {
                'filename': filename,
                'filepath': filepath,
                'url': full_url,
                'relative_path': relative_url,
                'bot_url': bot_url,
                'size': f"{qr_img.width}x{qr_img.height}",
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR equipamento: {e}")
            raise
    
    def gerar_qr_checklist(self, checklist, tamanho='medium'):
        """Gera QR code PADRONIZADO para checklist"""
        try:
            # URL do checklist padronizada
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            checklist_url = f"{base_url}/api/nr12/checklist/{checklist.uuid}/"
            
            # Configurações
            config = self._get_config(tamanho)
            
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=config['box_size'],
                border=4,
            )
            qr.add_data(checklist_url)
            qr.make(fit=True)
            
            # Gerar imagem
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # PADRÃO: qr_codes/checklists/check_{uuid}_{tamanho}.png
            filename = f"check_{str(checklist.uuid)[:8]}_{tamanho}.png"
            filepath = os.path.join(self.base_dir, 'checklists', filename)
            qr_img.save(filepath, 'PNG', quality=95)
            
            # URL relativa padronizada
            relative_url = f"qr_codes/checklists/{filename}"
            full_url = settings.MEDIA_URL + relative_url
            
            return {
                'filename': filename,
                'filepath': filepath,
                'url': full_url,
                'relative_path': relative_url,
                'checklist_url': checklist_url,
                'size': f"{qr_img.width}x{qr_img.height}",
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR checklist: {e}")
            raise
    
    def _get_config(self, tamanho):
        """Configurações padronizadas por tamanho"""
        configs = {
            'small': {
                'box_size': 5,
                'font_size': 12,
                'padding': 10,
                'final_size': (150, 200)
            },
            'medium': {
                'box_size': 8,
                'font_size': 16,
                'padding': 20,
                'final_size': (300, 380)
            },
            'large': {
                'box_size': 12,
                'font_size': 24,
                'padding': 30,
                'final_size': (500, 620)
            }
        }
        return configs.get(tamanho, configs['medium'])
    
    def _add_operador_info(self, qr_img, operador, config):
        """Adiciona informações padronizadas do operador"""
        try:
            # Criar nova imagem com espaço para texto
            final_img = Image.new('RGB', config['final_size'], 'white')
            
            # Centralizar QR code
            qr_x = (config['final_size'][0] - qr_img.width) // 2
            qr_y = config['padding']
            final_img.paste(qr_img, (qr_x, qr_y))
            
            # Adicionar texto
            draw = ImageDraw.Draw(final_img)
            try:
                font = ImageFont.truetype("arial.ttf", config['font_size'])
            except:
                font = ImageFont.load_default()
            
            # Texto do operador
            y_text = qr_y + qr_img.height + config['padding']
            
            # Nome (centralizado)
            nome_text = operador.nome[:25]
            bbox = draw.textbbox((0, 0), nome_text, font=font)
            text_width = bbox[2] - bbox[0]
            x_center = (config['final_size'][0] - text_width) // 2
            draw.text((x_center, y_text), nome_text, fill="black", font=font)
            
            # Código (centralizado)
            y_text += config['font_size'] + 5
            codigo_text = f"Código: {operador.codigo}"
            bbox = draw.textbbox((0, 0), codigo_text, font=font)
            text_width = bbox[2] - bbox[0]
            x_center = (config['final_size'][0] - text_width) // 2
            draw.text((x_center, y_text), codigo_text, fill="black", font=font)
            
            # Função (centralizado)
            y_text += config['font_size'] + 5
            funcao_text = f"{operador.funcao} - {operador.setor}"
            bbox = draw.textbbox((0, 0), funcao_text, font=font)
            text_width = bbox[2] - bbox[0]
            x_center = (config['final_size'][0] - text_width) // 2
            draw.text((x_center, y_text), funcao_text, fill="gray", font=font)
            
            return final_img
        except Exception as e:
            logger.warning(f"Erro ao adicionar texto ao QR operador: {e}")
            return qr_img
    
    def _add_equipamento_info(self, qr_img, equipamento, config):
        """Adiciona informações padronizadas do equipamento"""
        try:
            # Criar nova imagem com espaço para texto
            final_img = Image.new('RGB', config['final_size'], 'white')
            
            # Centralizar QR code
            qr_x = (config['final_size'][0] - qr_img.width) // 2
            qr_y = config['padding']
            final_img.paste(qr_img, (qr_x, qr_y))
            
            # Adicionar texto
            draw = ImageDraw.Draw(final_img)
            try:
                font = ImageFont.truetype("arial.ttf", config['font_size'])
            except:
                font = ImageFont.load_default()
            
            # Texto do equipamento
            y_text = qr_y + qr_img.height + config['padding']
            
            # Nome do equipamento (centralizado)
            nome_text = equipamento.nome[:30]
            bbox = draw.textbbox((0, 0), nome_text, font=font)
            text_width = bbox[2] - bbox[0]
            x_center = (config['final_size'][0] - text_width) // 2
            draw.text((x_center, y_text), nome_text, fill="black", font=font)
            
            # ID do equipamento (centralizado)
            y_text += config['font_size'] + 5
            id_text = f"ID: {equipamento.id}"
            bbox = draw.textbbox((0, 0), id_text, font=font)
            text_width = bbox[2] - bbox[0]
            x_center = (config['final_size'][0] - text_width) // 2
            draw.text((x_center, y_text), id_text, fill="black", font=font)
            
            # Cliente (centralizado)
            y_text += config['font_size'] + 5
            cliente_text = equipamento.cliente.razao_social[:25]
            bbox = draw.textbbox((0, 0), cliente_text, font=font)
            text_width = bbox[2] - bbox[0]
            x_center = (config['final_size'][0] - text_width) // 2
            draw.text((x_center, y_text), cliente_text, fill="gray", font=font)
            
            return final_img
        except Exception as e:
            logger.warning(f"Erro ao adicionar texto ao QR equipamento: {e}")
            return qr_img
    
    def limpar_qr_antigos(self, dias=30):
        """Remove QR codes antigos de forma padronizada"""
        import time
        cutoff = time.time() - (dias * 24 * 60 * 60)
        
        removidos = 0
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    removidos += 1
        
        logger.info(f"Removidos {removidos} QR codes antigos")
        return removidos
    
    def migrar_qr_codes_existentes(self):
        """Migra QR codes dos caminhos antigos para o padrão novo"""
        migrados = 0
        
        # Migrar operadores
        old_operadores_dir = os.path.join(settings.MEDIA_ROOT, 'operadores', 'qrcodes')
        if os.path.exists(old_operadores_dir):
            for file in os.listdir(old_operadores_dir):
                if file.endswith('.png'):
                    old_path = os.path.join(old_operadores_dir, file)
                    new_path = os.path.join(self.base_dir, 'operadores', file)
                    
                    # Copiar arquivo
                    import shutil
                    shutil.copy2(old_path, new_path)
                    migrados += 1
        
        # Migrar equipamentos
        old_equipamentos_files = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        if os.path.exists(old_equipamentos_files):
            for file in os.listdir(old_equipamentos_files):
                if file.startswith('qr_equipamento_') and file.endswith('.png'):
                    old_path = os.path.join(old_equipamentos_files, file)
                    new_path = os.path.join(self.base_dir, 'equipamentos', file)
                    
                    # Copiar arquivo
                    import shutil
                    shutil.copy2(old_path, new_path)
                    migrados += 1
        
        return migrados