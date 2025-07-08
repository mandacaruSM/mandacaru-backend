# backend/apps/orcamentos/admin.py
from django.contrib import admin
from .models import Orcamento

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'valor', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('cliente__nome_fantasia',)