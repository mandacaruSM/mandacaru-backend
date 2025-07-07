from django.contrib import admin
from .models import HistoricoManutencao

@admin.register(HistoricoManutencao)
class HistoricoManutencaoAdmin(admin.ModelAdmin):
    list_display = ('equipamento', 'data', 'tipo', 'descricao')
    list_filter = ('tipo', 'data')
    search_fields = ('descricao',)
