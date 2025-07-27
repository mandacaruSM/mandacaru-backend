from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Operador
import json

@method_decorator(csrf_exempt, name='dispatch')
class OperadorAPIView(View):
    def get(self, request, pk=None):
        try:
            if pk:
                operador = Operador.objects.get(id=pk)
                data = self._serialize_operador(operador)
                return JsonResponse(data)
            else:
                search = request.GET.get('search', '').strip()
                queryset = Operador.objects.all()
                if search:
                    queryset = queryset.filter(Q(nome__icontains=search))
                operadores = [self._serialize_operador(op) for op in queryset[:50]]
                return JsonResponse({'count': len(operadores), 'results': operadores})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_operador(self, operador):
        return {
            'id': operador.id,
            'codigo': operador.codigo,
            'nome': operador.nome,
            'data_nascimento': operador.data_nascimento.strftime('%Y-%m-%d') if operador.data_nascimento else None,
            'status': getattr(operador, 'status', 'ATIVO'),
            'ativo_bot': getattr(operador, 'ativo_bot', True),
            'chat_id_telegram': operador.chat_id_telegram,
        }


