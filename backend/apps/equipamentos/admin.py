from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from .models import Equipamento, CategoriaEquipamento

# Filtro customizado para ArrayField
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
            return queryset.filter(frequencias_checklist__contains=[self.value()])
        return queryset


# Formulário customizado para mostrar checkboxes no lugar de campo texto
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
    form = EquipamentoAdminForm  # ← aplica o form com checkboxes

    list_display = (
        'nome', 'categoria', 'marca', 'modelo', 'cliente', 'ativo_nr12', 'created_at',
        'qr_code_tag', 'link_pdf_qr'
    )
    list_filter = ('categoria', 'ativo_nr12', FrequenciaChecklistFilter, 'marca', 'cliente')
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
                'frequencias_checklist',
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

    def qr_code_tag(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="60" />', obj.qr_code.url)
        return "QR não gerado"
    qr_code_tag.short_description = "QR Code"

    def link_pdf_qr(self, obj):
        url = reverse('qr_code_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">📄 PDF</a>', url)
    link_pdf_qr.short_description = "QR PDF"


# Cabeçalhos personalizados
admin.site.site_header = "Mandacaru ERP - Gestão de Equipamentos"
admin.site.site_title = "Mandacaru ERP"
admin.site.index_title = "Painel Administrativo"
