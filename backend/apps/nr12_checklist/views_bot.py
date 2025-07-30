from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from datetime import date, timedelta

from .models import ChecklistNR12
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento


@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_bot(request):
    """Checklists públicos para o bot"""
    try:
        operador_id = request.GET.get('operador_id')
        equipamento_id = request.GET.get('equipamento_id')
        
        queryset = ChecklistNR12.objects.select_related('equipamento')
        
        if operador_id:
            try:
                operador = Operador.objects.get(id=operador_id)
                equipamentos = Equipamento.objects.filter(ativo=True)[:10]
                queryset = queryset.filter(equipamento__in=equipamentos)
            except Operador.DoesNotExist:
                pass
        
        if equipamento_id:
            queryset = queryset.filter(equipamento_id=equipamento_id)
        
        data_limite = date.today() - timedelta(days=30)
        queryset = queryset.filter(data_checklist__gte=data_limite)
        
        checklists = []
        for checklist in queryset[:20]:
            checklists.append({
                'id': checklist.id,
                'equipamento_id': checklist.equipamento.id,
                'equipamento_nome': checklist.equipamento.nome,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'status': checklist.status,
                'turno': getattr(checklist, 'turno', 'MANHA'),
            })
        
        return Response({
            'success': True,
            'count': len(checklists),
            'results': checklists
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_operador(request, operador_id):
    """Equipamentos de um operador"""
    try:
        operador = Operador.objects.get(id=operador_id)
        equipamentos = Equipamento.objects.filter(ativo=True)[:10]
        
        equipamentos_data = []
        for eq in equipamentos:
            equipamentos_data.append({
                'id': eq.id,
                'nome': eq.nome,
                'marca': getattr(eq, 'marca', ''),
                'modelo': getattr(eq, 'modelo', ''),
                'ativo': getattr(eq, 'ativo', True),
            })
        
        return Response({
            'success': True,
            'operador_id': operador_id,
            'count': len(equipamentos_data),
            'equipamentos': equipamentos_data
        })
        
    except Operador.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Operador não encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
