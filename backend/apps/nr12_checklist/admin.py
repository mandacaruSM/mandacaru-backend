from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from .models import (
    TipoEquipamentoNR12, 
    ItemChecklistPadrao, 
    ChecklistNR12, 
    ItemChecklistRealizado, 
    AlertaManutencao
)

@admin.register(TipoEquipamentoNR12)
class TipoEquipamentoNR12Admin(admin.ModelAdmin):
    list_display = ['nome', 'total_itens', 'created_at']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['created_at']
    
    def total_itens(self, obj):
        count = obj.itens_checklist.count()
        return format_html(
            '<span style="color: {};">{} itens</span>',
            'green' if count > 0 else 'red',
            count
        )
    total_itens.short_description = 'Total de Itens'

@admin.register(ItemChecklistPadrao)
class ItemChecklistPadraoAdmin(admin.ModelAdmin):
    list_display = ['item', 'tipo_equipamento', 'criticidade', 'ordem', 'ativo']
    list_filter = ['tipo_equipamento', 'criticidade', 'ativo']
    search_fields = ['item', 'descricao']
    list_editable = ['ordem', 'ativo']
    ordering = ['tipo_equipamento', 'ordem']

@admin.register(ChecklistNR12)
class ChecklistNR12Admin(admin.ModelAdmin):
    list_display = ['equipamento', 'data_checklist', 'turno', 'status_colorido', 'responsavel', 'total_itens']
    list_filter = ['status', 'turno', 'data_checklist', 'necessita_manutencao']
    search_fields = ['equipamento__nome', 'observacoes']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    date_hierarchy = 'data_checklist'
    
    # TODAS AS AÇÕES INCLUINDO QR CODES
    actions = [
        'iniciar_checklists', 
        'finalizar_checklists', 
        'cancelar_checklists', 
        'gerar_qr_codes_acao'
    ]
    
    def status_colorido(self, obj):
        cores = {
            'PENDENTE': '#ffc107',     # Amarelo
            'EM_ANDAMENTO': '#17a2b8', # Azul
            'CONCLUIDO': '#28a745',    # Verde
            'CANCELADO': '#dc3545'     # Vermelho
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            cores.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_colorido.short_description = 'Status'
    
    def total_itens(self, obj):
        total = obj.itens.count()
        if total > 0:
            concluidos = obj.itens.exclude(status='PENDENTE').count()
            return format_html('<span>{}/{}</span>', concluidos, total)
        return "0"
    total_itens.short_description = 'Itens (Feitos/Total)'
    
    # AÇÃO 1: Iniciar Checklists
    def iniciar_checklists(self, request, queryset):
        iniciados = 0
        erros = []
        
        for checklist in queryset:
            if checklist.status == 'PENDENTE':
                try:
                    checklist.status = 'EM_ANDAMENTO'
                    checklist.data_inicio = timezone.now()
                    checklist.responsavel = request.user
                    checklist.save()
                    
                    # Criar itens baseados no tipo (se existir)
                    if hasattr(checklist.equipamento, 'tipo_nr12') and checklist.equipamento.tipo_nr12:
                        self._criar_itens_checklist(checklist)
                    
                    iniciados += 1
                except Exception as e:
                    erros.append(f"Erro no checklist {checklist.id}: {str(e)}")
            else:
                erros.append(f"Checklist {checklist.id} já foi iniciado")
        
        if iniciados > 0:
            messages.success(request, f"✅ {iniciados} checklist(s) iniciado(s) com sucesso!")
        
        if erros:
            for erro in erros[:5]:
                messages.warning(request, f"⚠️ {erro}")
    
    iniciar_checklists.short_description = "🚀 Iniciar checklists selecionados"
    
    # AÇÃO 2: Finalizar Checklists
    def finalizar_checklists(self, request, queryset):
        finalizados = 0
        erros = []
        
        for checklist in queryset:
            if checklist.status == 'EM_ANDAMENTO':
                try:
                    checklist.status = 'CONCLUIDO'
                    checklist.data_conclusao = timezone.now()
                    
                    # Verificar se há problemas
                    itens_nok = checklist.itens.filter(status='NOK').count()
                    checklist.necessita_manutencao = itens_nok > 0
                    
                    checklist.save()
                    finalizados += 1
                except Exception as e:
                    erros.append(f"Erro no checklist {checklist.id}: {str(e)}")
            else:
                erros.append(f"Checklist {checklist.id} não está em andamento")
        
        if finalizados > 0:
            messages.success(request, f"✅ {finalizados} checklist(s) finalizado(s)!")
        
        if erros:
            for erro in erros[:3]:
                messages.warning(request, f"⚠️ {erro}")
    
    finalizar_checklists.short_description = "✅ Finalizar checklists selecionados"
    
    # AÇÃO 3: Cancelar Checklists
    def cancelar_checklists(self, request, queryset):
        cancelados = queryset.filter(status__in=['PENDENTE', 'EM_ANDAMENTO']).update(
            status='CANCELADO'
        )
        
        if cancelados > 0:
            messages.success(request, f"❌ {cancelados} checklist(s) cancelado(s)!")
        else:
            messages.warning(request, "⚠️ Nenhum checklist pode ser cancelado")
    
    cancelar_checklists.short_description = "❌ Cancelar checklists selecionados"
    
    # AÇÃO 4: Gerar QR Codes
    def gerar_qr_codes_acao(self, request, queryset):
        """Ação para gerar QR codes dos checklists selecionados"""
        
        try:
            from .qr_generator import gerar_qr_code_base64
        except ImportError:
            messages.error(request, "❌ Arquivo qr_generator.py não encontrado!")
            return
        
        gerados = 0
        erros = []
        urls_geradas = []
        
        for checklist in queryset:
            try:
                qr_data = gerar_qr_code_base64(checklist)
                gerados += 1
                urls_geradas.append(qr_data['url'])
            except Exception as e:
                erros.append(f"Checklist {checklist.id}: {str(e)}")
        
        # Mensagens de resultado
        if gerados > 0:
            messages.success(request, f"🔗 {gerados} QR Code(s) gerado(s) com sucesso!")
            
            # Mostrar algumas URLs geradas
            if urls_geradas:
                urls_sample = urls_geradas[:3]  # Mostrar máximo 3 URLs
                for url in urls_sample:
                    messages.info(request, f"📱 URL: {url}")
        
        if erros:
            for erro in erros[:3]:  # Mostrar máximo 3 erros
                messages.warning(request, f"❌ {erro}")
    
    gerar_qr_codes_acao.short_description = "🔗 Gerar QR Codes"
    
    def _criar_itens_checklist(self, checklist):
        """Cria itens do checklist baseado no tipo do equipamento"""
        try:
            if hasattr(checklist.equipamento, 'tipo_nr12') and checklist.equipamento.tipo_nr12:
                itens_padrao = checklist.equipamento.tipo_nr12.itens_checklist.filter(ativo=True)
                
                for item_padrao in itens_padrao:
                    ItemChecklistRealizado.objects.get_or_create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        defaults={'status': 'PENDENTE'}
                    )
        except Exception:
            pass

@admin.register(ItemChecklistRealizado)
class ItemChecklistRealizadoAdmin(admin.ModelAdmin):
    list_display = ['checklist', 'item_padrao', 'status', 'status_colorido', 'verificado_por', 'verificado_em']
    list_filter = ['status', 'verificado_em']
    search_fields = ['checklist__equipamento__nome', 'item_padrao__item']
    list_editable = ['status']
    
    actions = ['marcar_como_ok', 'marcar_como_nok', 'marcar_como_na']
    
    def status_colorido(self, obj):
        cores = {
            'OK': '#28a745',      # Verde
            'NOK': '#dc3545',     # Vermelho
            'NA': '#6c757d',      # Cinza
            'PENDENTE': '#ffc107' # Amarelo
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            cores.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_colorido.short_description = 'Status'
    
    def marcar_como_ok(self, request, queryset):
        updated = queryset.update(
            status='OK',
            verificado_em=timezone.now(),
            verificado_por=request.user
        )
        messages.success(request, f"✅ {updated} item(s) marcado(s) como OK!")
    marcar_como_ok.short_description = "✅ Marcar como OK (Conforme)"
    
    def marcar_como_nok(self, request, queryset):
        updated = queryset.update(
            status='NOK',
            verificado_em=timezone.now(),
            verificado_por=request.user
        )
        messages.warning(request, f"❌ {updated} item(s) marcado(s) como NÃO CONFORME!")
    marcar_como_nok.short_description = "❌ Marcar como NOK (Não Conforme)"
    
    def marcar_como_na(self, request, queryset):
        updated = queryset.update(
            status='NA',
            verificado_em=timezone.now(),
            verificado_por=request.user
        )
        messages.info(request, f"➖ {updated} item(s) marcado(s) como N/A!")
    marcar_como_na.short_description = "➖ Marcar como N/A (Não Aplicável)"

@admin.register(AlertaManutencao)
class AlertaManutencaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'equipamento', 'tipo', 'criticidade', 'data_prevista', 'status']
    list_filter = ['tipo', 'status', 'criticidade', 'data_prevista']
    search_fields = ['titulo', 'descricao', 'equipamento__nome']
    readonly_fields = ['data_identificacao', 'created_at', 'updated_at']
    date_hierarchy = 'data_prevista'
    
    actions = ['marcar_como_notificado', 'marcar_como_resolvido']
    
    def marcar_como_notificado(self, request, queryset):
        updated = queryset.filter(status='ATIVO').update(
            status='NOTIFICADO',
            data_notificacao=timezone.now()
        )
        messages.success(request, f"📢 {updated} alerta(s) marcado(s) como notificado!")
    marcar_como_notificado.short_description = "📢 Marcar como notificado"
    
    def marcar_como_resolvido(self, request, queryset):
        updated = queryset.filter(status__in=['ATIVO', 'NOTIFICADO']).update(
            status='RESOLVIDO',
            data_resolucao=timezone.now()
        )
        messages.success(request, f"✅ {updated} alerta(s) marcado(s) como resolvido!")
    marcar_como_resolvido.short_description = "✅ Marcar como resolvido"