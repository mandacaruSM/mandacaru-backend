from django.contrib import admin
from .models import OrdemServico

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'orcamento',
        'cliente',
        'data_abertura',  # <— aqui antes estava 'data_execucao'
        'finalizada',
    )
    list_filter = ('finalizada', 'data_abertura')
    search_fields = ('cliente__nome_fantasia',)
