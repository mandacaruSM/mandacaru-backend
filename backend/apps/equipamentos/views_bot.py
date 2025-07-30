from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Equipamento


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_publicos(request):
    """Lista equipamentos (público para bot)"""
    try:
        operador_id = request.GET.get('operador_id')
        equipamentos = Equipamento.objects.filter(ativo=True)[:20]
        
        equipamentos_data = []
        for eq in equipamentos:
            equipamentos_data.append({
                'id': eq.id,
                'nome': eq.nome,
                'marca': getattr(eq, 'marca', ''),
                'modelo': getattr(eq, 'modelo', ''),
                'ativo': getattr(eq, 'ativo', True),
                'horimetro_atual': getattr(eq, 'horimetro_atual', 0),
                'status_operacional': getattr(eq, 'status_operacional', 'Operacional'),
            })
        
        return Response({
            'success': True,
            'count': len(equipamentos_data),
            'results': equipamentos_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_equipamento(request, equipamento_id):
    """Checklists de um equipamento específico"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import date, timedelta
        
        equipamento = Equipamento.objects.get(id=equipamento_id)
        
        data_limite = date.today() - timedelta(days=30)
        checklists = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            data_checklist__gte=data_limite
        ).order_by('-data_checklist')[:10]
        
        checklists_data = []
        for checklist in checklists:
            checklists_data.append({
                'id': checklist.id,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'status': checklist.status,
                'turno': getattr(checklist, 'turno', 'MANHA'),
            })
        
        return Response({
            'success': True,
            'equipamento': {
                'id': equipamento.id,
                'nome': equipamento.nome,
            },
            'count': len(checklists_data),
            'checklists': checklists_data
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
