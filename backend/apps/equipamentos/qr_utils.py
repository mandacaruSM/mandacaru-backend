# ===============================================
# ARQUIVO: backend/apps/equipamentos/qr_utils.py
# Utilitários para QR Codes - NOVO ARQUIVO
# ===============================================

import qrcode
import json
import uuid
from io import BytesIO
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QRCodeGenerator:
    """Gerador de QR Codes para equipamentos e checklists"""
    
    @staticmethod
    def gerar_qr_equipamento(equipamento) -> Dict[str, Any]:
        """
        Gera QR Code para equipamento
        CORRIGIDO: Inclui validações e dados completos
        """
        try:
            # Dados do QR Code
            qr_data = {
                'tipo': 'equipamento',
                'id': equipamento.id,
                'uuid': str(equipamento.uuid) if hasattr(equipamento, 'uuid') else str(uuid.uuid4()),
                'codigo': getattr(equipamento, 'codigo', f'EQ{equipamento.id:04d}'),
                'nome': equipamento.nome,
                'cliente_id': equipamento.cliente.id if equipamento.cliente else None,
                'cliente_nome': equipamento.cliente.nome if equipamento.cliente else None,
                'ativo_nr12': getattr(equipamento, 'ativo_nr12', True),
                'timestamp': timezone.now().isoformat(),
                'url_bot': f"/bot/equipamento/{equipamento.id}/",
                'url_web': f"/equipamentos/{equipamento.id}/",
                'versao': '2.0'
            }
            
            # Gerar QR Code
            qr_text = json.dumps(qr_data, ensure_ascii=False)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Gerar imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Salvar em BytesIO para retornar
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Salvar dados no equipamento
            equipamento.qr_code_data = qr_data
            equipamento.save(update_fields=['qr_code_data'])
            
            logger.info(f"✅ QR Code gerado para equipamento {equipamento.id}")
            
            return {
                'success': True,
                'qr_data': qr_data,
                'qr_text': qr_text,
                'image_buffer': img_buffer,
                'url_acesso': qr_data['url_bot']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar QR Code para equipamento {equipamento.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def gerar_qr_checklist(checklist) -> Dict[str, Any]:
        """
        Gera QR Code para checklist específico
        """
        try:
            qr_data = {
                'tipo': 'checklist',
                'checklist_id': checklist.id,
                'checklist_uuid': str(checklist.uuid) if hasattr(checklist, 'uuid') else None,
                'equipamento_id': checklist.equipamento.id,
                'equipamento_nome': checklist.equipamento.nome,
                'data_checklist': checklist.data_checklist.isoformat(),
                'status': checklist.status,
                'turno': getattr(checklist, 'turno', 'MANHA'),
                'timestamp': timezone.now().isoformat(),
                'url_bot': f"/bot/checklist/{checklist.id}/",
                'url_web': f"/nr12/checklist/{checklist.id}/",
                'versao': '2.0'
            }
            
            # Gerar QR Code
            qr_text = json.dumps(qr_data, ensure_ascii=False)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            logger.info(f"✅ QR Code gerado para checklist {checklist.id}")
            
            return {
                'success': True,
                'qr_data': qr_data,
                'qr_text': qr_text,
                'image_buffer': img_buffer,
                'url_acesso': qr_data['url_bot']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar QR Code para checklist {checklist.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validar_qr_data(qr_text: str) -> Dict[str, Any]:
        """
        Valida dados de QR Code escaneado
        """
        try:
            # Tentar fazer parse do JSON
            qr_data = json.loads(qr_text)
            
            # Validações básicas
            if not isinstance(qr_data, dict):
                return {'valid': False, 'error': 'Formato inválido'}
            
            if 'tipo' not in qr_data:
                return {'valid': False, 'error': 'Tipo não especificado'}
            
            tipo = qr_data.get('tipo')
            
            if tipo == 'equipamento':
                return QRCodeGenerator._validar_qr_equipamento(qr_data)
            elif tipo == 'checklist':
                return QRCodeGenerator._validar_qr_checklist(qr_data)
            else:
                return {'valid': False, 'error': f'Tipo não suportado: {tipo}'}
                
        except json.JSONDecodeError:
            return {'valid': False, 'error': 'JSON inválido'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    @staticmethod
    def _validar_qr_equipamento(qr_data: Dict) -> Dict[str, Any]:
        """Valida QR Code de equipamento"""
        required_fields = ['id', 'codigo', 'nome']
        
        for field in required_fields:
            if field not in qr_data:
                return {'valid': False, 'error': f'Campo obrigatório ausente: {field}'}
        
        # Verificar se equipamento existe
        try:
            from backend.apps.equipamentos.models import Equipamento
            equipamento = Equipamento.objects.get(id=qr_data['id'])
            
            # Verificar se está ativo para NR12
            if not getattr(equipamento, 'ativo_nr12', True):
                return {
                    'valid': False, 
                    'error': 'Equipamento não está ativo para NR12'
                }
            
            return {
                'valid': True,
                'tipo': 'equipamento',
                'equipamento': equipamento,
                'qr_data': qr_data
            }
            
        except Equipamento.DoesNotExist:
            return {'valid': False, 'error': 'Equipamento não encontrado'}
    
    @staticmethod
    def _validar_qr_checklist(qr_data: Dict) -> Dict[str, Any]:
        """Valida QR Code de checklist"""
        required_fields = ['checklist_id', 'equipamento_id']
        
        for field in required_fields:
            if field not in qr_data:
                return {'valid': False, 'error': f'Campo obrigatório ausente: {field}'}
        
        # Verificar se checklist existe
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            checklist = ChecklistNR12.objects.get(id=qr_data['checklist_id'])
            
            return {
                'valid': True,
                'tipo': 'checklist',
                'checklist': checklist,
                'equipamento': checklist.equipamento,
                'qr_data': qr_data
            }
            
        except ChecklistNR12.DoesNotExist:
            return {'valid': False, 'error': 'Checklist não encontrado'}

# ===============================================
# VIEWS PARA QR CODES
# ===============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse

@api_view(['GET'])
@permission_classes([AllowAny])
def gerar_qr_equipamento_view(request, equipamento_id):
    """
    Endpoint para gerar QR Code de equipamento
    """
    try:
        from backend.apps.equipamentos.models import Equipamento
        equipamento = Equipamento.objects.get(id=equipamento_id, ativo_nr12=True)
        
        # Verificar se operador pode acessar este equipamento
        operador_codigo = request.GET.get('operador_codigo')
        if operador_codigo:
            if not equipamento.pode_ser_acessado_por_operador(operador_codigo):
                return Response({
                    'success': False,
                    'error': 'Operador não autorizado para este equipamento'
                }, status=403)
        
        # Gerar QR Code
        qr_result = QRCodeGenerator.gerar_qr_equipamento(equipamento)
        
        if qr_result['success']:
            # Retornar imagem ou dados conforme parâmetro
            formato = request.GET.get('formato', 'json')
            
            if formato == 'image':
                response = HttpResponse(
                    qr_result['image_buffer'].getvalue(),
                    content_type='image/png'
                )
                response['Content-Disposition'] = f'filename="qr_equipamento_{equipamento.id}.png"'
                return response
            else:
                return Response({
                    'success': True,
                    'equipamento': {
                        'id': equipamento.id,
                        'nome': equipamento.nome,
                        'codigo': qr_result['qr_data']['codigo']
                    },
                    'qr_data': qr_result['qr_data'],
                    'url_acesso': qr_result['url_acesso']
                })
        else:
            return Response({
                'success': False,
                'error': qr_result['error']
            }, status=500)
            
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
@permission_classes([AllowAny])
def processar_qr_scan_view(request):
    """
    Processa QR Code escaneado pelo bot
    """
    try:
        qr_text = request.data.get('qr_text', '')
        operador_codigo = request.data.get('operador_codigo', '')
        
        if not qr_text:
            return Response({
                'success': False,
                'error': 'QR Code não fornecido'
            }, status=400)
        
        # Validar QR Code
        qr_validation = QRCodeGenerator.validar_qr_data(qr_text)
        
        if not qr_validation['valid']:
            return Response({
                'success': False,
                'error': qr_validation['error']
            }, status=400)
        
        # Verificar autorização do operador
        if operador_codigo:
            from backend.apps.operadores.models import Operador
            try:
                operador = Operador.objects.get(
                    codigo=operador_codigo,
                    ativo_bot=True,
                    status='ATIVO'
                )
                
                if qr_validation['tipo'] == 'equipamento':
                    equipamento = qr_validation['equipamento']
                    if not operador.pode_operar_equipamento(equipamento):
                        return Response({
                            'success': False,
                            'error': 'Operador não autorizado para este equipamento'
                        }, status=403)
                
                elif qr_validation['tipo'] == 'checklist':
                    checklist = qr_validation['checklist']
                    if not operador.pode_operar_equipamento(checklist.equipamento):
                        return Response({
                            'success': False,
                            'error': 'Operador não autorizado para este checklist'
                        }, status=403)
                
            except Operador.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Operador não encontrado'
                }, status=403)
        
        # Preparar resposta baseada no tipo
        if qr_validation['tipo'] == 'equipamento':
            equipamento = qr_validation['equipamento']
            
            # Verificar se há checklist pendente hoje
            from backend.apps.nr12_checklist.models import ChecklistNR12
            from datetime import date
            
            checklist_hoje = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=date.today(),
                status__in=['PENDENTE', 'EM_ANDAMENTO']
            ).first()
            
            return Response({
                'success': True,
                'tipo': 'equipamento',
                'equipamento': {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', f'EQ{equipamento.id:04d}'),
                    'cliente': equipamento.cliente.nome if equipamento.cliente else None,
                    'status': getattr(equipamento, 'status_operacional', 'OPERACIONAL')
                },
                'checklist_hoje': {
                    'id': checklist_hoje.id,
                    'status': checklist_hoje.status,
                    'turno': getattr(checklist_hoje, 'turno', 'MANHA')
                } if checklist_hoje else None,
                'acoes_disponiveis': [
                    'criar_checklist' if not checklist_hoje else 'continuar_checklist',
                    'ver_historico',
                    'relatorio_equipamento'
                ],
                'url_acesso': qr_validation['qr_data'].get('url_bot', f'/bot/equipamento/{equipamento.id}/')
            })
        
        elif qr_validation['tipo'] == 'checklist':
            checklist = qr_validation['checklist']
            
            return Response({
                'success': True,
                'tipo': 'checklist',
                'checklist': {
                    'id': checklist.id,
                    'status': checklist.status,
                    'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                    'turno': getattr(checklist, 'turno', 'MANHA')
                },
                'equipamento': {
                    'id': checklist.equipamento.id,
                    'nome': checklist.equipamento.nome,
                    'codigo': getattr(checklist.equipamento, 'codigo', f'EQ{checklist.equipamento.id:04d}')
                },
                'acoes_disponiveis': [
                    'iniciar_checklist' if checklist.status == 'PENDENTE' else 'continuar_checklist',
                    'ver_progresso',
                    'finalizar_checklist' if checklist.status == 'EM_ANDAMENTO' else None
                ],
                'url_acesso': qr_validation['qr_data'].get('url_bot', f'/bot/checklist/{checklist.id}/')
            })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


# ===============================================
# ARQUIVO: backend/apps/equipamentos/urls_qr.py
# URLs para QR Codes - NOVO ARQUIVO
# ===============================================

from django.urls import path
from .qr_utils import gerar_qr_equipamento_view, processar_qr_scan_view

urlpatterns = [
    # Gerar QR Code de equipamento
    path('equipamento/<int:equipamento_id>/qr/', 
         gerar_qr_equipamento_view, 
         name='gerar-qr-equipamento'),
    
    # Processar QR Code escaneado
    path('qr/scan/', 
         processar_qr_scan_view, 
         name='processar-qr-scan'),
]

# ===============================================
# HANDLERS PARA BOT - CORREÇÃO
# ===============================================

# Adicionar ao arquivo: mandacaru_bot/bot_qr/handlers.py

async def processar_qr_escaneado(message: types.Message, operador=None):
    """
    Processa QR Code escaneado pelo usuário
    CORRIGIDO: Usa novo sistema de validação
    """
    try:
        qr_text = message.text.strip()
        chat_id = str(message.chat.id)
        
        # Enviar para API para processar
        from core.db import fazer_requisicao_api
        
        result = await fazer_requisicao_api(
            'POST',
            'equipamentos/qr/scan/',
            data={
                'qr_text': qr_text,
                'operador_codigo': operador['codigo']
            }
        )
        
        if result and result.get('success'):
            await processar_resultado_qr(message, result)
        else:
            erro = result.get('error', 'QR Code inválido') if result else 'Erro de comunicação'
            await message.answer(f"❌ **QR Code Inválido**\n\n{erro}")
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar QR: {e}")
        await message.answer("❌ Erro ao processar QR Code. Tente novamente.")


async def processar_resultado_qr(message: types.Message, result: Dict[str, Any]):
    """
    Processa resultado do QR Code e mostra opções
    """
    try:
        tipo = result.get('tipo')
        
        if tipo == 'equipamento':
            await mostrar_opcoes_equipamento(message, result)
        elif tipo == 'checklist':
            await mostrar_opcoes_checklist(message, result)
        else:
            await message.answer("❌ Tipo de QR Code não suportado")
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar resultado QR: {e}")
        await message.answer("❌ Erro ao processar resultado")


async def mostrar_opcoes_equipamento(message: types.Message, result: Dict[str, Any]):
    """
    Mostra opções disponíveis para equipamento escaneado
    """
    equipamento = result.get('equipamento', {})
    checklist_hoje = result.get('checklist_hoje')
    acoes = result.get('acoes_disponiveis', [])
    
    texto = f"🔧 **Equipamento Encontrado**\n\n"
    texto += f"**Nome:** {equipamento.get('nome', 'N/A')}\n"
    texto += f"**Código:** {equipamento.get('codigo', 'N/A')}\n"
    
    if equipamento.get('cliente'):
        texto += f"**Cliente:** {equipamento['cliente']}\n"
    
    if checklist_hoje:
        status_emoji = "📋" if checklist_hoje['status'] == 'PENDENTE' else "🔄" if checklist_hoje['status'] == 'EM_ANDAMENTO' else "✅"
        texto += f"\n{status_emoji} **Checklist Hoje:** {checklist_hoje['status']}\n"
        texto += f"**Turno:** {checklist_hoje['turno']}\n"
    else:
        texto += f"\n📋 **Nenhum checklist criado hoje**\n"
    
    # Criar keyboard baseado nas ações disponíveis
    keyboard = []
    
    if 'criar_checklist' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="📋 Criar Checklist",
            callback_data=f"qr_create_checklist_{equipamento['id']}"
        )])
    
    if 'continuar_checklist' in acoes and checklist_hoje:
        keyboard.append([InlineKeyboardButton(
            text="▶️ Continuar Checklist",
            callback_data=f"start_checklist_{checklist_hoje['id']}"
        )])
    
    if 'ver_historico' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="📊 Ver Histórico",
            callback_data=f"qr_list_checklists_{equipamento['id']}"
        )])
    
    if 'relatorio_equipamento' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="📈 Relatório",
            callback_data=f"qr_report_{equipamento['id']}"
        )])
    
    # Botões de navegação
    keyboard.append([
        InlineKeyboardButton(text="🔄 Escanear Outro", callback_data="scan_new_qr"),
        InlineKeyboardButton(text="🏠 Menu", callback_data="menu_refresh")
    ])
    
    await message.answer(
        texto,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


async def mostrar_opcoes_checklist(message: types.Message, result: Dict[str, Any]):
    """
    Mostra opções disponíveis para checklist escaneado
    """
    checklist = result.get('checklist', {})
    equipamento = result.get('equipamento', {})
    acoes = result.get('acoes_disponiveis', [])
    
    texto = f"📋 **Checklist Encontrado**\n\n"
    texto += f"**Equipamento:** {equipamento.get('nome', 'N/A')}\n"
    texto += f"**Código:** {equipamento.get('codigo', 'N/A')}\n"
    texto += f"**Data:** {checklist.get('data_checklist', 'N/A')}\n"
    texto += f"**Turno:** {checklist.get('turno', 'N/A')}\n"
    
    status = checklist.get('status', 'N/A')
    status_emoji = "📋" if status == 'PENDENTE' else "🔄" if status == 'EM_ANDAMENTO' else "✅"
    texto += f"**Status:** {status_emoji} {status}\n"
    
    # Criar keyboard baseado nas ações disponíveis
    keyboard = []
    
    if 'iniciar_checklist' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="▶️ Iniciar Checklist",
            callback_data=f"start_checklist_{checklist['id']}"
        )])
    
    if 'continuar_checklist' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="🔄 Continuar",
            callback_data=f"checklist_select_{checklist['id']}"
        )])
    
    if 'ver_progresso' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="📊 Ver Progresso",
            callback_data=f"checklist_progress_{checklist['id']}"
        )])
    
    if 'finalizar_checklist' in acoes:
        keyboard.append([InlineKeyboardButton(
            text="🏁 Finalizar",
            callback_data=f"checklist_finish_{checklist['id']}"
        )])
    
    # Botões de navegação
    keyboard.append([
        InlineKeyboardButton(text="🔄 Escanear Outro", callback_data="scan_new_qr"),
        InlineKeyboardButton(text="🏠 Menu", callback_data="menu_refresh")
    ])
    
    await message.answer(
        texto,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )