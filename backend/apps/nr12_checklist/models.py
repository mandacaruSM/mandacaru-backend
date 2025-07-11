# 1. ATUALIZAR backend/apps/nr12_checklist/models.py
# ================================================================

import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class TipoEquipamentoNR12(models.Model):
    """Tipos de equipamentos com checklists padrão da NR12"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Tipo de Equipamento NR12"
        verbose_name_plural = "Tipos de Equipamentos NR12"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class ItemChecklistPadrao(models.Model):
    """Itens padrão de checklist por tipo de equipamento"""
    CRITICIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica')
    ]

    tipo_equipamento = models.ForeignKey(
        TipoEquipamentoNR12, 
        on_delete=models.CASCADE, 
        related_name='itens_checklist',
        verbose_name="Tipo de Equipamento"
    )
    item = models.CharField(max_length=255, verbose_name="Item")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    criticidade = models.CharField(max_length=10, choices=CRITICIDADE_CHOICES, verbose_name="Criticidade")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        ordering = ['ordem', 'item']
        unique_together = ['tipo_equipamento', 'item']
        verbose_name = "Item de Checklist Padrão"
        verbose_name_plural = "Itens de Checklist Padrão"

    def __str__(self):
        return f"{self.tipo_equipamento.nome} - {self.item}"

class ChecklistNR12(models.Model):
    """Checklist diário realizado em um equipamento"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado')
    ]

    TURNO_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
        ('MADRUGADA', 'Madrugada')
    ]

    # UUID para QR Code
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    equipamento = models.ForeignKey(
        'equipamentos.Equipamento', 
        on_delete=models.CASCADE, 
        related_name='checklists_nr12',
        verbose_name="Equipamento"
    )
    data_checklist = models.DateField(verbose_name="Data do Checklist")
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, verbose_name="Turno")
    
    # Responsável
    responsavel = models.ForeignKey(
        'auth_cliente.UsuarioCliente', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='checklists_realizados',
        verbose_name="Responsável"
    )
    
    # Status e dados
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    horimetro_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Horímetro Inicial"
    )
    horimetro_final = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Horímetro Final"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    necessita_manutencao = models.BooleanField(default=False, verbose_name="Necessita Manutenção")
    
    # Controle temporal
    data_inicio = models.DateTimeField(null=True, blank=True, verbose_name="Data de Início")
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        unique_together = ['equipamento', 'data_checklist', 'turno']
        ordering = ['-data_checklist', '-created_at']
        verbose_name = "Checklist NR12"
        verbose_name_plural = "Checklists NR12"

    def __str__(self):
        return f"Checklist {self.equipamento.nome} - {self.data_checklist} - {self.turno}"

    @property
    def qr_code_url(self):
        """URL para acessar via QR Code"""
        return f"/checklist/{self.uuid}/"

    @property
    def percentual_conclusao(self):
        """Calcula percentual de conclusão"""
        total = self.itens.count()
        if total == 0:
            return 0
        concluidos = self.itens.exclude(status='PENDENTE').count()
        return round((concluidos / total) * 100, 1)

    def iniciar_checklist(self, usuario):
        """Inicia o checklist"""
        if self.status != 'PENDENTE':
            raise ValidationError("Checklist já foi iniciado.")
        
        self.status = 'EM_ANDAMENTO'
        self.responsavel = usuario
        self.data_inicio = timezone.now()
        self.save()

        # Criar itens baseados no tipo do equipamento
        if hasattr(self.equipamento, 'tipo_nr12') and self.equipamento.tipo_nr12:
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=self.equipamento.tipo_nr12,
                ativo=True
            ).order_by('ordem')
            
            for item_padrao in itens_padrao:
                ItemChecklistRealizado.objects.get_or_create(
                    checklist=self,
                    item_padrao=item_padrao,
                    defaults={'status': 'PENDENTE'}
                )

    def finalizar_checklist(self):
        """Finaliza o checklist"""
        if self.status != 'EM_ANDAMENTO':
            raise ValidationError("Checklist deve estar em andamento para ser finalizado.")
        
        # Verificar se todos os itens foram verificados
        itens_pendentes = self.itens.filter(status='PENDENTE').count()
        if itens_pendentes > 0:
            raise ValidationError(f"Ainda há {itens_pendentes} itens pendentes.")
        
        self.status = 'CONCLUIDO'
        self.data_conclusao = timezone.now()
        self.save()

        # Verificar se precisa gerar alertas
        self._gerar_alertas_se_necessario()

    def _gerar_alertas_se_necessario(self):
        """Gera alertas baseados em itens não conformes"""
        from datetime import date, timedelta
        
        itens_nok = self.itens.filter(status='NOK')
        for item in itens_nok:
            if item.item_padrao.criticidade in ['ALTA', 'CRITICA']:
                AlertaManutencao.objects.get_or_create(
                    equipamento=self.equipamento,
                    titulo=f"Item não conforme: {item.item_padrao.item}",
                    defaults={
                        'tipo': 'CORRETIVA',
                        'descricao': f"Item '{item.item_padrao.item}' marcado como não conforme no checklist.",
                        'criticidade': item.item_padrao.criticidade,
                        'data_prevista': date.today() + timedelta(days=3),
                        'checklist_origem': self
                    }
                )

class ItemChecklistRealizado(models.Model):
    """Item específico verificado em um checklist"""
    STATUS_CHOICES = [
        ('OK', 'Conforme'),
        ('NOK', 'Não Conforme'),
        ('NA', 'Não Aplicável'),
        ('PENDENTE', 'Pendente')
    ]

    checklist = models.ForeignKey(
        ChecklistNR12, 
        on_delete=models.CASCADE, 
        related_name='itens',
        verbose_name="Checklist"
    )
    item_padrao = models.ForeignKey(
        ItemChecklistPadrao, 
        on_delete=models.CASCADE,
        verbose_name="Item Padrão"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    observacao = models.TextField(blank=True, verbose_name="Observação")
    
    # Evidências fotográficas
    foto_antes = models.ImageField(
        upload_to='checklist/fotos/', null=True, blank=True,
        verbose_name="Foto Antes"
    )
    foto_depois = models.ImageField(
        upload_to='checklist/fotos/', null=True, blank=True,
        verbose_name="Foto Depois"
    )
    
    # Controle
    verificado_em = models.DateTimeField(null=True, blank=True, verbose_name="Verificado em")
    verificado_por = models.ForeignKey(
        'auth_cliente.UsuarioCliente', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        verbose_name="Verificado por"
    )

    class Meta:
        unique_together = ['checklist', 'item_padrao']
        verbose_name = "Item de Checklist Realizado"
        verbose_name_plural = "Itens de Checklist Realizados"
        ordering = ['item_padrao__ordem']

    def __str__(self):
        return f"{self.checklist} - {self.item_padrao.item} - {self.status}"

    def marcar_como_verificado(self, usuario, status, observacao=''):
        """Marca item como verificado"""
        self.status = status
        self.observacao = observacao
        self.verificado_em = timezone.now()
        self.verificado_por = usuario
        self.save()

class AlertaManutencao(models.Model):
    """Alertas de manutenção baseados em checklists"""
    TIPO_CHOICES = [
        ('PREVENTIVA', 'Manutenção Preventiva'),
        ('CORRETIVA', 'Manutenção Corretiva'),
        ('URGENTE', 'Manutenção Urgente')
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('NOTIFICADO', 'Notificado'),
        ('RESOLVIDO', 'Resolvido'),
        ('CANCELADO', 'Cancelado')
    ]

    equipamento = models.ForeignKey(
        'equipamentos.Equipamento', 
        on_delete=models.CASCADE, 
        related_name='alertas_manutencao',
        verbose_name="Equipamento"
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ATIVO', verbose_name="Status")
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    criticidade = models.CharField(
        max_length=10, 
        choices=ItemChecklistPadrao.CRITICIDADE_CHOICES,
        verbose_name="Criticidade"
    )
    
    # Datas importantes
    data_identificacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Identificação")
    data_prevista = models.DateField(verbose_name="Data Prevista")
    data_notificacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Notificação")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    
    # Origem
    checklist_origem = models.ForeignKey(
        ChecklistNR12, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        verbose_name="Checklist de Origem"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-data_prevista', '-criticidade']
        verbose_name = "Alerta de Manutenção"
        verbose_name_plural = "Alertas de Manutenção"

    def __str__(self):
        return f"{self.equipamento.nome} - {self.titulo}"

    @property
    def dias_restantes(self):
        """Calcula dias restantes até a data prevista"""
        from datetime import date
        return (self.data_prevista - date.today()).days

    @property
    def is_urgente(self):
        """Verifica se o alerta é urgente (3 dias ou menos)"""
        return self.dias_restantes <= 3

    def marcar_como_notificado(self):
        """Marca alerta como notificado"""
        self.status = 'NOTIFICADO'
        self.data_notificacao = timezone.now()
        self.save()

    def marcar_como_resolvido(self):
        """Marca alerta como resolvido"""
        self.status = 'RESOLVIDO'
        self.data_resolucao = timezone.now()
        self.save()
