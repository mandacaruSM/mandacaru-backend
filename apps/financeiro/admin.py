from django.contrib import admin
from .models import Lancamento

@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descricao', 'valor', 'data', 'ordem_servico')
    list_filter = ('tipo', 'data')
    search_fields = ('descricao',)