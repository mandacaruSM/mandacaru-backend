from django.contrib import admin
from .models import Produto, MovimentacaoEstoque

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'unidade_medida', 'estoque_atual')
    search_fields = ('codigo', 'descricao')

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'data', 'origem')
    list_filter = ('tipo', 'data')
    search_fields = ('produto__descricao', 'origem')
