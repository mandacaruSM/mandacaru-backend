# ================================================================
# SUBSTITUIR backend/apps/clientes/admin.py
# ================================================================

from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'nome_fantasia', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'nome_fantasia', 'cnpj')  # ✅ ADICIONAR search_fields
    list_filter = ('estado', 'cidade')
    ordering = ('razao_social',)
    
    fieldsets = (
        ('Dados da Empresa', {
            'fields': (
                ('razao_social', 'nome_fantasia'),
                ('cnpj', 'inscricao_estadual'),
                ('email', 'telefone')
            )
        }),
        ('Endereço', {
            'fields': (
                ('rua', 'numero'),
                ('bairro', 'cidade'),
                ('estado', 'cep')
            )
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )