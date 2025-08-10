# ===============================================
# ARQUIVO: backend/apps/nr12_checklist/views_bot.py
# Views específicas para integração com Bot Telegram - CORRIGIDO
# ===============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from datetime import date, timedelta
from .models import ChecklistNR12, ItemChecklistRealizado
from backend.apps.equipamentos.models import Equipamento
from backend.apps.operadores.models import Operador
from backend.apps.nr12_checklist.models import ChecklistNR12

@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_bot(request):
    """
    Lista checklists para o bot:
    Parâmetros:
      - operador_id (obrigatório)
      - equipamento_id (opcional)
      - status in [PENDENTE, EM_ANDAMENTO, CONCLUIDO, CANCELADO] (opcional)
      - data_checklist=YYYY-MM-DD (opcional)
      - include_team=true (opcional; se operador for supervisor, inclui equipe)
      - page, page_size (opcionais; default 1 e 20)
    """
    try:
        operador_id = request.GET.get('operador_id')
        if not operador_id:
            return Response({'success': False, 'error': 'operador_id é obrigatório'}, status=400)

        try:
            operador = Operador.objects.get(id=operador_id, ativo_bot=True, status='ATIVO')
        except Operador.DoesNotExist:
            return Response({'success': False, 'error': 'Operador não autorizado'}, status=403)

        include_team = request.GET.get('include_team', 'false').lower() == 'true'
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)

        qs = ChecklistNR12.objects.all().select_related('equipamento', 'responsavel')

        # Escopo de equipamentos permitidos
        equipamentos_permitidos = operador.get_equipamentos_disponiveis()
        qs = qs.filter(equipamento__in=equipamentos_permitidos)

        # Filtros opcionais
        equipamento_id = request.GET.get('equipamento_id')
        if equipamento_id:
            qs = qs.filter(equipamento_id=equipamento_id)

        status_param = request.GET.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        data_param = request.GET.get('data_checklist')
        if data_param:
            qs = qs.filter(data_checklist=data_param)

        # Incluir checklists da equipe (apenas se for supervisor e include_team=true)
        if include_team and operador.operadores_supervisionados.exists():
            equipamentos_equipe = []
            for sup in operador.operadores_supervisionados.filter(status='ATIVO', ativo_bot=True):
                equipamentos_equipe.append(sup.get_equipamentos_disponiveis().values_list('id', flat=True))
            # Union de IDs
            from itertools import chain
            ids_equipe = set(chain.from_iterable(equipamentos_equipe))
            qs = qs | ChecklistNR12.objects.filter(equipamento_id__in=ids_equipe)

        qs = qs.order_by('-id')

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        results = []
        for c in page_obj:
            results.append({
                'id': c.id,
                'status': c.status,
                'turno': getattr(c, 'turno', 'MANHA'),
                'data_checklist': c.data_checklist.strftime('%Y-%m-%d') if c.data_checklist else None,
                'equipamento': {
                    'id': c.equipamento.id,
                    'nome': c.equipamento.nome,
                    'codigo': getattr(c.equipamento, 'codigo', f"EQ{c.equipamento.id:04d}")
                },
                'responsavel': getattr(c.responsavel, 'username', None),
                'percentual_conclusao': getattr(c, 'percentual_conclusao', None),
            })

        return Response({
            'success': True,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'results': results
        })
    except Exception as e:
        return Response({'success': False, 'error': f'Erro interno: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def equipamentos_operador(request, operador_id):
    """
    Equipamentos disponíveis para um operador (respeita autorização e supervisão).
    Parâmetros: page, page_size
    """
    try:
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)

        try:
            operador = Operador.objects.get(id=operador_id, ativo_bot=True, status='ATIVO')
        except Operador.DoesNotExist:
            return Response({'success': False, 'error': 'Operador não autorizado'}, status=403)

        equipamentos = operador.get_equipamentos_disponiveis()
        paginator = Paginator(equipamentos, page_size)
        page_obj = paginator.get_page(page)

        supervisor_info = {}
        if operador.operadores_supervisionados.exists():
            supervisionados = operador.operadores_supervisionados.filter(status='ATIVO')
            supervisor_info = {
                'is_supervisor': True,
                'supervisionados_count': supervisionados.count(),
                'supervisionados': [
                    {
                        'id': sup.id,
                        'nome': sup.nome,
                        'codigo': sup.codigo,
                        'equipamentos_count': sup.get_equipamentos_disponiveis().count()
                    } for sup in supervisionados[:10]
                ]
            }

        items = []
        for eq in page_obj:
            # há checklist pendente hoje?
            chk = ChecklistNR12.objects.filter(
                equipamento=eq, data_checklist=date.today(),
                status__in=['PENDENTE', 'EM_ANDAMENTO']
            ).first()

            items.append({
                'id': eq.id,
                'nome': eq.nome,
                'codigo': getattr(eq, 'codigo', f"EQ{eq.id:04d}"),
                'cliente': {'id': eq.cliente.id, 'nome': eq.cliente.nome} if eq.cliente else None,
                'status_operacional': getattr(eq, 'status_operacional', 'OPERACIONAL'),
                'ativo_nr12': getattr(eq, 'ativo_nr12', True),
                'checklist_hoje': {
                    'id': chk.id, 'status': chk.status, 'turno': getattr(chk, 'turno', 'MANHA')
                } if chk else None,
                'pode_operar': operador.pode_operar_equipamento(eq),
            })

        return Response({
            'success': True,
            'operador': {
                'id': operador.id,
                'nome': operador.nome,
                'codigo': operador.codigo,
                **supervisor_info
            },
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'results': items
        })
    except Exception as e:
        return Response({'success': False, 'error': f'Erro interno: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def criar_checklist_equipamento(request):
    """
    Cria um checklist para um equipamento (usado pelo bot).
    Body JSON: {equipamento_id:int, operador_codigo:str, turno:str=MANHA, frequencia:str=DIARIO}
    """
    try:
        data = request.data
        equipamento_id = data.get('equipamento_id')
        operador_codigo = data.get('operador_codigo')
        turno = data.get('turno', 'MANHA')

        if not equipamento_id or not operador_codigo:
            return Response({'success': False, 'error': 'Parâmetros obrigatórios ausentes'}, status=400)

        try:
            operador = Operador.objects.get(codigo=operador_codigo, ativo_bot=True, status='ATIVO')
        except Operador.DoesNotExist:
            return Response({'success': False, 'error': 'Operador não autorizado'}, status=403)

        try:
            equipamento = Equipamento.objects.get(id=equipamento_id, ativo_nr12=True)
        except Equipamento.DoesNotExist:
            return Response({'success': False, 'error': 'Equipamento não encontrado'}, status=404)

        if not operador.pode_operar_equipamento(equipamento):
            return Response({'success': False, 'error': 'Operador não autorizado para este equipamento'}, status=403)

        existente = ChecklistNR12.objects.filter(
            equipamento=equipamento, data_checklist=date.today(), turno=turno
        ).first()
        if existente:
            return Response({
                'success': True,
                'message': 'Checklist já existe para hoje',
                'checklist': {'id': existente.id, 'status': existente.status, 'turno': existente.turno}
            })

        checklist = ChecklistNR12.objects.create(
            equipamento=equipamento,
            data_checklist=date.today(),
            turno=turno,
            status='PENDENTE',
            responsavel=operador.user if hasattr(operador, 'user') else None
        )

        # Gerar itens (se tiver task/função disponível)
        total_itens = 0
        try:
            from backend.apps.core.tasks import criar_itens_checklist
            total_itens = criar_itens_checklist(checklist)
        except Exception:
            pass

        return Response({
            'success': True,
            'message': 'Checklist criado',
            'checklist': {
                'id': checklist.id,
                'status': checklist.status,
                'turno': checklist.turno,
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'total_itens': total_itens
            }
        })
    except Exception as e:
        return Response({'success': False, 'error': f'Erro interno: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_checklist(request, checklist_id):
    """
    Inicia um checklist (muda status para EM_ANDAMENTO)
    """
    try:
        operador_codigo = request.data.get('operador_codigo')
        
        # Validar operador
        try:
            operador = Operador.objects.get(
                codigo=operador_codigo,
                ativo_bot=True,
                status='ATIVO'
            )
        except Operador.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Operador não autorizado'
            }, status=403)
        
        # Buscar checklist
        try:
            checklist = ChecklistNR12.objects.get(id=checklist_id)
        except ChecklistNR12.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Checklist não encontrado'
            }, status=404)
        
        # Verificar se pode iniciar
        if not operador.pode_iniciar_checklist(checklist_id):
            return Response({
                'success': False,
                'error': 'Não autorizado a iniciar este checklist'
            }, status=403)
        
        # Iniciar checklist
        from django.utils import timezone
        checklist.status = 'EM_ANDAMENTO'
        checklist.data_inicio = timezone.now()
        if not checklist.responsavel:
            checklist.responsavel = operador.user if hasattr(operador, 'user') else None
        checklist.save()
        
        # Atualizar último acesso do operador
        operador.atualizar_ultimo_acesso()
        
        return Response({
            'success': True,
            'message': 'Checklist iniciado com sucesso',
            'checklist': {
                'id': checklist.id,
                'status': checklist.status,
                'data_inicio': checklist.data_inicio.isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)