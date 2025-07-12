# backend/apps/dashboard/views.py
# ================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from datetime import date, timedelta, datetime
from django.utils import timezone

@login_required
@require_http_methods(["GET"])
def dashboard_principal(request):
    """View principal do dashboard"""
    return render(request, 'dashboard/principal.html')

@login_required
@require_http_methods(["GET"])
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
        from backend.apps.equipamentos.models import Equipamento
        categorias = Equipamento.objects.filter(ativo=True).values(
            'categoria__nome'
        ).annotate(
            total=Count('id'),
            operacionais=Count('id', filter=Q(status='OPERACIONAL')),
            manutencao=Count('id', filter=Q(status='MANUTENCAO'))
        ).order_by('-total')[:5]
        
        return JsonResponse({
            'kpis': {
                'total_equipamentos': snapshot.total_equipamentos,
                'equipamentos_operacionais': snapshot.equipamentos_operacionais,
                'equipamentos_manutencao': snapshot.equipamentos_manutencao,
                'equipamentos_parados': snapshot.equipamentos_parados,
                'checklists_pendentes': snapshot.checklists_pendentes,
                'checklists_concluidos': snapshot.checklists_concluidos,
                'checklists_com_problemas': snapshot.checklists_com_problemas,
                'manutencoes_vencidas': snapshot.manutencoes_vencidas,
                'manutencoes_proximas': snapshot.manutencoes_proximas,
                'alertas_criticos': snapshot.alertas_criticos,
                'contas_vencidas': float(snapshot.contas_vencidas),
                'contas_a_vencer': float(snapshot.contas_a_vencer),
                'faturamento_mes': float(snapshot.faturamento_mes),
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
        return JsonResponse({
            'error': 'Erro ao carregar KPIs',
            'message': str(e)
        }, status=500)

@login_required  
@require_http_methods(["GET"])
def equipamentos_resumo(request):
    """Resumo detalhado dos equipamentos"""
    from backend.apps.equipamentos.models import Equipamento
    
    # Equipamentos por status
    por_status = Equipamento.objects.filter(ativo=True).values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Equipamentos por categoria
    por_categoria = Equipamento.objects.filter(ativo=True).values(
        'categoria__nome', 'categoria__prefixo_codigo'
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
            'categoria': eq.categoria.nome,
            'dias_restantes': dias,
            'urgente': dias <= 7
        })
    
    return JsonResponse({
        'por_status': list(por_status),
        'por_categoria': list(por_categoria),
        'manutencao_proxima': manutencao_data
    })

@login_required
@require_http_methods(["GET"])
def checklist_resumo(request):
    """Resumo dos checklists NR12"""
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
    
    return JsonResponse({
        'hoje': hoje_stats,
        'ultimos_7_dias': list(ultimos_7_dias),
        'performance_equipamentos': list(performance)
    })

