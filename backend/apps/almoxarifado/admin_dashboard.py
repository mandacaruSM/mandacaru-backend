# ----------------------------------------------------------------
# 8. DASHBOARD ADMIN PERSONALIZADO
# backend/apps/almoxarifado/admin_dashboard.py
# ----------------------------------------------------------------

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import EstoqueCombustivel
from backend.apps.abastecimento.models import RegistroAbastecimento
from datetime import date, timedelta

class AlmoxarifadoDashboardMixin:
    """Mixin para adicionar dashboard ao admin do almoxarifado"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='almoxarifado_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """View do dashboard do almoxarifado"""
        # Estatísticas de estoque
        estoques = EstoqueCombustivel.objects.filter(ativo=True)
        total_combustiveis = estoques.count()
        com_estoque_baixo = sum(1 for e in estoques if e.abaixo_do_minimo)
        valor_total_estoque = sum(
            e.quantidade_em_estoque * e.valor_compra for e in estoques
        )
        
        # Estatísticas de abastecimentos (últimos 30 dias)
        data_inicio = date.today() - timedelta(days=30)
        abastecimentos_almox = RegistroAbastecimento.objects.filter(
            origem_combustivel='ALMOXARIFADO',
            data_abastecimento__date__gte=data_inicio
        )
        
        stats_abastecimento = abastecimentos_almox.aggregate(
            total=Count('id'),
            total_litros=Sum('quantidade_litros'),
            total_valor=Sum('valor_total')
        )
        
        # Top equipamentos que mais consomem do almoxarifado
        top_equipamentos = abastecimentos_almox.values(
            'equipamento__nome'
        ).annotate(
            total_litros=Sum('quantidade_litros'),
            total_abastecimentos=Count('id')
        ).order_by('-total_litros')[:5]
        
        context = {
            'title': 'Dashboard do Almoxarifado',
            'estoques': estoques,
            'estatisticas': {
                'total_combustiveis': total_combustiveis,
                'com_estoque_baixo': com_estoque_baixo,
                'valor_total_estoque': valor_total_estoque,
                'abastecimentos_30_dias': stats_abastecimento['total'] or 0,
                'litros_30_dias': float(stats_abastecimento['total_litros'] or 0),
                'valor_30_dias': float(stats_abastecimento['total_valor'] or 0),
            },
            'top_equipamentos': top_equipamentos,
            'alertas_estoque': [e for e in estoques if e.abaixo_do_minimo],
        }
        
        return render(request, 'admin/almoxarifado/dashboard.html', context)