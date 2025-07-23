# backend/apps/operadores/admin.py - VERSÃO CORRIGIDA

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
            'fields': ('qr_code_data_display', 'qr_code_preview', 'gerar_qr_button'),
            'classes': ('collapse',)
        })
    )
    
    # ✅ CORRIGIDO: Remover campos que não existem
    readonly_fields = [
        'codigo', 'qr_code_data_display', 'qr_code_preview', 'gerar_qr_button',
        'ultimo_acesso_bot', 'chat_id_telegram'
    ]
    
    # ✅ AÇÕES PERSONALIZADAS
    actions = ['gerar_qr_codes_acao', 'atualizar_chat_ids']

    def qr_code_preview(self, obj):
        """Mostra preview do QR code"""
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="100" height="100" style="border: 1px solid #ccc;" />',
                obj.qr_code.url
            )
        return "QR Code não gerado"
    qr_code_preview.short_description = "QR Code"
    
    def qr_code_data_display(self, obj):
        """Mostra dados do QR code de forma legível"""
        if obj.qr_code_data:
            return format_html(
                '<code style="background: #f5f5f5; padding: 5px; border-radius: 3px;">{}</code>',
                obj.qr_code_data
            )
        return "Não gerado"
    qr_code_data_display.short_description = "Dados do QR Code"
    
    def gerar_qr_button(self, obj):
        """Botão para gerar QR code"""
        if obj.pk:
            return format_html(
                '<a class="button" href="javascript:void(0)" onclick="gerarQRCode({})">🔲 Gerar QR Code</a>',
                obj.pk
            )
        return "Salve primeiro"
    gerar_qr_button.short_description = "Ações"
    
    def gerar_qr_codes_acao(self, request, queryset):
        """Ação para gerar QR codes em lote"""
        gerados = 0
        erros = 0
        
        for operador in queryset:
            try:
                operador.gerar_qr_code()
                gerados += 1
            except Exception as e:
                erros += 1
                self.message_user(
                    request, 
                    f"Erro ao gerar QR para {operador.codigo}: {e}", 
                    level='ERROR'
                )
        
        if gerados > 0:
            self.message_user(
                request,
                f"✅ {gerados} QR codes gerados com sucesso!"
            )
        
        if erros > 0:
            self.message_user(
                request,
                f"❌ {erros} erros encontrados",
                level='WARNING'
            )
    
    gerar_qr_codes_acao.short_description = "🔲 Gerar QR codes selecionados"
    
    def atualizar_chat_ids(self, request, queryset):
        """Ação para limpar chat IDs inválidos"""
        atualizados = queryset.filter(chat_id_telegram__isnull=False).update(chat_id_telegram=None)
        self.message_user(
            request,
            f"✅ {atualizados} chat IDs limpos. Operadores precisarão fazer login novamente no bot."
        )
    
    atualizar_chat_ids.short_description = "🔄 Limpar Chat IDs (requer novo login no bot)"
    
    class Media:
        js = ('admin/js/operador_admin.js',)  # Para funcionalidades JavaScript personalizadas