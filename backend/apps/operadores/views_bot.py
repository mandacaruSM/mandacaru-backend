from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import Operador

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def operador_login_bot(request):
    """Login específico para bot telegram - VERSÃO SIMPLES"""
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({
                'success': False, 
                'error': 'Nome é obrigatório'
            })
        
        # Buscar operadores - versão mais simples
        operadores = Operador.objects.filter(nome__icontains=nome)
        
        if not operadores.exists():
            return JsonResponse({
                'success': False,
                'error': 'Nenhum operador encontrado'
            })
        
        # Converter para dados simples
        resultado = []
        for op in operadores:
            resultado.append({
                'id': op.id,
                'nome': op.nome,
                'cargo': getattr(op, 'cargo', ''),
                'data_nascimento': op.data_nascimento.strftime('%Y-%m-%d') if op.data_nascimento else None
            })
        
        return JsonResponse({
            'success': True,
            'operadores': resultado,
            'count': len(resultado)
        })
        
    except Exception as e:
        logger.error(f"Erro no login do bot: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Erro: {str(e)}'
        })

@csrf_exempt
def validar_operador_bot(request, operador_id):
    """Validar operador"""
    return JsonResponse({
        'success': True, 
        'message': 'Endpoint funcionando',
        'operador_id': operador_id
    })

@csrf_exempt  
def listar_operadores_bot(request):
    """Listar operadores"""
    operadores = Operador.objects.all()[:5]  # Primeiros 5
    resultado = [{'id': op.id, 'nome': op.nome} for op in operadores]
    
    return JsonResponse({
        'success': True, 
        'results': resultado,
        'count': len(resultado)
    })