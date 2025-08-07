# ===============================================
# backend/apps/nr12_checklist/views_bot.py
# Views específicas para integração com Bot Telegram
# ===============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import date, timedelta

from .models import ChecklistNR12, ItemChecklistRealizado
from backend.apps.equipamentos.models import Equipamento
from backend.apps.operadores.models import Operador


@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_bot(request):
    """
    Lista checklists para o Bot Telegram
    Parâmetros: operador_id, equipamento_id, status, data_checklist
    """
    try:
        # Obter parâmetros de filtro
        operador_id = request.GET.get('operador_id')
        equipamento_id = request.GET.get('equipamento_id')
        status = request.GET.get('status', 'PENDENTE')
        data_checklist = request.GET.get('data_checklist')
        
        # Construir queryset base
        queryset = ChecklistNR12.objects.all()
        
        # Filtrar por operador (equipamentos que ele pode acessar)
        if operador_id:
            try:
                operador = Operador.objects.get(id=operador_id, ativo_bot=True, status='ATIVO')
                equipamentos_disponiveis = operador.get_equipamentos_disponiveis()
                queryset = queryset.filter(equipamento__in=equipamentos_disponiveis)
            except Operador.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Operador não encontrado ou não autorizado'
                }, status=403)
        
        # Outros filtros
        if equipamento_id:
            queryset = queryset.filter(equipamento_id=equipamento_id)
        if status:
            queryset = queryset.filter(status=status)
        if data_checklist:
            try:
                data = date.fromisoformat(data_checklist)
                queryset = queryset.filter(data_checklist=data)
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Formato de data inválido. Use YYYY-MM-DD'
                }, status=400)
        
        # Ordenar e limitar resultados
        checklists = queryset.select_related(
            'equipamento', 'responsavel'
        ).order_by('-data_checklist', 'equipamento__nome')[:50]
        
        # Serializar dados
        checklists_data = []
        for checklist in checklists:
            checklists_data.append({
                'id': checklist.id,
                'equipamento': {
                    'id': checklist.equipamento.id,
                    'nome': checklist.equipamento.nome,
                    'codigo': getattr(checklist.equipamento, 'codigo', f"EQ{checklist.equipamento.id:04d}"),
                },
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'turno': getattr(checklist, 'turno', 'MANHA'),
                'status': checklist.status,
                'responsavel': checklist.responsavel.get_full_name() if checklist.responsavel else None,
                'data_criacao': getattr(checklist, 'created_at', checklist.data_checklist).strftime('%Y-%m-%d %H:%M:%S'),
                'uuid': str(getattr(checklist, 'uuid', '')),
            })
        
        return Response({
            'success': True,
            'count': len(checklists_data),
            'results': checklists_data,
            'filters_applied': {
                'operador_id': operador_id,
                'equipamento_id': equipamento_id,
                'status': status,
                'data_checklist': data_checklist,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_operador(request, operador_id):
    """
    Lista equipamentos que um operador específico pode acessar
    """
    try:
        operador = get_object_or_404(
            Operador, 
            id=operador_id, 
            ativo_bot=True, 
            status='ATIVO'
        )
        
        # Obter equipamentos que o operador pode acessar
        equipamentos = operador.get_equipamentos_disponiveis()[:50]
        
        # Serializar dados
        equipamentos_data = []
        for equipamento in equipamentos:
            # Verificar se há checklist pendente para hoje
            checklist_hoje = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=date.today(),
                status__in=['PENDENTE', 'EM_ANDAMENTO']
            ).first()
            
            equipamentos_data.append({
                'id': equipamento.id,
                'nome': equipamento.nome,
                'codigo': getattr(equipamento, 'codigo', f"EQ{equipamento.id:04d}"),
                'marca': getattr(equipamento, 'marca', ''),
                'modelo': getattr(equipamento, 'modelo', ''),
                'horimetro_atual': getattr(equipamento, 'horimetro_atual', 0),
                'status_operacional': getattr(equipamento, 'status_operacional', 'DISPONIVEL'),
                'checklist_hoje': {
                    'id': checklist_hoje.id,
                    'status': checklist_hoje.status,
                    'turno': getattr(checklist_hoje, 'turno', 'MANHA'),
                } if checklist_hoje else None,
                'ativo_nr12': getattr(equipamento, 'ativo_nr12', True),
            })
        
        return Response({
            'success': True,
            'operador': {
                'id': operador.id,
                'nome': operador.nome,
                'codigo': operador.codigo,
            },
            'count': len(equipamentos_data),
            'equipamentos': equipamentos_data
        })
        
    except Operador.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Operador não encontrado ou não autorizado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)