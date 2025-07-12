# backend/apps/dashboard/admin.py
# ================================================================

from django.contrib import admin
from .models import KPISnapshot, AlertaDashboard

@admin.register(KPISnapshot)
class KPISnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'data_snapshot', 'total_equipamentos', 'checklists_concluidos', 
        'alertas_criticos', 'calculado_em'
    )
    list_filter = ('data_snapshot',)
    readonly_fields = ('calculado_em',)
    ordering = ('-data_snapshot',)
    
    actions = ['recalcular_kpis']
    
    def recalcular_kpis(self, request, queryset):
        for snapshot in queryset:
            KPISnapshot.calcular_kpis_hoje()
        self.message_user(request, 'KPIs recalculados com sucesso!')
    recalcular_kpis.short_description = 'Recalcular KPIs selecionados'

@admin.register(AlertaDashboard)
class AlertaDashboardAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'prioridade', 'ativo', 'criado_em')
    list_filter = ('tipo', 'prioridade', 'ativo')
    search_fields = ('titulo', 'descricao')
    ordering = ('-prioridade', '-criado_em')
