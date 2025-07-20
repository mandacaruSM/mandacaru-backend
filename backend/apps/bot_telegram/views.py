# ================================================================
# ARQUIVO: backend/apps/bot_telegram/views.py
# Views para integração com bot Telegram e acesso via QR Code
# ================================================================

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def checklist_qr_redirect(request, checklist_uuid):
    """
    Endpoint acessado quando QR Code do checklist é escaneado
    GET: Retorna informações básicas do checklist
    POST: Webhook do Telegram para receber atualizações
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        checklist = get_object_or_404(ChecklistNR12, uuid=checklist_uuid)
        
        if request.method == 'GET':
            # Acesso direto via QR Code - redirecionar ou retornar dados
            bot_link = f"https://t.me/MandacaruBot?start=checklist_{checklist_uuid}"
            
            # Se for um bot/user-agent do Telegram, retornar JSON
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            if 'telegram' in user_agent or 'bot' in user_agent:
                return JsonResponse({
                    'success': True,
                    'checklist': {
                        'id': checklist.id,
                        'uuid': str(checklist.uuid),
                        'equipamento': checklist.equipamento.nome,
                        'data': checklist.data_checklist.isoformat(),
                        'turno': checklist.turno,
                        'status': checklist.status,
                        'pode_editar': checklist.status in ['PENDENTE', 'EM_ANDAMENTO']
                    },
                    'bot_link': bot_link,
                    'message': f'Checklist do equipamento {checklist.equipamento.nome} - {checklist.data_checklist}'
                })
            else:
                # Redirecionar para o bot do Telegram
                return HttpResponseRedirect(bot_link)
        
        elif request.method == 'POST':
            # Webhook do Telegram - processar atualizações
            try:
                data = json.loads(request.body)
                # Aqui você pode processar atualizações do bot
                # Por enquanto, apenas retornar sucesso
                return JsonResponse({'success': True, 'message': 'Webhook recebido'})
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        logger.error(f"Erro no checklist QR redirect: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Checklist não encontrado ou erro interno'
        }, status=404)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def equipamento_qr_redirect(request, equipamento_id):
    """
    Endpoint acessado quando QR Code do equipamento é escaneado
    """
    try:
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import date
        
        equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)
        
        if request.method == 'GET':
            # Verificar checklist de hoje
            hoje = date.today()
            checklist_hoje = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=hoje
            ).first()
            
            bot_link = f"https://t.me/MandacaruBot?start=equipamento_{equipamento_id}"
            
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            if 'telegram' in user_agent or 'bot' in user_agent:
                return JsonResponse({
                    'success': True,
                    'equipamento': {
                        'id': equipamento.id,
                        'nome': equipamento.nome,
                        'marca': equipamento.marca,
                        'modelo': equipamento.modelo,
                        'cliente': equipamento.cliente.razao_social,
                        'tipo_nr12': equipamento.tipo_nr12.nome if equipamento.tipo_nr12 else None,
                        'ativo_nr12': equipamento.ativo_nr12
                    },
                    'checklist_hoje': {
                        'existe': checklist_hoje is not None,
                        'uuid': str(checklist_hoje.uuid) if checklist_hoje else None,
                        'status': checklist_hoje.status if checklist_hoje else 'PENDENTE',
                        'turno': checklist_hoje.turno if checklist_hoje else None
                    },
                    'bot_link': bot_link,
                    'acoes_disponiveis': [
                        'consultar_checklist',
                        'iniciar_checklist',
                        'registrar_abastecimento',
                        'reportar_anomalia',
                        'consultar_historico'
                    ]
                })
            else:
                return HttpResponseRedirect(bot_link)
        
        elif request.method == 'POST':
            # Processar ações do bot
            try:
                data = json.loads(request.body)
                acao = data.get('acao')
                
                if acao == 'consultar_status':
                    # Retornar status atual do equipamento
                    return JsonResponse({
                        'success': True,
                        'equipamento': equipamento.nome,
                        'status': 'Operacional',  # Implementar lógica de status
                        'checklist_pendente': checklist_hoje.status == 'PENDENTE' if checklist_hoje else True
                    })
                
                return JsonResponse({'success': True, 'message': 'Ação processada'})
                
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        logger.error(f"Erro no equipamento QR redirect: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Equipamento não encontrado ou erro interno'
        }, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """
    Webhook principal do bot Telegram
    Recebe todas as atualizações do Telegram
    """
    try:
        data = json.loads(request.body)
        
        # Log da mensagem recebida (apenas em desenvolvimento)
        if settings.DEBUG:
            logger.info(f"Webhook Telegram recebido: {data}")
        
        # Verificar se é uma mensagem
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Processar comandos
            if text.startswith('/start'):
                # Extrair parâmetro do start
                parts = text.split(' ')
                if len(parts) > 1:
                    param = parts[1]
                    
                    if param.startswith('checklist_'):
                        # Link para checklist específico
                        checklist_uuid = param.replace('checklist_', '')
                        # Implementar lógica para enviar detalhes do checklist
                        response_text = f"🔍 Checklist identificado: {checklist_uuid}\n\nUse o menu abaixo para interagir:"
                    
                    elif param.startswith('equipamento_'):
                        # Link para equipamento específico
                        equipamento_id = param.replace('equipamento_', '')
                        # Implementar lógica para equipamento
                        response_text = f"🔧 Equipamento ID: {equipamento_id}\n\nEscolha uma opção:"
                    
                    else:
                        response_text = "👋 Bem-vindo ao Mandacaru ERP!\n\nEscaneie um QR Code para começar."
                else:
                    response_text = "👋 Bem-vindo ao Mandacaru ERP!\n\nEscaneie um QR Code para começar."
                
                # Aqui você enviaria a resposta via API do Telegram
                # Por enquanto, apenas loggar
                logger.info(f"Resposta para chat {chat_id}: {response_text}")
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        logger.error("JSON inválido recebido no webhook")
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        logger.error(f"Erro no webhook Telegram: {e}")
        return JsonResponse({'success': False, 'error': 'Erro interno'}, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """
    Health check para verificar se o serviço está funcionando
    """
    try:
        # Verificar conexão com banco
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Verificar se as apps principais estão funcionando
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from backend.apps.equipamentos.models import Equipamento
        
        total_checklists = ChecklistNR12.objects.count()
        total_equipamentos = Equipamento.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': '2025-01-14T15:30:00Z',
            'database': 'connected',
            'services': {
                'checklists': f'{total_checklists} registros',
                'equipamentos': f'{total_equipamentos} registros'
            },
            'version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': '2025-01-14T15:30:00Z'
        }, status=503)