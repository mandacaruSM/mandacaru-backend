# ================================================================
# SUBSTITUIR backend/apps/equipamentos/admin.py
# ================================================================

from django.contrib import admin
from .models import Equipamento, CategoriaEquipamento

@admin.register(CategoriaEquipamento)
class CategoriaEquipamentoAdmin(admin.ModelAdmin):
    """Admin para categorias de equipamentos"""
    list_display = ('codigo', 'nome', 'prefixo_codigo', 'total_equipamentos', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome', 'descricao')
    ordering = ('codigo',)
    
    def total_equipamentos(self, obj):
        """Mostra total de equipamentos da categoria"""
        return obj.equipamentos.count()
    total_equipamentos.short_description = 'Total de Equipamentos'

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    """Admin melhorado para equipamentos"""
    
    list_display = (
        'nome', 'categoria', 'marca', 'modelo', 'cliente', 'ativo_nr12', 'created_at'
    )
    list_filter = ('categoria', 'ativo_nr12', 'frequencia_checklist', 'marca', 'cliente')
    search_fields = ('nome', 'marca', 'modelo', 'n_serie')
    ordering = ('categoria', 'nome')
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                ('nome', 'categoria'),
                'descricao'
            )
        }),
        ('Especificações Técnicas', {
            'fields': (
                ('marca', 'modelo'),
                'n_serie',
                'horimetro'
            )
        }),
        ('Localização', {
            'fields': (
                ('cliente', 'empreendimento'),
            )
        }),
        ('NR12 e Segurança', {
            'fields': (
                ('tipo_nr12', 'ativo_nr12'),
                'frequencia_checklist',
            )
        }),
        ('Controle', {
            'fields': (
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'categoria', 'cliente', 'empreendimento', 'tipo_nr12'
        )

# Personalizar título do admin
admin.site.site_header = "Mandacaru ERP - Gestão de Equipamentos"
admin.site.site_title = "Mandacaru ERP"
admin.site.index_title = "Painel Administrativo"