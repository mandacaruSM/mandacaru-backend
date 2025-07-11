from django.contrib import admin
from .models import TipoEquipamentoNR12, ItemChecklistPadrao, ChecklistNR12, ItemChecklistRealizado, AlertaManutencao

@admin.register(TipoEquipamentoNR12)
class TipoEquipamentoNR12Admin(admin.ModelAdmin):
    list_display = ('nome', 'created_at')
    search_fields = ('nome', 'descricao')

@admin.register(ItemChecklistPadrao)
class ItemChecklistPadraoAdmin(admin.ModelAdmin):
    list_display = ('item', 'tipo_equipamento', 'criticidade', 'ordem', 'ativo')
    list_filter = ('criticidade', 'ativo', 'tipo_equipamento')
    search_fields = ('item', 'descricao')
    ordering = ('tipo_equipamento', 'ordem')

@admin.register(ChecklistNR12)
class ChecklistNR12Admin(admin.ModelAdmin):
    list_display = ('equipamento', 'data_checklist', 'turno', 'status', 'responsavel')
    list_filter = ('status', 'turno', 'data_checklist')
    search_fields = ('equipamento__nome', 'responsavel__username')
    readonly_fields = ('uuid', 'created_at', 'updated_at')

@admin.register(ItemChecklistRealizado)
class ItemChecklistRealizadoAdmin(admin.ModelAdmin):
    list_display = ('checklist', 'item_padrao', 'status', 'verificado_por', 'verificado_em')
    list_filter = ('status', 'verificado_em')
    search_fields = ('checklist__equipamento__nome', 'item_padrao__item')

@admin.register(AlertaManutencao)
class AlertaManutencaoAdmin(admin.ModelAdmin):
    list_display = ('equipamento', 'titulo', 'tipo', 'criticidade', 'status', 'data_prevista')
    list_filter = ('tipo', 'status', 'criticidade', 'data_prevista')
    search_fields = ('equipamento__nome', 'titulo', 'descricao')