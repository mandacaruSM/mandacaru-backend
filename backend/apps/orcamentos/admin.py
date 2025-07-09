from django.contrib import admin
from .models import Orcamento

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'empreendimento',
        'valor_total',   # <— aqui antes estava 'valor'
        'status',
        'data_criacao',
    )
    list_filter = ('status', 'data_criacao')
    search_fields = ('cliente__nome_fantasia',)
