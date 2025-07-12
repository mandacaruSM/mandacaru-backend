# ================================================================
# MELHORAR backend/apps/dashboard/views.py
# ================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from datetime import date, timedelta, datetime
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import KPISnapshot, AlertaDashboard, obter_resumo_dashboard, criar_alertas_automaticos

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_principal(request):
    """API principal do dashboard"""
    try:
        # Atualizar alertas automáticos
        criar_alertas_automaticos()
        
        # Obter resumo completo
        resumo = obter_resumo_dashboard()
        
        return Response({
            'success': True,
            'data': resumo,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpis_api(request):
    """API com KPIs em tempo real"""
    try:
        # Calcular KPIs atuais
        snapshot = KPISnapshot.calcular_kpis_hoje()
        
        # Dados adicionais
        hoje = date.today()
        
        # Tendências (comparar com semana passada)
        semana_passada = hoje - timedelta(days=7)
        snapshot_anterior = KPISnapshot.objects.filter(
            data_snapshot=semana_passada
        ).first()
        
        # Calcular tendências
        tendencias = {}
        if snapshot_anterior:
            campos_numericos = [
                'total_equipamentos', 'equipamentos_operacionais', 
                'checklists_concluidos', 'alertas_criticos'
            ]
            for campo in campos_numericos:
                atual = getattr(snapshot, campo, 0)
                anterior = getattr(snapshot_anterior, campo, 0)
                if anterior > 0:
                    tendencias[campo] = round(((atual - anterior) / anterior) * 100, 1)
                else:
                    tendencias[campo] = 0
        
        # Dados para gráficos
        ultimos_7_dias = []
        for i in range(7):
            data = hoje - timedelta(days=i)
            snap = KPISnapshot.objects.filter(data_snapshot=data).first()
            if snap:
                ultimos_7_dias.append({
                    'data': data.strftime('%d/%m'),
                    'checklists_concluidos': snap.checklists_concluidos,
                    'checklists_pendentes': snap.checklists_pendentes,
                    'equipamentos_operacionais': snap.equipamentos_operacionais
                })
        
        ultimos_7_dias.reverse()  # Ordem cronológica
        
        # Alertas ativos
        alertas = AlertaDashboard.objects.filter(
            ativo=True,
            exibir_ate__isnull=True  # Ou maior que agora
        )[:5]
        
        alertas_data = []
        for alerta in alertas:
            alertas_data.append({
                'tipo': alerta.tipo,
                'titulo': alerta.titulo,
                'descricao': alerta.descricao,
                'prioridade': alerta.prioridade,
                'cor': alerta.cor_prioridade,
                'icone': alerta.icone or '⚠️',
                'link': alerta.link_acao
            })
        
        # Distribuição por categoria
        try:
            from backend.apps.equipamentos.models import Equipamento
            categorias = Equipamento.objects.filter(ativo=True).values(
                'categoria__nome'
            ).annotate(
                total=Count('id'),
                operacionais=Count('id', filter=Q(status='OPERACIONAL')),
                manutencao=Count('id', filter=Q(status='MANUTENCAO'))
            ).order_by('-total')[:5]
        except:
            categorias = []
        
        return Response({
            'kpis': {
                'total_equipamentos': snapshot.total_equipamentos,
                'equipamentos_operacionais': snapshot.equipamentos_operacionais,
                'equipamentos_manutencao': snapshot.equipamentos_manutencao,
                'equipamentos_parados': snapshot.equipamentos_parados,
                'equipamentos_nr12_ativos': snapshot.equipamentos_nr12_ativos,
                'checklists_pendentes': snapshot.checklists_pendentes,
                'checklists_concluidos': snapshot.checklists_concluidos,
                'checklists_com_problemas': snapshot.checklists_com_problemas,
                'manutencoes_vencidas': snapshot.manutencoes_vencidas,
                'manutencoes_proximas': snapshot.manutencoes_proximas,
                'alertas_criticos': snapshot.alertas_criticos,
                'alertas_ativos': snapshot.alertas_ativos,
                'contas_vencidas': float(snapshot.contas_vencidas),
                'contas_a_vencer': float(snapshot.contas_a_vencer),
                'faturamento_mes': float(snapshot.faturamento_mes),
                'produtos_estoque_baixo': snapshot.produtos_estoque_baixo,
            },
            'tendencias': tendencias,
            'graficos': {
                'ultimos_7_dias': ultimos_7_dias,
                'categorias': list(categorias)
            },
            'alertas': alertas_data,
            'atualizado_em': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': 'Erro ao carregar KPIs',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def equipamentos_resumo(request):
    """Resumo detalhado dos equipamentos"""
    try:
        from backend.apps.equipamentos.models import Equipamento
        
        # Equipamentos por status
        por_status = Equipamento.objects.filter(ativo=True).values('status').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Equipamentos por categoria
        por_categoria = Equipamento.objects.filter(ativo=True).values(
            'categoria__nome', 'categoria__codigo'
        ).annotate(
            total=Count('id'),
            operacionais=Count('id', filter=Q(status='OPERACIONAL')),
            manutencao=Count('id', filter=Q(status='MANUTENCAO'))
        ).order_by('-total')
        
        # Equipamentos com manutenção próxima
        hoje = date.today()
        manutencao_proxima = Equipamento.objects.filter(
            ativo=True,
            proxima_manutencao_preventiva__range=[hoje, hoje + timedelta(days=30)]
        ).select_related('categoria').order_by('proxima_manutencao_preventiva')[:10]
        
        manutencao_data = []
        for eq in manutencao_proxima:
            dias = (eq.proxima_manutencao_preventiva - hoje).days
            manutencao_data.append({
                'id': eq.id,
                'codigo': eq.codigo,
                'nome': eq.nome,
                'categoria': eq.categoria.nome if eq.categoria else 'Sem categoria',
                'dias_restantes': dias,
                'urgente': dias <= 7,
                'data_manutencao': eq.proxima_manutencao_preventiva.isoformat()
            })
        
        return Response({
            'por_status': list(por_status),
            'por_categoria': list(por_categoria),
            'manutencao_proxima': manutencao_data
        })
        
    except Exception as e:
        return Response({
            'error': 'Erro ao buscar dados de equipamentos',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checklist_resumo(request):
    """Resumo dos checklists NR12"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        hoje = date.today()
        
        # Checklists de hoje
        hoje_stats = ChecklistNR12.objects.filter(data_checklist=hoje).aggregate(
            total=Count('id'),
            pendentes=Count('id', filter=Q(status='PENDENTE')),
            concluidos=Count('id', filter=Q(status='CONCLUIDO')),
            problemas=Count('id', filter=Q(status='CONCLUIDO', necessita_manutencao=True))
        )
        
        # Últimos 7 dias
        semana_passada = hoje - timedelta(days=7)
        ultimos_7_dias = ChecklistNR12.objects.filter(
            data_checklist__gte=semana_passada
        ).values('data_checklist').annotate(
            total=Count('id'),
            concluidos=Count('id', filter=Q(status='CONCLUIDO')),
            problemas=Count('id', filter=Q(necessita_manutencao=True))
        ).order_by('data_checklist')
        
        # Performance por equipamento
        performance = ChecklistNR12.objects.filter(
            data_checklist__gte=semana_passada,
            status='CONCLUIDO'
        ).values(
            'equipamento__codigo', 'equipamento__nome'
        ).annotate(
            total_checklists=Count('id'),
            com_problemas=Count('id', filter=Q(necessita_manutencao=True))
        ).order_by('-total_checklists')[:10]
        
        return Response({
            'hoje': hoje_stats,
            'ultimos_7_dias': list(ultimos_7_dias),
            'performance_equipamentos': list(performance)
        })
        
    except Exception as e:
        return Response({
            'error': 'Erro ao buscar dados de checklists',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recalcular_kpis(request):
    """Força recálculo dos KPIs"""
    try:
        snapshot = KPISnapshot.calcular_kpis_hoje()
        criar_alertas_automaticos()
        
        return Response({
            'success': True,
            'message': 'KPIs recalculados com sucesso',
            'data_snapshot': snapshot.data_snapshot,
            'calculado_em': snapshot.calculado_em.isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financeiro_resumo(request):
    """Resumo financeiro"""
    try:
        from backend.apps.financeiro.models import ContaFinanceira
        
        hoje = date.today()
        
        # Contas por status
        contas_stats = ContaFinanceira.objects.aggregate(
            total_pendentes=Count('id', filter=Q(status='PENDENTE')),
            total_vencidas=Count('id', filter=Q(status='VENCIDO')),
            total_pagas=Count('id', filter=Q(status='PAGO')),
            valor_vencido=Sum('valor_restante', filter=Q(status='VENCIDO')) or 0,
            valor_pendente=Sum('valor_restante', filter=Q(status='PENDENTE')) or 0,
        )
        
        # Contas a vencer nos próximos 30 dias
        proximas_vencer = ContaFinanceira.objects.filter(
            status='PENDENTE',
            data_vencimento__range=[hoje, hoje + timedelta(days=30)]
        ).order_by('data_vencimento')[:10]
        
        vencimentos_data = []
        for conta in proximas_vencer:
            dias = (conta.data_vencimento - hoje).days
            vencimentos_data.append({
                'id': conta.id,
                'numero': conta.numero,
                'descricao': conta.descricao,
                'valor': float(conta.valor_restante),
                'data_vencimento': conta.data_vencimento.isoformat(),
                'dias_restantes': dias,
                'urgente': dias <= 7,
                'tipo': conta.tipo
            })
        
        # Faturamento mensal
        faturamento_mensal = ContaFinanceira.objects.filter(
            tipo='RECEBER',
            status='PAGO',
            data_pagamento__month=hoje.month,
            data_pagamento__year=hoje.year
        ).aggregate(
            total=Sum('valor_pago') or 0
        )
        
        return Response({
            'contas_stats': {
                'pendentes': contas_stats['total_pendentes'],
                'vencidas': contas_stats['total_vencidas'],
                'pagas': contas_stats['total_pagas'],
                'valor_vencido': float(contas_stats['valor_vencido']),
                'valor_pendente': float(contas_stats['valor_pendente']),
            },
            'proximas_vencer': vencimentos_data,
            'faturamento_mes': float(faturamento_mensal['total'])
        })
        
    except Exception as e:
        return Response({
            'error': 'Erro ao buscar dados financeiros',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estoque_resumo(request):
    """Resumo do estoque"""
    try:
        from backend.apps.almoxarifado.models import Produto, MovimentacaoEstoque
        
        hoje = date.today()
        
        # Produtos com estoque baixo
        estoque_baixo = Produto.objects.filter(
            estoque_atual__lt=5
        ).order_by('estoque_atual')[:10]
        
        produtos_baixo = []
        for produto in estoque_baixo:
            produtos_baixo.append({
                'id': produto.id,
                'codigo': produto.codigo,
                'descricao': produto.descricao,
                'estoque_atual': float(produto.estoque_atual),
                'unidade_medida': produto.unidade_medida,
                'critico': produto.estoque_atual <= 2
            })
        
        # Movimentações recentes
        movimentacoes_recentes = MovimentacaoEstoque.objects.select_related(
            'produto'
        ).order_by('-data')[:10]
        
        movimentacoes_data = []
        for mov in movimentacoes_recentes:
            movimentacoes_data.append({
                'id': mov.id,
                'produto': mov.produto.descricao,
                'tipo': mov.tipo,
                'quantidade': float(mov.quantidade),
                'data': mov.data.isoformat(),
                'origem': mov.origem or 'Sistema'
            })
        
        # Estatísticas gerais
        stats = Produto.objects.aggregate(
            total_produtos=Count('id'),
            produtos_zerados=Count('id', filter=Q(estoque_atual=0)),
            produtos_baixo=Count('id', filter=Q(estoque_atual__lt=5)),
            valor_total_estoque=Sum('estoque_atual') or 0
        )
        
        return Response({
            'estatisticas': {
                'total_produtos': stats['total_produtos'],
                'produtos_zerados': stats['produtos_zerados'],
                'produtos_baixo': stats['produtos_baixo'],
                'total_itens_estoque': float(stats['valor_total_estoque'])
            },
            'produtos_estoque_baixo': produtos_baixo,
            'movimentacoes_recentes': movimentacoes_data
        })
        
    except Exception as e:
        return Response({
            'error': 'Erro ao buscar dados de estoque',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alertas_dashboard(request):
    """Lista todos os alertas do dashboard"""
    try:
        alertas = AlertaDashboard.objects.filter(ativo=True).order_by('-prioridade', '-criado_em')
        
        alertas_data = []
        for alerta in alertas:
            alertas_data.append({
                'id': alerta.id,
                'tipo': alerta.tipo,
                'titulo': alerta.titulo,
                'descricao': alerta.descricao,
                'prioridade': alerta.prioridade,
                'cor': alerta.cor_prioridade,
                'icone': alerta.icone or '⚠️',
                'link_acao': alerta.link_acao,
                'criado_em': alerta.criado_em.isoformat(),
                'exibe_ate': alerta.exibir_ate.isoformat() if alerta.exibir_ate else None
            })
        
        return Response({
            'total': len(alertas_data),
            'alertas': alertas_data
        })
        
    except Exception as e:
        return Response({
            'error': 'Erro ao buscar alertas',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_alerta_lido(request, alerta_id):
    """Marca um alerta como lido (desativa)"""
    try:
        alerta = AlertaDashboard.objects.get(id=alerta_id)
        alerta.ativo = False
        alerta.save()
        
        return Response({
            'success': True,
            'message': 'Alerta marcado como lido'
        })
        
    except AlertaDashboard.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Alerta não encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_completo(request):
    """Dashboard completo com todos os dados"""
    try:
        # Calcular KPIs atuais
        snapshot = KPISnapshot.calcular_kpis_hoje()
        criar_alertas_automaticos()
        
        # Obter dados de todas as APIs
        kpis_data = kpis_api(request).data
        equipamentos_data = equipamentos_resumo(request).data
        checklist_data = checklist_resumo(request).data
        financeiro_data = financeiro_resumo(request).data
        estoque_data = estoque_resumo(request).data
        alertas_data = alertas_dashboard(request).data
        
        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'data': {
                'kpis': kpis_data,
                'equipamentos': equipamentos_data,
                'checklists': checklist_data,
                'financeiro': financeiro_data,
                'estoque': estoque_data,
                'alertas': alertas_data['alertas'][:5],  # Apenas os 5 mais importantes
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)