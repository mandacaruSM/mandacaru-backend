# backend/apps/operadores/quick_api_views.py
# SOLUÇÃO RÁPIDA - Criar uma view API simples que funciona

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Operador
import json

@method_decorator(csrf_exempt, name='dispatch')
class OperadorQuickAPIView(View):
    """
    View API simples para operadores - funciona imediatamente
    GET /api/operadores/?search=nome
    """
    
    def get(self, request):
        try:
            # Parâmetro de busca
            search = request.GET.get('search', '').strip()
            
            # Buscar operadores
            queryset = Operador.objects.filter(status='ATIVO')
            
            if search:
                queryset = queryset.filter(
                    Q(nome__icontains=search) |
                    Q(codigo__icontains=search) |
                    Q(funcao__icontains=search) |
                    Q(setor__icontains=search)
                )
            
            # Converter para lista
            operadores = []
            for op in queryset[:50]:  # Limitar para 50 resultados
                operadores.append({
                    'id': op.id,
                    'codigo': op.codigo,
                    'nome': op.nome,
                    'funcao': op.funcao,
                    'setor': op.setor,
                    'telefone': op.telefone,
                    'data_nascimento': op.data_nascimento.strftime('%Y-%m-%d') if op.data_nascimento else None,
                    'status': op.status,
                    'ativo_bot': op.ativo_bot,
                    'chat_id_telegram': op.chat_id_telegram,
                })
            
            # Resposta no formato DRF
            response_data = {
                'count': len(operadores),
                'results': operadores
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Erro interno: {str(e)}'
            }, status=500)
    
    def patch(self, request):
        """Atualizar operador (para chat_id)"""
        try:
            # Pegar ID da URL
            path_parts = request.path.strip('/').split('/')
            if len(path_parts) >= 3:
                operador_id = int(path_parts[-2])  # /api/operadores/123/
            else:
                return JsonResponse({'error': 'ID não fornecido'}, status=400)
            
            # Buscar operador
            operador = Operador.objects.get(id=operador_id)
            
            # Dados do JSON
            data = json.loads(request.body.decode('utf-8'))
            
            # Atualizar campos permitidos
            if 'chat_id_telegram' in data:
                operador.chat_id_telegram = data['chat_id_telegram']
                operador.save()
            
            return JsonResponse({
                'id': operador.id,
                'nome': operador.nome,
                'codigo': operador.codigo,
                'chat_id_telegram': operador.chat_id_telegram,
                'success': True
            })
            
        except Operador.DoesNotExist:
            return JsonResponse({'error': 'Operador não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# backend/apps/operadores/quick_urls.py
# URLs simples que funcionam imediatamente

from django.urls import path, re_path
from .quick_api_views import OperadorQuickAPIView

urlpatterns = [
    # Lista e busca
    path('', OperadorQuickAPIView.as_view(), name='operador-list'),
    # Atualização individual
    re_path(r'^(?P<pk>\d+)/$', OperadorQuickAPIView.as_view(), name='operador-detail'),
]