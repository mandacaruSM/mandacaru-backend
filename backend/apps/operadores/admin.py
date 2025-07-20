# backend/apps/operadores/admin.py - ATUALIZADO
from django.contrib import admin
from django.utils.html import format_html
from .models import Operador

@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nome', 'funcao', 'setor', 'status', 
        'ativo_bot', 'ultimo_acesso_bot', 'qr_code_preview'
    ]
    list_filter = [
        'status', 'setor', 'funcao', 'ativo_bot', 
        'pode_fazer_checklist', 'pode_registrar_abastecimento'
    ]
    search_fields = ['codigo', 'nome', 'cpf', 'telefone', 'email']
    
    filter_horizontal = [
        'clientes_autorizados',
        'empreendimentos_autorizados', 
        'equipamentos_autorizados'
    ]
    
    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'nome', 'cpf', 'rg', 'data_nascimento')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'endereco', 'cidade', 'estado', 'cep')
        }),
        ('Dados Profissionais', {
            'fields': (
                'funcao', 'setor', 'data_admissao', 'data_demissao', 
                'salario', 'supervisor'
            )
        }),
        ('Vínculos de Trabalho', {
            'fields': (
                'clientes_autorizados',
                'empreendimentos_autorizados',
                'equipamentos_autorizados'
            ),
            'classes': ('collapse',)
        }),
        ('Permissões do Sistema', {
            'fields': (
                'pode_fazer_checklist',
                'pode_registrar_abastecimento', 
                'pode_reportar_anomalia',
                'pode_ver_relatorios'
            )
        }),
        ('Bot Telegram', {
            'fields': (
                'ativo_bot', 'chat_id_telegram', 'ultimo_acesso_bot'
            ),
            'classes': ('collapse',)
        }),
        ('Localização e Uso', {
            'fields': (
                'localizacao_atual', 'ultimo_equipamento_usado'
            ),
            'classes': ('collapse',)
        }),
        ('Documentos', {
            'fields': (
                'tipo_documento', 'numero_documento', 
                'cnh_numero', 'cnh_categoria', 'cnh_vencimento'
            ),
            'classes': ('collapse',)
        }),
        ('Status e Controle', {
            'fields': ('status', 'observacoes', 'user')
        }),
        ('QR Code', {
            'fields': ('qr_code_data', 'qr_code_preview'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'codigo', 'qr_code_data', 'qr_code_preview', 
        'ultimo_acesso_bot', 'chat_id_telegram'
    ]

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="100" height="100" style="border: 1px solid #ccc;" />',
                obj.qr_code.url
            )
        return "QR Code não gerado"
    qr_code_preview.short_description = "QR Code"

