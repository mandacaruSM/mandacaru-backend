# backend/apps/abastecimento/admin.py

from django.contrib import admin
from .models import TipoCombustivel, RegistroAbastecimento, RelatorioConsumo

@admin.register(TipoCombustivel)
class TipoCombustivelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'unidade_medida', 'preco_medio', 'ativo']
    search_fields = ['nome']

@admin.register(RegistroAbastecimento)
class RegistroAbastecimentoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'equipamento', 'data_abastecimento', 'quantidade_litros', 'valor_total', 'aprovado']
    list_filter = ['aprovado', 'tipo_combustivel']
    search_fields = ['numero', 'equipamento__nome']
    readonly_fields = ['numero', 'valor_total', 'criado_em', 'atualizado_em']

@admin.register(RelatorioConsumo)
class RelatorioConsumoAdmin(admin.ModelAdmin):
    list_display = ['equipamento', 'periodo_inicio', 'periodo_fim', 'total_litros', 'total_valor', 'consumo_medio_hora']
