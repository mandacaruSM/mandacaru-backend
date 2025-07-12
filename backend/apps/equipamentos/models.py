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
        if obj.proxima_manutencao_preventiva:
            dias = obj.dias_proxima_manutencao
            if dias < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">🚨 Atrasado {} dias</span>',
                    abs(dias)
                )
            elif dias <= 7:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠️ {} dias</span>',
                    dias
                )
            else:
                return format_html(
                    '<span style="color: green;">✅ {} dias</span>',
                    dias
                )
        return "Não agendada"
    proxima_manutencao.short_description = 'Próxima Manutenção'
    
    def valor_atual(self, obj):
        """Valor atual do equipamento"""
        if obj.valor_depreciado:
            return format_html(
                'R$ {:,.2f}',
                obj.valor_depreciado
            )
        elif obj.valor_aquisicao:
            return format_html(
                'R$ {:,.2f} <small>(aquisição)</small>',
                obj.valor_aquisicao
            )
        return "Não informado"
    valor_atual.short_description = 'Valor Atual'
    
    def foto_thumb(self, obj):
        """Thumbnail da foto principal"""
        if obj.foto_principal:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 80px; border-radius: 4px;">',
                obj.foto_principal.url
            )
        return "📷"
    foto_thumb.short_description = 'Foto'
    
    def preview_foto_principal(self, obj):
        """Preview da foto principal"""
        if obj.foto_principal:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px;">',
                obj.foto_principal.url
            )
        return "Nenhuma foto principal"
    preview_foto_principal.short_description = 'Preview da Foto'
    
    actions = ['marcar_manutencao', 'ativar_nr12', 'desativar_nr12']
    
    def marcar_manutencao(self, request, queryset):
        """Marca equipamentos para manutenção"""
        count = queryset.update(status='MANUTENCAO')
        self.message_user(
            request,
            f'{count} equipamento(s) marcado(s) para manutenção.'
        )
    marcar_manutencao.short_description = 'Marcar para manutenção'
    
    def ativar_nr12(self, request, queryset):
        """Ativar NR12 para equipamentos"""
        count = queryset.update(ativo_nr12=True)
        self.message_user(
            request,
            f'NR12 ativado para {count} equipamento(s).'
        )
    ativar_nr12.short_description = 'Ativar NR12'
    
    def desativar_nr12(self, request, queryset):
        """Desativar NR12 para equipamentos"""
        count = queryset.update(ativo_nr12=False)
        self.message_user(
            request,
            f'NR12 desativado para {count} equipamento(s).'
        )
    desativar_nr12.short_description = 'Desativar NR12'


@admin.register(HistoricoHorimetro)
class HistoricoHorimetroAdmin(admin.ModelAdmin):
    """Admin para histórico do horímetro"""
    list_display = (
        'equipamento', 'horimetro_anterior', 'horimetro_novo', 
        'diferenca_horas', 'created_at'
    )
    list_filter = ('created_at', 'equipamento__categoria')
    search_fields = ('equipamento__codigo', 'equipamento__nome')
    readonly_fields = ('diferenca', 'created_at', 'created_by')
    ordering = ('-created_at',)
    
    def diferenca_horas(self, obj):
        """Formatação da diferença em horas"""
        return f"+{obj.diferenca}h"
    diferenca_horas.short_description = 'Diferença'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('equipamento')


@admin.register(FotoEquipamento)
class FotoEquipamentoAdmin(admin.ModelAdmin):
    """Admin para fotos dos equipamentos"""
    list_display = ('equipamento', 'titulo', 'data_foto', 'preview_mini')
    list_filter = ('data_foto', 'equipamento__categoria')
    search_fields = ('equipamento__codigo', 'equipamento__nome', 'titulo')
    ordering = ('-data_foto',)
    
    def preview_mini(self, obj):
        """Preview mini da foto"""
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 80px; border-radius: 4px;">',
                obj.foto.url
            )
        return "Sem foto"
    preview_mini.short_description = 'Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('equipamento')


# ================================================================
# CUSTOMIZAÇÕES DO ADMIN
# ================================================================

# Personalizar título do admin
admin.site.site_header = "ERP Mandacaru - Equipamentos"
admin.site.site_title = "Mandacaru ERP"
admin.site.index_title = "Gestão de Equipamentos"

# Registrar automaticamente as categorias na primeira vez
from django.contrib.admin.sites import AdminSite
from django.core.management.commands.migrate import Command as MigrateCommand

class EquipamentosAdminSite(AdminSite):
    """Site admin customizado para equipamentos"""
    
    def ready(self):
        """Executado quando o admin está pronto"""
        super().ready()
        # Criar categorias automaticamente se não existirem
        if CategoriaEquipamento.objects.count() == 0:
            from .models import criar_categorias_mandacaru
            criar_categorias_mandacaru()
            print("✅ Categorias Mandacaru criadas automaticamente!")


# ================================================================
# FILTROS CUSTOMIZADOS
# ================================================================

class StatusManutencaoFilter(admin.SimpleListFilter):
    """Filtro customizado para status de manutenção"""
    title = 'Status de Manutenção'
    parameter_name = 'manutencao_status'
    
    def lookups(self, request, model_admin):
        return (
            ('precisa', 'Precisa de manutenção'),
            ('em_dia', 'Em dia'),
            ('atrasada', 'Manutenção atrasada'),
        )
    
    def queryset(self, request, queryset):
        from datetime import date
        
        if self.value() == 'precisa':
            return queryset.filter(
                proxima_manutencao_preventiva__lte=date.today()
            )
        elif self.value() == 'em_dia':
            return queryset.filter(
                proxima_manutencao_preventiva__gt=date.today()
            )
        elif self.value() == 'atrasada':
            return queryset.filter(
                proxima_manutencao_preventiva__lt=date.today()
            )
        return queryset


class ChecklistPendenteFilter(admin.SimpleListFilter):
    """Filtro para equipamentos com checklist pendente"""
    title = 'Checklist Hoje'
    parameter_name = 'checklist_hoje'
    
    def lookups(self, request, model_admin):
        return (
            ('pendente', 'Pendente hoje'),
            ('concluido', 'Concluído hoje'),
            ('sem_checklist', 'Sem checklist'),
        )
    
    def queryset(self, request, queryset):
        from datetime import date
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        hoje = date.today()
        
        if self.value() == 'pendente':
            equipamentos_com_pendente = ChecklistNR12.objects.filter(
                data_checklist=hoje,
                status='PENDENTE'
            ).values_list('equipamento_id', flat=True)
            return queryset.filter(id__in=equipamentos_com_pendente)
            
        elif self.value() == 'concluido':
            equipamentos_concluidos = ChecklistNR12.objects.filter(
                data_checklist=hoje,
                status='CONCLUIDO'
            ).values_list('equipamento_id', flat=True)
            return queryset.filter(id__in=equipamentos_concluidos)
            
        elif self.value() == 'sem_checklist':
            equipamentos_com_checklist = ChecklistNR12.objects.filter(
                data_checklist=hoje
            ).values_list('equipamento_id', flat=True)
            return queryset.exclude(id__in=equipamentos_com_checklist)
            
        return queryset


# Adicionar os filtros customizados ao EquipamentoAdmin
EquipamentoAdmin.list_filter = EquipamentoAdmin.list_filter + (
    StatusManutencaoFilter,
    ChecklistPendenteFilter,
)