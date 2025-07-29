from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import Equipamento

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def equipamento_action_bot(request, equipamento_id):
    """Actions do equipamento para o bot"""
    try:
        equipamento = Equipamento.objects.get(id=equipamento_id)
        
        if request.method == 'GET':
            # Retornar dados do equipamento
            return JsonResponse({
                'success': True,
                'equipamento': {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', f'EQ{equipamento.id:04d}'),
                    'categoria': equipamento.categoria.nome if equipamento.categoria else '',
                    'localizacao': getattr(equipamento, 'localizacao_atual', ''),
                    'status': 'ativo' if getattr(equipamento, 'ativo_nr12', True) else 'inativo'
                }
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            acao = data.get('acao')
            
            if acao == 'iniciar_checklist':
                return processar_iniciar_checklist(equipamento, data)
            elif acao == 'continuar_checklist':
                return processar_continuar_checklist(equipamento, data)
            elif acao == 'status':
                return obter_status_equipamento(equipamento)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Ação "{acao}" não reconhecida'
                })
        
    except Equipamento.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Equipamento não encontrado'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        })
    except Exception as e:
        logger.error(f"Erro na ação do equipamento: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

def processar_iniciar_checklist(equipamento, data):
    """Processa início de checklist"""
    try:
        operador_id = data.get('operador_id')
        if not operador_id:
            return JsonResponse({
                'success': False,
                'error': 'ID do operador é obrigatório'
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Checklist iniciado com sucesso',
            'checklist': {
                'equipamento': equipamento.nome,
                'status': 'em_andamento'
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao iniciar checklist: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao iniciar checklist: {str(e)}'
        })

def processar_continuar_checklist(equipamento, data):
    """Processa continuação de checklist"""
    return JsonResponse({
        'success': True,
        'message': 'Checklist continuado'
    })

def obter_status_equipamento(equipamento):
    """Obtém status detalhado do equipamento"""
    try:
        status_info = {
            'equipamento': {
                'id': equipamento.id,
                'nome': equipamento.nome,
                'codigo': getattr(equipamento, 'codigo', f'EQ{equipamento.id:04d}'),
                'categoria': equipamento.categoria.nome if equipamento.categoria else '',
                'localizacao': getattr(equipamento, 'localizacao_atual', ''),
                'ativo': getattr(equipamento, 'ativo_nr12', True)
            }
        }
        
        return JsonResponse({
            'success': True,
            'status': status_info
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter status: {str(e)}'
        })
