# backend/apps/nr12_checklist/bot_views/bot_views.py

from datetime import date, timedelta
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from backend.apps.operadores.models import Operador
from backend.apps.nr12_checklist.models import ChecklistNR12

@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_bot_list(request):
    """
    Lista checklists para o bot Telegram
    GET /api/nr12/bot/checklists/
    
    Parâmetros:
    - operador_id: ID do operador
    - status: Status do checklist (opcional)
    - dias: Últimos X dias (padrão: 30)
    - limite: número máximo de resultados (padrão: 20)
    """
    try:
        # valida operador
        operador_id = request.GET.get('operador_id')
        if not operador_id:
            return Response({'success': False, 'error': 'operador_id é obrigatório'}, status=400)

        operador = Operador.objects.filter(
            id=operador_id,
            status='ATIVO',
            ativo_bot=True
        ).first()
        if not operador:
            return Response({'success': False, 'error': 'Operador não autorizado'}, status=403)

        # intervalo de datas
        dias = int(request.GET.get('dias', 30))
        data_limite = date.today() - timedelta(days=dias)

        # usar apenas equipamentos autorizados
        equipamentos = operador.get_equipamentos_disponiveis()

        # base do queryset
        queryset = ChecklistNR12.objects.select_related(
            'equipamento', 'responsavel'
        ).filter(
            equipamento__in=equipamentos,
            data_checklist__gte=data_limite
        )

        # filtro opcional por status
        status_param = request.GET.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # ordenar e limitar
        limite = int(request.GET.get('limite', 20))
        queryset = queryset.order_by('-data_checklist', '-created_at')[:limite]

        # serializar
        results = []
        for chk in queryset:
            total_itens = chk.itens.count()
            itens_concluidos = chk.itens.filter(status__in=['CONFORME', 'NAO_CONFORME']).count()
            percentual = round((itens_concluidos / total_itens) * 100, 1) if total_itens else 0

            results.append({
                'id': chk.id,
                'uuid': str(chk.uuid),
                'equipamento_id': chk.equipamento.id,
                'equipamento_nome': chk.equipamento.nome,
                'data_checklist': chk.data_checklist.strftime('%Y-%m-%d'),
                'turno': chk.turno,
                'status': chk.status,
                'responsavel': chk.responsavel.username if chk.responsavel else None,
                'total_itens': total_itens,
                'itens_concluidos': itens_concluidos,
                'percentual_conclusao': percentual,
                'created_at': chk.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return Response({'success': True, 'count': len(results), 'results': results})

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)