from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render

from backend.apps.nr12_checklist.models import ChecklistNR12


@api_view(['GET'])
@permission_classes([AllowAny])
def checklist_por_uuid(request, checklist_uuid):
    try:
        checklist = ChecklistNR12.objects.get(uuid=checklist_uuid)
        data = {
            'id': checklist.id,
            'uuid': str(checklist.uuid),
            'equipamento': {
                'id': checklist.equipamento.id,
                'nome': checklist.equipamento.nome,
                'marca': checklist.equipamento.marca,
                'modelo': checklist.equipamento.modelo,
                'cliente': checklist.equipamento.cliente.razao_social
            },
            'data_checklist': checklist.data_checklist,
            'turno': checklist.turno,
            'status': checklist.status,
            'responsavel': checklist.responsavel.username if checklist.responsavel else None,
            'pode_editar': checklist.status in ['PENDENTE', 'EM_ANDAMENTO'],
            'link_bot': f"https://t.me/seu_bot?start=checklist_{checklist.uuid}",
            'percentual_conclusao': checklist.percentual_conclusao
        }
        return Response(data)
    except ChecklistNR12.DoesNotExist:
        return Response({'error': 'Checklist não encontrado'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def visualizar_checklist_html(request, pk):
    checklist = get_object_or_404(ChecklistNR12.objects.select_related(
        'equipamento', 'responsavel'
    ).prefetch_related('itens__item_padrao'), pk=pk)

    return render(request, 'nr12_checklist/checklist_imprimir.html', {
        'checklist': checklist,
        'itens': checklist.itens.all(),
        'empresa': checklist.equipamento.cliente.razao_social if checklist.equipamento.cliente else '',
    })
