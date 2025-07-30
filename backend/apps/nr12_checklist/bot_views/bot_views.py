# ===============================================
# CORREÇÃO 1: backend/apps/nr12_checklist/bot_views/bot_checklists.py
# ===============================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from datetime import date, timedelta

from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado
from backend.apps.equipamentos.models import Equipamento
from backend.apps.operadores.models import Operador


@api_view(['GET'])
@permission_classes([AllowAny])  # Público para o bot
def checklists_bot_list(request):
    """
    Lista checklists para o bot Telegram
    GET /api/nr12/bot/checklists/
    
    Parâmetros:
    - operador_id: ID do operador
    - equipamento_id: ID do equipamento
    - status: Status do checklist
    - dias: Últimos X dias (padrão: 30)
    """
    try:
        # Parâmetros de filtro
        operador_id = request.GET.get('operador_id')
        equipamento_id = request.GET.get('equipamento_id')
        status = request.GET.get('status')
        dias = int(request.GET.get('dias', 30))
        
        # Query base
        queryset = ChecklistNR12.objects.select_related(
            'equipamento', 'responsavel'
        ).prefetch_related('itens')
        
        # Filtrar por data (últimos X dias)
        data_limite = date.today() - timedelta(days=dias)
        queryset = queryset.filter(data_checklist__gte=data_limite)
        
        # Filtros específicos
        if operador_id:
            # Filtrar por checklists onde o operador é responsável
            # OU equipamentos que o operador pode usar
            try:
                operador = Operador.objects.get(id=operador_id)
                
                # Buscar equipamentos que o operador pode usar
                # (adapte conforme sua regra de negócio)
                equipamentos_operador = Equipamento.objects.filter(
                    Q(responsavel=operador) |  # Se operador é responsável
                    Q(operadores_autorizados=operador)  # Se tem relação M2M
                )
                
                queryset = queryset.filter(
                    Q(responsavel__operador=operador) |  # Se responsável é o operador
                    Q(equipamento__in=equipamentos_operador)  # Ou equipamento autorizado
                )
                
            except Operador.DoesNotExist:
                return Response({'error': 'Operador não encontrado'}, status=404)
        
        if equipamento_id:
            queryset = queryset.filter(equipamento_id=equipamento_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        # Ordenar por data mais recente
        queryset = queryset.order_by('-data_checklist', '-created_at')
        
        # Limitar resultados
        limite = int(request.GET.get('limite', 20))
        queryset = queryset[:limite]
        
        # Serializar dados
        checklists_data = []
        for checklist in queryset:
            # Calcular progresso
            total_itens = checklist.itens.count()
            itens_concluidos = checklist.itens.filter(
                status__in=['CONFORME', 'NAO_CONFORME']
            ).count()
            
            percentual = 0
            if total_itens > 0:
                percentual = round((itens_concluidos / total_itens) * 100, 1)
            
            checklist_data = {
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'equipamento_id': checklist.equipamento.id,
                'equipamento_nome': checklist.equipamento.nome,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'turno': checklist.turno,
                'status': checklist.status,
                'responsavel': checklist.responsavel.username if checklist.responsavel else None,
                'total_itens': total_itens,
                'itens_concluidos': itens_concluidos,
                'percentual_conclusao': percentual,
                'pode_editar': checklist.status in ['PENDENTE', 'EM_ANDAMENTO'],
                'created_at': checklist.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            checklists_data.append(checklist_data)
        
        return Response({
            'success': True,
            'count': len(checklists_data),
            'results': checklists_data,
            'filtros_aplicados': {
                'operador_id': operador_id,
                'equipamento_id': equipamento_id,
                'status': status,
                'dias': dias,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_operador_bot(request, operador_id):
    """
    Lista equipamentos que um operador pode usar
    GET /api/operadores/{operador_id}/equipamentos/
    """
    try:
        operador = Operador.objects.get(id=operador_id)
        
        # Buscar equipamentos do operador
        # (adapte conforme sua regra de negócio)
        equipamentos = Equipamento.objects.filter(
            Q(responsavel=operador) |  # Equipamentos onde é responsável
            Q(operadores_autorizados=operador) |  # Equipamentos autorizados (se há M2M)
            Q(ativo=True)  # Equipamentos ativos
        ).distinct()
        
        equipamentos_data = []
        for eq in equipamentos:
            # Contar checklists recentes
            checklists_recentes = ChecklistNR12.objects.filter(
                equipamento=eq,
                data_checklist__gte=date.today() - timedelta(days=7)
            ).count()
            
            equipamento_data = {
                'id': eq.id,
                'nome': eq.nome,
                'marca': getattr(eq, 'marca', ''),
                'modelo': getattr(eq, 'modelo', ''),
                'numero_serie': getattr(eq, 'numero_serie', ''),
                'uuid': str(getattr(eq, 'uuid', '')),
                'ativo': getattr(eq, 'ativo', True),
                'checklists_ultima_semana': checklists_recentes,
                'pode_usar': True,
            }
            equipamentos_data.append(equipamento_data)
        
        return Response({
            'success': True,
            'operador': {
                'id': operador.id,
                'nome': operador.nome,
                'chat_id_telegram': getattr(operador, 'chat_id_telegram', None),
            },
            'count': len(equipamentos_data),
            'equipamentos': equipamentos_data,
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


@api_view(['POST'])
@permission_classes([AllowAny])
def criar_checklist_bot(request):
    """
    Cria um novo checklist via bot
    POST /api/nr12/bot/checklists/criar/
    
    Body JSON:
    {
        "equipamento_id": 1,
        "operador_id": 9,
        "turno": "MANHA"
    }
    """
    try:
        data = request.data
        
        equipamento_id = data.get('equipamento_id')
        operador_id = data.get('operador_id')
        turno = data.get('turno', 'MANHA')
        
        if not equipamento_id or not operador_id:
            return Response({
                'success': False,
                'error': 'equipamento_id e operador_id são obrigatórios'
            }, status=400)
        
        # Verificar se equipamento existe
        try:
            equipamento = Equipamento.objects.get(id=equipamento_id)
        except Equipamento.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Equipamento não encontrado'
            }, status=404)
        
        # Verificar se operador existe
        try:
            operador = Operador.objects.get(id=operador_id)
        except Operador.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Operador não encontrado'
            }, status=404)
        
        # Verificar se já existe checklist hoje para este equipamento
        checklist_existente = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            data_checklist=date.today()
        ).first()
        
        if checklist_existente:
            return Response({
                'success': False,
                'error': 'Já existe um checklist hoje para este equipamento',
                'checklist_existente': {
                    'id': checklist_existente.id,
                    'status': checklist_existente.status,
                    'pode_editar': checklist_existente.status in ['PENDENTE', 'EM_ANDAMENTO']
                }
            }, status=400)
        
        # Criar novo checklist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Tentar associar a um usuário (operador pode ter user relacionado)
        user = None
        if hasattr(operador, 'user'):
            user = operador.user
        else:
            # Usar primeiro admin como fallback
            user = User.objects.filter(is_staff=True).first()
        
        checklist = ChecklistNR12.objects.create(
            equipamento=equipamento,
            responsavel=user,
            data_checklist=date.today(),
            turno=turno,
            status='PENDENTE'
        )
        
        # Criar itens do checklist baseados no tipo do equipamento
        from backend.apps.nr12_checklist.models import ItemChecklistPadrao, ItemChecklistRealizado
        
        # Buscar tipo do equipamento
        tipo_equipamento = getattr(equipamento, 'tipo_nr12', None)
        if tipo_equipamento:
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=tipo_equipamento,
                ativo=True
            ).order_by('ordem')
            
            # Criar itens realizados
            for item_padrao in itens_padrao:
                ItemChecklistRealizado.objects.create(
                    checklist=checklist,
                    item_padrao=item_padrao,
                    status='PENDENTE'
                )
        
        return Response({
            'success': True,
            'checklist': {
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'equipamento_nome': equipamento.nome,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'turno': checklist.turno,
                'status': checklist.status,
                'total_itens': checklist.itens.count(),
                'link_bot': f"https://t.me/Mandacarusmbot?start=checklist_{checklist.uuid}",
            }
        })
        
    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc() if request.GET.get('debug') else None
        }, status=500)
