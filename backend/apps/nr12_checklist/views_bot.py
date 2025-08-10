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


@api_view(['GET'])
@permission_classes([AllowAny])
def checklists_bot(request):
    """
    Lista checklists para o Bot Telegram
    CORRIGIDO: Inclui paginação e filtros de supervisor
    """
    try:
        # Obter parâmetros de filtro
        operador_id = request.GET.get('operador_id')
        equipamento_id = request.GET.get('equipamento_id')
        status = request.GET.get('status', 'PENDENTE')
        data_checklist = request.GET.get('data_checklist')
        include_team = request.GET.get('include_team', 'false').lower() == 'true'
        
        # Parâmetros de paginação
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 10)), 50)  # Máximo 50 itens
        
        # Construir queryset base
        queryset = ChecklistNR12.objects.select_related(
            'equipamento', 
            'equipamento__cliente', 
            'responsavel'
        ).prefetch_related('itens')
        
        # Filtrar por operador (equipamentos que ele pode acessar)
        if operador_id:
            try:
                operador = Operador.objects.get(id=operador_id, ativo_bot=True, status='ATIVO')
                equipamentos_disponiveis = operador.get_equipamentos_disponiveis()
                queryset = queryset.filter(equipamento__in=equipamentos_disponiveis)
                
                # ✅ NOVO: Se include_team=true e é supervisor, incluir checklists da equipe
                if include_team and operador.operadores_supervisionados.exists():
                    supervisionados_ids = operador.operadores_supervisionados.filter(
                        status='ATIVO'
                    ).values_list('user_id', flat=True)
                    
                    # Incluir checklists dos supervisionados
                    checklists_equipe = ChecklistNR12.objects.filter(
                        responsavel_id__in=supervisionados_ids
                    )
                    queryset = queryset.union(checklists_equipe)
                
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
        
        # Ordenar por data mais recente
        queryset = queryset.order_by('-data_checklist', '-created_at')
        
        # ✅ PAGINAÇÃO CORRIGIDA
        paginator = Paginator(queryset, page_size)
        
        if page > paginator.num_pages:
            page = paginator.num_pages or 1
        
        page_obj = paginator.get_page(page)
        
        # Serializar resultados
        checklists_data = []
        for checklist in page_obj:
            # Calcular progresso
            total_itens = checklist.itens.count()
            itens_respondidos = checklist.itens.exclude(status='PENDENTE').count()
            percentual_conclusao = (itens_respondidos / total_itens * 100) if total_itens > 0 else 0
            
            checklists_data.append({
                'id': checklist.id,
                'uuid': str(checklist.uuid) if hasattr(checklist, 'uuid') else None,
                'equipamento': {
                    'id': checklist.equipamento.id,
                    'nome': checklist.equipamento.nome,
                    'codigo': getattr(checklist.equipamento, 'codigo', f'EQ{checklist.equipamento.id:04d}'),
                    'cliente': checklist.equipamento.cliente.nome if checklist.equipamento.cliente else None
                },
                'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d'),
                'turno': getattr(checklist, 'turno', 'MANHA'),
                'status': checklist.status,
                'responsavel': {
                    'id': checklist.responsavel.id,
                    'username': checklist.responsavel.username,
                    'nome': getattr(checklist.responsavel, 'first_name', '') or checklist.responsavel.username
                } if checklist.responsavel else None,
                'total_itens': total_itens,
                'itens_respondidos': itens_respondidos,
                'percentual_conclusao': round(percentual_conclusao, 1),
                'data_criacao': checklist.created_at.isoformat() if hasattr(checklist, 'created_at') else None,
                'data_inicio': checklist.data_inicio.isoformat() if hasattr(checklist, 'data_inicio') and checklist.data_inicio else None,
                'data_conclusao': checklist.data_conclusao.isoformat() if hasattr(checklist, 'data_conclusao') and checklist.data_conclusao else None
            })
        
        return Response({
            'success': True,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'results': checklists_data,
            'filters_applied': {
                'operador_id': operador_id,
                'equipamento_id': equipamento_id,
                'status': status,
                'data_checklist': data_checklist,
                'include_team': include_team
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
    Lista equipamentos disponíveis para um operador
    CORRIGIDO: Inclui equipamentos de supervisionados se for supervisor
    """
    try:
        # Parâmetros
        include_supervisionados = request.GET.get('include_supervisionados', 'false').lower() == 'true'
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # Buscar operador
        try:
            operador = Operador.objects.get(
                id=operador_id, 
                ativo_bot=True, 
                status='ATIVO'
            )
        except Operador.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Operador não encontrado ou não autorizado'
            }, status=404)
        
        # Obter equipamentos disponíveis (já inclui lógica de supervisor)
        equipamentos = operador.get_equipamentos_disponiveis()
        
        # ✅ INFORMAÇÕES ADICIONAIS PARA SUPERVISORES
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
                    } for sup in supervisionados[:10]  # Limite para performance
                ]
            }
        
        # Paginação
        paginator = Paginator(equipamentos, page_size)
        page_obj = paginator.get_page(page)
        
        # Serializar equipamentos
        equipamentos_data = []
        for eq in page_obj:
            # Verificar se tem checklist pendente hoje
            checklist_hoje = ChecklistNR12.objects.filter(
                equipamento=eq,
                data_checklist=date.today(),
                status__in=['PENDENTE', 'EM_ANDAMENTO']
            ).first()
            
            equipamentos_data.append({
                'id': eq.id,
                'nome': eq.nome,
                'codigo': getattr(eq, 'codigo', f'EQ{eq.id:04d}'),
                'marca': getattr(eq, 'marca', ''),
                'modelo': getattr(eq, 'modelo', ''),
                'categoria': eq.categoria.nome if hasattr(eq, 'categoria') and eq.categoria else 'N/A',
                'status_operacional': getattr(eq, 'status_operacional', 'OPERACIONAL'),
                'cliente': {
                    'id': eq.cliente.id,
                    'nome': eq.cliente.nome
                } if eq.cliente else None,
                'horimetro_atual': getattr(eq, 'horimetro_atual', 0),
                'ativo_nr12': getattr(eq, 'ativo_nr12', True),
                'checklist_hoje': {
                    'id': checklist_hoje.id,
                    'status': checklist_hoje.status,
                    'turno': getattr(checklist_hoje, 'turno', 'MANHA')
                } if checklist_hoje else None,
                'pode_operar': operador.pode_operar_equipamento(eq)
            })
        
        return Response({
            'success': True,
            'operador': {
                'id': operador.id,
                'nome': operador.nome,
                'codigo': operador.codigo,
                'funcao': operador.funcao,
                **supervisor_info
            },
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'results': equipamentos_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def criar_checklist_equipamento(request):
    """
    Cria um novo checklist para um equipamento
    NOVO ENDPOINT para criação via bot
    """
    try:
        data = request.data
        equipamento_id = data.get('equipamento_id')
        operador_codigo = data.get('operador_codigo')
        turno = data.get('turno', 'MANHA')
        frequencia = data.get('frequencia', 'DIARIO')
        
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
                'error': 'Operador não encontrado ou não autorizado'
            }, status=403)
        
        # Validar equipamento
        try:
            equipamento = Equipamento.objects.get(id=equipamento_id, ativo_nr12=True)
        except Equipamento.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Equipamento não encontrado'
            }, status=404)
        
        # Verificar se operador pode operar o equipamento
        if not operador.pode_operar_equipamento(equipamento):
            return Response({
                'success': False,
                'error': 'Operador não autorizado para este equipamento'
            }, status=403)
        
        # Verificar se já existe checklist para hoje
        checklist_existente = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            data_checklist=date.today(),
            turno=turno
        ).first()
        
        if checklist_existente:
            return Response({
                'success': True,
                'message': 'Checklist já existe para hoje',
                'checklist': {
                    'id': checklist_existente.id,
                    'status': checklist_existente.status,
                    'turno': checklist_existente.turno
                }
            })
        
        # Criar novo checklist
        checklist = ChecklistNR12.objects.create(
            equipamento=equipamento,
            data_checklist=date.today(),
            turno=turno,
            status='PENDENTE',
            responsavel=operador.user if hasattr(operador, 'user') else None
        )
        
        # Criar itens do checklist usando task
        try:
            from backend.apps.core.tasks import criar_itens_checklist
            itens_criados = criar_itens_checklist(checklist)
            
            return Response({
                'success': True,
                'message': 'Checklist criado com sucesso',
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid) if hasattr(checklist, 'uuid') else None,
                    'status': checklist.status,
                    'turno': checklist.turno,
                    'total_itens': itens_criados,
                    'data_checklist': checklist.data_checklist.strftime('%Y-%m-%d')
                }
            })
            
        except Exception as e:
            # Se falhar ao criar itens, deletar checklist
            checklist.delete()
            return Response({
                'success': False,
                'error': f'Erro ao criar itens do checklist: {str(e)}'
            }, status=500)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


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