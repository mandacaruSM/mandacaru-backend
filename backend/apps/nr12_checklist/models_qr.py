import os
import glob
from django.db import models
from django.conf import settings
from .qr_manager import QRCodeManager
from django.utils import timezone

class ChecklistQRMixin:
    """Mixin para adicionar funcionalidades de QR PNG aos checklists"""
    
    @property
    def qr_code_png_url(self):
        """URL do QR code PNG se existir"""
        qr_manager = QRCodeManager()
        filename = f"checklist_{self.uuid}_*_medium_*.png"
        
        pattern = os.path.join(qr_manager.qr_dir, 'checklists', filename)
        files = glob.glob(pattern)
        
        if files:
            # Retornar o mais recente
            latest_file = max(files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return f"{settings.MEDIA_URL}qr_codes/checklists/{filename}"
        
        return None
    
    def gerar_qr_png(self, tamanho='medium', incluir_logo=True):
        """Gera QR code PNG para este checklist"""
        qr_manager = QRCodeManager()
        return qr_manager.gerar_qr_checklist(self, tamanho, incluir_logo)
    
    def tem_qr_png(self):
        """Verifica se já existe QR code PNG"""
        return self.qr_code_png_url is not None


class EquipamentoQRMixin:
    """Mixin para adicionar funcionalidades de QR PNG aos equipamentos"""
    
    @property
    def qr_code_png_url(self):
        """URL do QR code PNG do equipamento"""
        filename = f"eq_{self.id}_medium.png"
        filepath = os.path.join(settings.MEDIA_ROOT, 'qr_codes', 'equipamentos', filename)
        
        if os.path.exists(filepath):
            return f"{settings.MEDIA_URL}qr_codes/equipamentos/{filename}"
        
        return None
    
    def gerar_qr_png(self, tamanho='medium'):
        """Gera QR code PNG para este equipamento"""
        qr_manager = QRCodeManager()
        return qr_manager.gerar_qr_equipamento(self, tamanho)
    
    def tem_qr_png(self):
        """Verifica se já existe QR code PNG"""
        return self.qr_code_png_url is not None

class CategoriaChecklistNR12(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoria de Checklist NR12'
        verbose_name_plural = 'Categorias de Checklist NR12'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.nome}'

class ChecklistNR12(models.Model):
    # ... campos existentes ...
    
    @property
    def total_itens(self):
        """Total de itens do checklist"""
        return self.itens.count()
    
    @property
    def itens_verificados(self):
        """Total de itens já verificados"""
        return self.itens.exclude(status='PENDENTE').count()
    
    @property
    def itens_ok(self):
        """Total de itens OK"""
        return self.itens.filter(status='OK').count()
    
    @property
    def itens_nok(self):
        """Total de itens NOK"""
        return self.itens.filter(status='NOK').count()
    
    @property
    def itens_na(self):
        """Total de itens N/A"""
        return self.itens.filter(status='NA').count()
    
    @property
    def percentual_conclusao(self):
        """Percentual de conclusão do checklist"""
        total = self.total_itens
        if total == 0:
            return 0
        return int((self.itens_verificados / total) * 100)
    
    @property
    def tem_problemas(self):
        """Verifica se há itens NOK"""
        return self.itens_nok > 0
    
    @property
    def duracao(self):
        """Duração do checklist em minutos"""
        if self.hora_inicio and self.hora_fim:
            delta = self.hora_fim - self.hora_inicio
            return int(delta.total_seconds() / 60)
        return None
    
    def get_resumo_para_bot(self):
        """Retorna resumo do checklist para o bot"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'equipamento': {
                'id': self.equipamento.id,
                'serie': self.equipamento.numero_serie,
                'modelo': self.equipamento.modelo,
            },
            'turno': self.get_turno_display(),
            'status': self.get_status_display(),
            'data': self.data_realizacao.strftime('%d/%m/%Y'),
            'progresso': {
                'percentual': self.percentual_conclusao,
                'verificados': self.itens_verificados,
                'total': self.total_itens,
            },
            'resultados': {
                'ok': self.itens_ok,
                'nok': self.itens_nok,
                'na': self.itens_na,
            },
            'tem_problemas': self.tem_problemas,
        }
    
    def get_proximo_item(self):
        """Retorna próximo item pendente"""
        return self.itens.filter(status='PENDENTE').order_by('item_padrao__ordem').first()
    
    def pode_ser_editado_por(self, user):
        """Verifica se o usuário pode editar o checklist"""
        if self.status == 'FINALIZADO':
            return False
        return self.responsavel == user or user.is_superuser


class ItemChecklistRealizado(models.Model):
    # ... campos existentes ...
    
    def get_info_para_bot(self):
        """Retorna informações do item para o bot"""
        return {
            'id': self.id,
            'ordem': self.ordem,
            'descricao': self.item_padrao.descricao,
            'categoria': self.item_padrao.categoria,
            'status': self.get_status_display(),
            'observacao': self.observacao,
            'permite_na': self.item_padrao.permite_na,
            'requer_obs_nok': self.item_padrao.requer_observacao_se_nok,
            'verificado_por': self.verificado_por.get_full_name() if self.verificado_por else None,
            'data_verificacao': self.data_verificacao.strftime('%d/%m/%Y %H:%M') if self.data_verificacao else None,
        }
    
    def marcar_como_verificado(self, status, user, observacao=''):
        """Marca item como verificado"""
        self.status = status
        self.verificado_por = user
        self.data_verificacao = timezone.now()
        self.observacao = observacao
        self.save()
        
        # Atualizar status do checklist se necessário
        if self.checklist.status == 'INICIADO':
            self.checklist.status = 'EM_ANDAMENTO'
            self.checklist.save()
