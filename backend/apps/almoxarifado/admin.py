# backend/apps/almoxarifado/admin.py

from django.contrib import admin
from .models import Produto, MovimentacaoEstoque, EstoqueCombustivel


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'unidade_medida', 'estoque_atual')
    search_fields = ('codigo', 'descricao')


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'data', 'origem')
    list_filter = ('tipo', 'data')
    search_fields = ('produto__descricao', 'origem')


@admin.register(EstoqueCombustivel)
class EstoqueCombustivelAdmin(admin.ModelAdmin):
    list_display = (
        'tipo_combustivel',
        'quantidade_em_estoque',
        'estoque_minimo',
        'abaixo_do_minimo',
        'valor_compra',
        'ativo'
    )
    list_filter = ('ativo',)
    search_fields = ('tipo_combustivel__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        (None, {
            'fields': (
                'tipo_combustivel',
                'quantidade_em_estoque',
                'estoque_minimo',
                'valor_compra',
                'ativo',
            )
        }),
        ('Controle de Auditoria', {
            'classes': ('collapse',),
            'fields': ('criado_em', 'atualizado_em'),
        }),
    )
