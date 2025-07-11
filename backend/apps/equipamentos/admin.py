from django.contrib import admin
from .models import Equipamento

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    """Admin completo para equipamentos"""
    list_display = ('nome', 'cliente', 'empreendimento', 'tipo', 'marca', 'modelo', 'ativo_nr12')
    list_filter = ('cliente', 'empreendimento', 'tipo', 'marca', 'ativo_nr12', 'frequencia_checklist')
    search_fields = ('nome', 'marca', 'modelo', 'n_serie')
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'cliente', 'empreendimento')
        }),
        ('Especificações Técnicas', {
            'fields': ('tipo', 'marca', 'modelo', 'n_serie', 'horimetro')
        }),
        ('Configurações NR12', {
            'fields': ('tipo_nr12', 'frequencia_checklist', 'ativo_nr12'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente', 'empreendimento', 'tipo_nr12')