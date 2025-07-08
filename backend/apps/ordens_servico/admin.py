# backend/apps/ordens_servico/admin.py
from django.contrib import admin
from .models import OrdemServico

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'orcamento', 'finalizada', 'data_execucao')
    list_filter = ('finalizada',)
