# ================================================================
# ADMIN EQUIPAMENTO CORRIGIDO
# backend/apps/equipamentos/admin.py
# ================================================================

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from .models import Equipamento, CategoriaEquipamento

# ✅ FILTRO CORRIGIDO para ArrayField
class FrequenciaChecklistFilter(admin.SimpleListFilter):
    title = 'Frequência NR12'
    parameter_name = 'frequencias_checklist'

    def lookups(self, request, model_admin):
        return [
            ('DIARIA', 'Diária'),
            ('SEMANAL', 'Semanal'),
            ('MENSAL', 'Mensal'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            # ✅ CORRIGIDO: Usar __contains para ArrayField
            return queryset.filter(frequencias_checklist__contains=[self.value()])
        return queryset


# ✅ FORMULÁRIO CORRIGIDO para mostrar checkboxes
class EquipamentoAdminForm(forms.ModelForm):
    FREQUENCIA_CHOICES = [
        ('DIARIA', 'Diária'),
        ('SEMANAL', 'Semanal'),
        ('MENSAL', 'Mensal'),
    ]

    frequencias_checklist = forms.MultipleChoiceField(
        choices=FREQUENCIA_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Frequência(s) do Checklist NR12"
    )

    class Meta:
        model = Equipamento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Inicializar valor do campo para exibição correta
        if self.instance and self.instance.pk:
            self.fields['frequencias_checklist'].initial = self.instance.frequencias_checklist or []


@admin.register(CategoriaEquipamento)
class CategoriaEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'prefixo_codigo', 'total_equipamentos', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome', 'descricao')
    ordering = ('codigo',)

    def total_equipamentos(self, obj):
        return obj.equipamentos.count()
    total_equipamentos.short_description = 'Total de Equipamentos'


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    form = EquipamentoAdminForm  # ✅ Aplicar form com checkboxes

    list_display = (
        'codigo_display', 'nome', 'categoria', 'marca', 'modelo', 'cliente', 
        'status_operacional', 'ativo_nr12', 'frequencias_display', 'created_at',
        'qr_code_tag', 'link_pdf_qr'
    )
    
    list_filter = (
        'categoria', 'ativo_nr12', FrequenciaChecklistFilter, 'marca', 'cliente',
        'status', 'status_operacional'
    )
    
    search_fields = ('nome', 'marca', 'modelo', 'n_serie')
    ordering = ('categoria', 'nome')
    readonly_fields = ('created_at', 'updated_at', 'codigo_display')

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
                ('horimetro', 'horimetro_atual')
            )
        }),
        ('Status e Operação', {
            'fields': (
                ('status', 'status_operacional'),
                ('ativo', 'ativo_nr12'),
                ('operador_atual', 'data_inicio_uso'),
                'localizacao_atual'
            )
        }),
        ('Localização', {
            'fields': (
                ('cliente', 'empreendimento'),
            )
        }),
        ('NR12 e Segurança', {
            'fields': (
                'tipo_nr12',
                'frequencias_checklist',  # ✅ Campo corrigido
                'proxima_manutencao_preventiva'
            )
        }),
        ('Restrições de Acesso', {
            'fields': (
                'requer_cnh',
                'categoria_cnh_necessaria', 
                'nivel_experiencia_minimo'
            ),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': (
                'codigo_display',
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'categoria', 'cliente', 'empreendimento', 'tipo_nr12', 'operador_atual'
        )

    def codigo_display(self, obj):
        """Exibe o código gerado automaticamente"""
        return obj.codigo
    codigo_display.short_description = "Código"

    def frequencias_display(self, obj):
        """Exibe frequências de forma legível"""
        if obj.frequencias_checklist:
            freq_map = {
                'DIARIA': 'D',
                'SEMANAL': 'S', 
                'MENSAL': 'M'
            }
            return ', '.join([freq_map.get(f, f) for f in obj.frequencias_checklist])
        return '-'
    frequencias_display.short_description = "Frequências"

    def qr_code_tag(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="60" style="border: 1px solid #ccc;" />',
                obj.qr_code.url
            )
        return "QR não gerado"
    qr_code_tag.short_description = "QR Code"

    def link_pdf_qr(self, obj):
        url = reverse('qr_code_pdf', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" target="_blank">📄 PDF</a>',
            url
        )
    link_pdf_qr.short_description = "QR PDF"

    # ✅ AÇÕES DO ADMIN
    actions = ['gerar_qr_codes', 'ativar_nr12', 'desativar_nr12']

    def gerar_qr_codes(self, request, queryset):
        """Ação para gerar QR codes dos equipamentos selecionados"""
        gerados = 0
        for equipamento in queryset:
            try:
                equipamento.gerar_qr_png()
                gerados += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Erro ao gerar QR para {equipamento.nome}: {str(e)}",
                    level='ERROR'
                )
        
        if gerados > 0:
            self.message_user(
                request,
                f"✅ {gerados} QR code(s) gerado(s) com sucesso!"
            )
    gerar_qr_codes.short_description = "🔗 Gerar QR Codes"

    def ativar_nr12(self, request, queryset):
        """Ativa NR12 para equipamentos selecionados"""
        updated = queryset.update(ativo_nr12=True)
        self.message_user(
            request,
            f"✅ {updated} equipamento(s) ativado(s) para NR12"
        )
    ativar_nr12.short_description = "✅ Ativar NR12"

    def desativar_nr12(self, request, queryset):
        """Desativa NR12 para equipamentos selecionados"""
        updated = queryset.update(ativo_nr12=False)
        self.message_user(
            request,
            f"❌ {updated} equipamento(s) desativado(s) para NR12"
        )
    desativar_nr12.short_description = "❌ Desativar NR12"


# Cabeçalhos personalizados
admin.site.site_header = "Mandacaru ERP - Gestão de Equipamentos"
admin.site.site_title = "Mandacaru ERP"
admin.site.index_title = "Painel Administrativo"