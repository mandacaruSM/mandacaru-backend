# ================================================================
# SUBSTITUIR backend/apps/empreendimentos/admin.py
# ================================================================

from django.contrib import admin
from .models import Empreendimento

@admin.register(Empreendimento)
class EmpreendimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'cidade', 'estado', 'distancia_km')
    search_fields = ('nome', 'cliente__razao_social', 'cidade')  # ✅ ADICIONAR search_fields
    list_filter = ('estado', 'cidade')
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                ('nome', 'cliente'),
                'descricao'
            )
        }),
        ('Localização', {
            'fields': (
                'endereco',
                ('cidade', 'estado'),
                'cep',
                'distancia_km'
            )
        }),
    )