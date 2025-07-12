# backend/apps/equipamentos/admin.py - VERSÃO COMPLETA
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CategoriaEquipamento, Equipamento, HistoricoHorimetro, FotoEquipamento

@admin.register(CategoriaEquipamento)
class CategoriaEquipamentoAdmin(admin.ModelAdmin):
    """Admin para categorias de equipamentos"""
    list_display = ('codigo', 'nome', 'prefixo_codigo', 'total_equipamentos', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome', 'descricao')
    ordering = ('codigo',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'nome', 'descricao', 'ativo')
        }),
        ('Configurações', {
            'fields': ('prefixo_codigo',),
            'description': 'Prefixo usado para gerar códigos automáticos dos equipamentos'
        }),
    )
    
    def total_equipamentos(self, obj):
        """Mostra total de equipamentos da categoria"""
        total = obj.equipamentos.count()
        if total > 0:
            url = reverse('admin:equipamentos_equipamento_changelist')
            return format_html(
                '<a href="{}?categoria__id__exact={}">{} equipamentos</a>',
                url, obj.id, total
            )
        return "0 equipamentos"
    total_equipamentos.short_description = 'Total de Equipamentos'


class FotoEquipamentoInline(admin.TabularInline):
    """Inline para fotos dos equipamentos"""
    model = FotoEquipamento
    extra = 1
    fields = ('foto', 'titulo', 'descricao', 'data_foto')
    readonly_fields = ('preview_foto',)
    
    def preview_foto(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;">',
                obj.foto.url
            )
        return "Sem foto"
    preview_foto.short_description = 'Preview'


class HistoricoHorimetroInline(admin.TabularInline):
    """Inline para histórico do horímetro"""
    model = HistoricoHorimetro
    extra = 0
    fields = ('horimetro_anterior', 'horimetro_novo', 'diferenca', 'observacao', 'created_at')
    readonly_fields = ('diferenca', 'created_at')
    ordering = ('-created_at',)


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    """Admin completo para equipamentos"""
    
    list_display = (
        'codigo', 'nome', 'categoria', 'cliente', 'status', 
        'ativo_nr12', 'proxima_manutencao', 'valor_atual',
        'foto_thumb'
    )
    list_filter = (
        'categoria', 'status', 'condicao', 'ativo_nr12', 
        'cliente', 'empreendimento', 'frequencia_checklist'
    )
    search_fields = (
        'codigo', 'nome', 'marca', 'modelo', 'numero_serie',
        'cliente__razao_social', 'empreendimento__nome'
    )
    ordering = ('codigo',)
    
    readonly_fields = (
        'uuid', 'codigo', 'created_at', 'updated_at', 
        'idade_anos', 'valor_depreciado', 'localizacao_completa',
        'preview_foto_principal'
    )
    
    autocomplete_fields = ('cliente', 'empreendimento', 'categoria')
    
    fieldsets = (
        ('Identificação', {
            'fields': (
                ('uuid', 'codigo'),
                ('nome', 'categoria'),
                'codigo_patrimonio',
                'descricao'
            )
        }),
        ('Especificações Técnicas', {
            'fields': (
                ('fabricante', 'marca'),
                ('modelo', 'numero_serie'),
                ('ano_fabricacao', 'capacidade'),
                'consumo_medio'
            )
        }),
        ('Localização', {
            'fields': (
                ('cliente', 'empreendimento'),
                ('setor', 'area'),
                'localizacao_detalhada',
                'coordenadas_gps',
                'localizacao_completa'
            )
        }),
        ('Status e Condição', {
            'fields': (
                ('status', 'condicao'),
                'criticidade',
                'ativo'
            )
        }),
        ('Dados Operacionais', {
            'fields': (
                'horimetro_atual',
                ('proxima_manutencao_preventiva', 'ultima_manutencao'),
                'intervalo_manutencao_horas'
            )
        }),
        ('Dados Financeiros', {
            'fields': (
                ('valor_aquisicao', 'data_aquisicao'),
                ('vida_util_anos', 'valor_residual'),
                ('idade_anos', 'valor_depreciado')
            ),
            'classes': ('collapse',)
        }),
        ('NR12 e Segurança', {
            'fields': (
                ('tipo_nr12', 'ativo_nr12'),
                'frequencia_checklist',
                'requires_operator_license'
            )
        }),
        ('Documentação', {
            'fields': (
                'foto_principal',
                'preview_foto_principal',
                ('manual_operacao', 'manual_manutencao'),
                'certificados'
            ),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes', 'observacoes_tecnicas'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': (
                'created_by',
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FotoEquipamentoInline, HistoricoHorimetroInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cliente', 'empreendimento', 'categoria', 'tipo_nr12'
        )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def proxima_manutencao(self, obj):
        """Status da próxima manutenção"""