# ================================================================
# ARQUIVO: backend/apps/nr12_checklist/qr_manager.py
# Sistema completo de geração e gestão de QR codes PNG
# ================================================================

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import logging
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class QRCodeManager:
    """Gerenciador completo de QR codes PNG"""
    
    def __init__(self):
        self.qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        self.ensure_qr_directory()
    
    def ensure_qr_directory(self):
        """Garante que o diretório de QR codes existe"""
        os.makedirs(self.qr_dir, exist_ok=True)
        
        # Criar subdiretórios
        subdirs = ['checklists', 'equipamentos', 'temp']
        for subdir in subdirs:
            os.makedirs(os.path.join(self.qr_dir, subdir), exist_ok=True)
    
    def gerar_qr_checklist(self, checklist, tamanho='medium', incluir_logo=True):
        """
        Gera QR code PNG para checklist
        
        Args:
            checklist: Instância do ChecklistNR12
            tamanho: 'small', 'medium', 'large'
            incluir_logo: Se deve incluir logo da empresa
        
        Returns:
            dict: Informações do QR code gerado
        """
        try:
            # Configurações por tamanho
            config = self._get_size_config(tamanho)
            
            # URL do checklist
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            url = f"{base_url}/qr/{checklist.uuid}/"
            
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=config['box_size'],
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Gerar imagem base
            qr_img = qr.make_image(
                fill_color="black", 
                back_color="white"
            ).convert('RGB')
            
            # Adicionar informações ao QR code
            if config['add_text']:
                qr_img = self._add_text_to_qr(qr_img, checklist, config)
            
            # Adicionar logo se solicitado
            if incluir_logo and config['add_logo']:
                qr_img = self._add_logo_to_qr(qr_img, config)
            
            # Salvar arquivo
            filename = self._generate_filename(checklist, tamanho)
            filepath = os.path.join(self.qr_dir, 'checklists', filename)
            
            qr_img.save(filepath, 'PNG', quality=95)
            
            # URL para acesso
            qr_url = f"{settings.MEDIA_URL}qr_codes/checklists/{filename}"
            
            # Informações do QR gerado
            qr_info = {
                'filename': filename,
                'filepath': filepath,
                'url': qr_url,
                'checklist_url': url,
                'size': f"{qr_img.width}x{qr_img.height}",
                'file_size': os.path.getsize(filepath),
                'created_at': datetime.now().isoformat(),
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid),
                    'equipamento': checklist.equipamento.nome,
                    'cliente': checklist.equipamento.cliente.razao_social,
                    'data': checklist.data_checklist.strftime('%d/%m/%Y'),
                    'turno': checklist.turno
                }
            }
            
            logger.info(f"✅ QR code gerado: {filename} ({qr_img.width}x{qr_img.height})")
            return qr_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar QR code: {e}")
            raise
    
    def gerar_qr_equipamento(self, equipamento, tamanho='medium'):
        """
        Gera QR code PNG permanente para equipamento
        
        Args:
            equipamento: Instância do Equipamento
            tamanho: 'small', 'medium', 'large'
        
        Returns:
            dict: Informações do QR code gerado
        """
        try:
            config = self._get_size_config(tamanho)
            
            # URL do equipamento
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            url = f"{base_url}/equipamento/{equipamento.id}/"
            
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta correção para durabilidade
                box_size=config['box_size'],
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Gerar imagem
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # Adicionar informações do equipamento
            if config['add_text']:
                qr_img = self._add_equipment_text(qr_img, equipamento, config)
            
            # Adicionar logo
            if config['add_logo']:
                qr_img = self._add_logo_to_qr(qr_img, config)
            
            # Salvar arquivo
            filename = f"eq_{equipamento.id}_{tamanho}.png"
            filepath = os.path.join(self.qr_dir, 'equipamentos', filename)
            
            qr_img.save(filepath, 'PNG', quality=95)
            
            # URL para acesso
            qr_url = f"{settings.MEDIA_URL}qr_codes/equipamentos/{filename}"
            
            return {
                'filename': filename,
                'filepath': filepath,
                'url': qr_url,
                'equipamento_url': url,
                'size': f"{qr_img.width}x{qr_img.height}",
                'file_size': os.path.getsize(filepath),
                'equipamento': {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', f"EQ{equipamento.id}"),
                    'cliente': equipamento.cliente.razao_social
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar QR equipamento: {e}")
            raise
    
    def gerar_batch_qr_codes(self, checklists, tamanho='medium', incluir_logo=True):
        """
        Gera QR codes em lote para múltiplos checklists
        
        Args:
            checklists: Lista de ChecklistNR12
            tamanho: Tamanho dos QR codes
            incluir_logo: Se deve incluir logo
        
        Returns:
            list: Lista com informações dos QR codes gerados
        """
        resultados = []
        
        for checklist in checklists:
            try:
                qr_info = self.gerar_qr_checklist(checklist, tamanho, incluir_logo)
                resultados.append(qr_info)
            except Exception as e:
                logger.error(f"❌ Erro no checklist {checklist.id}: {e}")
                resultados.append({
                    'error': str(e),
                    'checklist_id': checklist.id
                })
        
        logger.info(f"✅ Batch concluído: {len(resultados)} QR codes processados")
        return resultados
    
    def _get_size_config(self, tamanho):
        """Retorna configurações baseadas no tamanho"""
        configs = {
            'small': {
                'box_size': 8,
                'font_size': 16,
                'add_text': True,
                'add_logo': False,
                'text_height': 60,
                'logo_size': (40, 40)
            },
            'medium': {
                'box_size': 10,
                'font_size': 20,
                'add_text': True,
                'add_logo': True,
                'text_height': 80,
                'logo_size': (60, 60)
            },
            'large': {
                'box_size': 15,
                'font_size': 28,
                'add_text': True,
                'add_logo': True,
                'text_height': 120,
                'logo_size': (80, 80)
            }
        }
        return configs.get(tamanho, configs['medium'])
    
    def _add_text_to_qr(self, qr_img, checklist, config):
        """Adiciona texto informativo ao QR code"""
        try:
            # Criar nova imagem com espaço para texto
            text_height = config['text_height']
            new_height = qr_img.height + text_height
            new_img = Image.new('RGB', (qr_img.width, new_height), 'white')
            
            # Colar QR code no topo
            new_img.paste(qr_img, (0, 0))
            
            # Adicionar texto
            draw = ImageDraw.Draw(new_img)
            
            try:
                font = ImageFont.truetype("arial.ttf", config['font_size'])
                font_small = ImageFont.truetype("arial.ttf", config['font_size'] - 4)
            except:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Textos
            equipamento = checklist.equipamento.nome[:25] + "..." if len(checklist.equipamento.nome) > 25 else checklist.equipamento.nome
            data_texto = checklist.data_checklist.strftime('%d/%m/%Y')
            
            # Posições
            y_start = qr_img.height + 10
            center_x = qr_img.width // 2
            
            # Desenhar textos centralizados
            draw.text((center_x, y_start), equipamento, fill='black', font=font, anchor='mt')
            draw.text((center_x, y_start + 25), f"{data_texto} - {checklist.turno}", fill='black', font=font_small, anchor='mt')
            draw.text((center_x, y_start + 45), f"ID: {checklist.uuid}", fill='gray', font=font_small, anchor='mt')
            
            return new_img
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao adicionar texto: {e}")
            return qr_img
    
    def _add_equipment_text(self, qr_img, equipamento, config):
        """Adiciona texto do equipamento ao QR code"""
        try:
            text_height = config['text_height']
            new_height = qr_img.height + text_height
            new_img = Image.new('RGB', (qr_img.width, new_height), 'white')
            
            # Colar QR code
            new_img.paste(qr_img, (0, 0))
            
            # Adicionar texto
            draw = ImageDraw.Draw(new_img)
            
            try:
                font = ImageFont.truetype("arial.ttf", config['font_size'])
                font_small = ImageFont.truetype("arial.ttf", config['font_size'] - 4)
            except:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Textos do equipamento
            nome = equipamento.nome[:20] + "..." if len(equipamento.nome) > 20 else equipamento.nome
            codigo = getattr(equipamento, 'codigo', f"EQ{equipamento.id}")
            
            y_start = qr_img.height + 10
            center_x = qr_img.width // 2
            
            draw.text((center_x, y_start), nome, fill='black', font=font, anchor='mt')
            draw.text((center_x, y_start + 25), f"Código: {codigo}", fill='black', font=font_small, anchor='mt')
            draw.text((center_x, y_start + 45), equipamento.cliente.razao_social[:25], fill='gray', font=font_small, anchor='mt')
            
            return new_img
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao adicionar texto equipamento: {e}")
            return qr_img
    
    def _add_logo_to_qr(self, qr_img, config):
        """Adiciona logo da empresa ao QR code"""
        try:
            logo_path = getattr(settings, 'QR_LOGO_PATH', None)
            if not logo_path or not os.path.exists(logo_path):
                return qr_img
            
            # Carregar logo
            logo = Image.open(logo_path).convert('RGBA')
            
            # Redimensionar logo
            logo_size = config['logo_size']
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            
            # Criar máscara circular para o logo
            mask = Image.new('L', logo_size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse([0, 0, logo_size[0], logo_size[1]], fill=255)
            
            # Criar fundo branco circular
            white_bg = Image.new('RGBA', logo_size, (255, 255, 255, 255))
            
            # Posição central do QR code
            pos_x = (qr_img.width - logo_size[0]) // 2
            pos_y = (qr_img.height - logo_size[1]) // 2
            
            # Colar fundo branco circular
            qr_img.paste(white_bg, (pos_x, pos_y), mask)
            
            # Colar logo
            logo_resized = logo.resize((logo_size[0] - 4, logo_size[1] - 4), Image.Resampling.LANCZOS)
            logo_pos_x = pos_x + 2
            logo_pos_y = pos_y + 2
            
            qr_img.paste(logo_resized, (logo_pos_x, logo_pos_y), logo_resized)
            
            return qr_img
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao adicionar logo: {e}")
            return qr_img
    
    def _generate_filename(self, checklist, tamanho):
        """Gera nome do arquivo baseado no checklist"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        equipamento_id = checklist.equipamento.id
        return f"checklist_{checklist.uuid}_{equipamento_id}_{tamanho}_{timestamp}.png"
    
    def limpar_qr_antigos(self, dias=7):
        """Remove QR codes antigos"""
        import time
        
        removed_count = 0
        cutoff = time.time() - (dias * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.qr_dir):
            for file in files:
                if file.endswith('.png'):
                    filepath = os.path.join(root, file)
                    if os.path.getmtime(filepath) < cutoff:
                        try:
                            os.remove(filepath)
                            removed_count += 1
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao remover {filepath}: {e}")
        
        logger.info(f"🧹 {removed_count} QR codes antigos removidos")
        return removed_count
    
    def gerar_qr_customizado(self, dados, filename, config_custom=None):
        """
        Gera QR code customizado com dados específicos
        
        Args:
            dados: Dados para o QR code (URL, texto, etc.)
            filename: Nome do arquivo
            config_custom: Configurações customizadas
        
        Returns:
            dict: Informações do QR code gerado
        """
        try:
            config = config_custom or self._get_size_config('medium')
            
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=config['box_size'],
                border=4,
            )
            qr.add_data(dados)
            qr.make(fit=True)
            
            # Gerar imagem
            qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            
            # Salvar
            filepath = os.path.join(self.qr_dir, 'temp', filename)
            qr_img.save(filepath, 'PNG', quality=95)
            
            qr_url = f"{settings.MEDIA_URL}qr_codes/temp/{filename}"
            
            return {
                'filename': filename,
                'filepath': filepath,
                'url': qr_url,
                'data': dados,
                'size': f"{qr_img.width}x{qr_img.height}",
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar QR customizado: {e}")
            raise


# ================================================================
# VIEWS PARA SERVIR E GERENCIAR QR CODES
# ================================================================

from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gerar_qr_checklist_view(request, checklist_id):
    """API para gerar QR code de checklist específico"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        checklist = ChecklistNR12.objects.get(id=checklist_id)
        
        # Parâmetros opcionais
        tamanho = request.data.get('tamanho', 'medium')
        incluir_logo = request.data.get('incluir_logo', True)
        
        # Gerar QR code
        qr_manager = QRCodeManager()
        qr_info = qr_manager.gerar_qr_checklist(checklist, tamanho, incluir_logo)
        
        return Response({
            'success': True,
            'qr_code': qr_info
        })
        
    except ChecklistNR12.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Checklist não encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gerar_qr_equipamento_view(request, equipamento_id):
    """API para gerar QR code de equipamento"""
    try:
        from backend.apps.equipamentos.models import Equipamento
        
        equipamento = Equipamento.objects.get(id=equipamento_id)
        tamanho = request.data.get('tamanho', 'medium')
        
        qr_manager = QRCodeManager()
        qr_info = qr_manager.gerar_qr_equipamento(equipamento, tamanho)
        
        return Response({
            'success': True,
            'qr_code': qr_info
        })
        
    except Equipamento.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Equipamento não encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gerar_qr_batch_view(request):
    """API para gerar QR codes em lote"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        # Parâmetros
        checklist_ids = request.data.get('checklist_ids', [])
        tamanho = request.data.get('tamanho', 'medium')
        incluir_logo = request.data.get('incluir_logo', True)
        
        # Buscar checklists
        checklists = ChecklistNR12.objects.filter(id__in=checklist_ids)
        
        if not checklists.exists():
            return Response({
                'success': False,
                'error': 'Nenhum checklist encontrado'
            }, status=404)
        
        # Gerar QR codes
        qr_manager = QRCodeManager()
        resultados = qr_manager.gerar_batch_qr_codes(checklists, tamanho, incluir_logo)
        
        return Response({
            'success': True,
            'total_processados': len(resultados),
            'qr_codes': resultados
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_qr_codes_view(request):
    """Lista QR codes gerados"""
    try:
        qr_manager = QRCodeManager()
        
        # Listar arquivos nos diretórios
        checklists_dir = os.path.join(qr_manager.qr_dir, 'checklists')
        equipamentos_dir = os.path.join(qr_manager.qr_dir, 'equipamentos')
        
        qr_codes = {
            'checklists': [],
            'equipamentos': []
        }
        
        # Listar checklists
        if os.path.exists(checklists_dir):
            for filename in os.listdir(checklists_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(checklists_dir, filename)
                    qr_codes['checklists'].append({
                        'filename': filename,
                        'url': f"{settings.MEDIA_URL}qr_codes/checklists/{filename}",
                        'size': os.path.getsize(filepath),
                        'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                    })
        
        # Listar equipamentos
        if os.path.exists(equipamentos_dir):
            for filename in os.listdir(equipamentos_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(equipamentos_dir, filename)
                    qr_codes['equipamentos'].append({
                        'filename': filename,
                        'url': f"{settings.MEDIA_URL}qr_codes/equipamentos/{filename}",
                        'size': os.path.getsize(filepath),
                        'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                    })
        
        return Response({
            'success': True,
            'qr_codes': qr_codes
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def limpar_qr_antigos_view(request):
    """Remove QR codes antigos"""
    try:
        dias = int(request.query_params.get('dias', 7))
        
        qr_manager = QRCodeManager()
        removed_count = qr_manager.limpar_qr_antigos(dias)
        
        return Response({
            'success': True,
            'message': f'{removed_count} QR codes removidos',
            'removed_count': removed_count
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ================================================================
# TASK CELERY PARA GERAÇÃO AUTOMÁTICA
# ================================================================

from celery import shared_task

@shared_task
def gerar_qr_codes_diarios():
    """Task para gerar QR codes dos checklists diários"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import date
        
        hoje = date.today()
        checklists_hoje = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        )
        
        if not checklists_hoje.exists():
            return "Nenhum checklist pendente para hoje"
        
        qr_manager = QRCodeManager()
        resultados = qr_manager.gerar_batch_qr_codes(
            list(checklists_hoje), 
            tamanho='medium', 
            incluir_logo=True
        )
        
        sucesso = len([r for r in resultados if 'error' not in r])
        
        logger.info(f"✅ QR codes diários gerados: {sucesso}/{len(resultados)}")
        return f"QR codes gerados: {sucesso}/{len(resultados)}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar QR codes diários: {e}")
        raise

@shared_task
def limpar_qr_codes_antigos():
    """Task para limpeza automática de QR codes antigos"""
    try:
        qr_manager = QRCodeManager()
        removed_count = qr_manager.limpar_qr_antigos(dias=7)
        
        return f"QR codes antigos removidos: {removed_count}"
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza de QR codes: {e}")
        raise