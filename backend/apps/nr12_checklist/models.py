# ================================================================
# CORRIGIR backend/apps/nr12_checklist/models.py
# ================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import uuid

User = get_user_model()


class TipoEquipamentoNR12(models.Model):
    """Tipos de equipamentos para categorização NR12"""
    
    nome = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nome"
    )
    descricao = models.TextField(
        blank=True, 
        verbose_name="Descrição"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Criado em"
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        default='Geral',
        verbose_name="Categoria"
    )
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Tipo de Equipamento NR12'
        verbose_name_plural = 'Tipos de Equipamentos NR12'
    
    def __str__(self):
        return self.nome


class FrequenciaChecklist(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Frequência de Checklist"
        verbose_name_plural = "Frequências de Checklists"
        ordering = ['codigo']

    def __str__(self):
        return self.nome


class ItemChecklistPadrao(models.Model):
    """Itens padrão de checklist por tipo de equipamento"""
    
    CRITICIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    tipo_equipamento = models.ForeignKey(
        TipoEquipamentoNR12,
        on_delete=models.CASCADE,
        related_name='itens_checklist',
        verbose_name="Tipo de Equipamento"
    )
    item = models.CharField(
        max_length=255, 
        verbose_name="Item"
    )
    descricao = models.TextField(
        blank=True, 
        verbose_name="Descrição"
    )
    criticidade = models.CharField(
        max_length=10, 
        choices=CRITICIDADE_CHOICES, 
        verbose_name="Criticidade"
    )
    ordem = models.PositiveIntegerField(
        default=0, 
        verbose_name="Ordem"
    )
    ativo = models.BooleanField(
        default=True, 
        verbose_name="Ativo"
    )
    
    class Meta:
        ordering = ['ordem', 'item']
        unique_together = [['tipo_equipamento', 'item']]
        verbose_name = 'Item de Checklist Padrão'
        verbose_name_plural = 'Itens de Checklist Padrão'
    
    def __str__(self):
        return f"{self.tipo_equipamento.nome} - {self.item}"


class ChecklistNR12(models.Model):
    """Checklist NR12 para equipamentos"""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TURNO_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
        ('MADRUGADA', 'Madrugada'),
    ]
    
    frequencia = models.CharField(
        max_length=10,
        choices=[('DIARIA', 'Diária'), ('SEMANAL', 'Semanal'), ('MENSAL', 'Mensal')],
        default='DIARIA',
        verbose_name='Frequência do Checklist'
    )

    # Identificação
    uuid = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )
    equipamento = models.ForeignKey(
        'equipamentos.Equipamento',
        on_delete=models.CASCADE,
        related_name='checklists_nr12',
        verbose_name="Equipamento"
    )
    
    # Data e turno
    data_checklist = models.DateField(
        verbose_name="Data do Checklist"
    )
    turno = models.CharField(
        max_length=20, 
        choices=TURNO_CHOICES, 
        verbose_name="Turno"
    )
    
    # Status e responsável
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='PENDENTE',
        verbose_name="Status"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='checklists_realizados',
        verbose_name="Responsável"
    )
    
    # Dados operacionais
    horimetro_inicial = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Horímetro Inicial"
    )
    horimetro_final = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Horímetro Final"
    )
    
    # Observações e resultados
    observacoes = models.TextField(
        blank=True, 
        verbose_name="Observações"
    )
    necessita_manutencao = models.BooleanField(
        default=False, 
        verbose_name="Necessita Manutenção"
    )
    
    # Controle de tempo
    data_inicio = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data de Início"
    )
    data_conclusao = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data de Conclusão"
    )
    
    # Auditoria
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Atualizado em"
    )
    
    class Meta:
        ordering = ['-data_checklist', '-created_at']
        unique_together = [['equipamento', 'data_checklist', 'turno']]
        verbose_name = 'Checklist NR12'
        verbose_name_plural = 'Checklists NR12'
    
    def __str__(self):
        return f"{self.equipamento.nome} - {self.data_checklist} - {self.turno}"
    
    @property
    def qr_code_url(self):
        """URL para acesso via QR Code"""
        return f"/api/bot-telegram/qr/{self.uuid}/"
    
    @property
    def percentual_conclusao(self):
        """Percentual de conclusão do checklist"""
        total_itens = self.itens.count()
        if total_itens == 0:
            return 0
        
        itens_concluidos = self.itens.exclude(status='PENDENTE').count()
        return round((itens_concluidos / total_itens) * 100, 1)
    
    def iniciar_checklist(self, usuario=None):
        """Inicia o checklist e cria os itens baseados no padrão"""
        if self.status != 'PENDENTE':
            raise ValueError("Checklist já foi iniciado ou finalizado")
        
        # Atualizar status
        self.status = 'EM_ANDAMENTO'
        self.data_inicio = timezone.now()
        if usuario:
            self.responsavel = usuario
        self.save()
        
        # Criar itens baseados no tipo NR12 do equipamento
        if self.equipamento.tipo_nr12:
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
        if self.status not in ['EM_ANDAMENTO', 'PENDENTE']:
            raise ValueError("Checklist não pode ser finalizado")
        
        # Verificar se há itens não conformes
        itens_nok = self.itens.filter(status='NOK').count()
        self.necessita_manutencao = itens_nok > 0
        
        # Atualizar status
        self.status = 'CONCLUIDO'
        self.data_conclusao = timezone.now()
        self.save()
        
        # Criar alertas para itens críticos não conformes
        self._criar_alertas_manutencao()
    
    def _criar_alertas_manutencao(self):
        """Cria alertas de manutenção para itens não conformes críticos"""
        itens_criticos_nok = self.itens.filter(
            status='NOK',
            item_padrao__criticidade__in=['ALTA', 'CRITICA']
        )
        
        for item in itens_criticos_nok:
            AlertaManutencao.objects.get_or_create(
                equipamento=self.equipamento,
                checklist_origem=self,
                titulo=f"Item não conforme: {item.item_padrao.item}",
                defaults={
                    'tipo': 'CORRETIVA',
                    'descricao': f"Item '{item.item_padrao.item}' marcado como não conforme no checklist de {self.data_checklist}.",
                    'criticidade': item.item_padrao.criticidade,
                    'data_prevista': date.today() + timedelta(days=1),
                }
            )


class ItemChecklistRealizado(models.Model):
    """Itens realizados de um checklist específico"""
    
    STATUS_CHOICES = [
        ('OK', 'Conforme'),
        ('NOK', 'Não Conforme'),
        ('NA', 'Não Aplicável'),
        ('PENDENTE', 'Pendente'),
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
    
    # Status e verificação
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDENTE',
        verbose_name="Status"
    )
    observacao = models.TextField(
        blank=True, 
        verbose_name="Observação"
    )
    
    # Fotos
    foto_antes = models.ImageField(
        upload_to='checklist/fotos/', 
        null=True, 
        blank=True,
        verbose_name="Foto Antes"
    )
    foto_depois = models.ImageField(
        upload_to='checklist/fotos/', 
        null=True, 
        blank=True,
        verbose_name="Foto Depois"
    )
    
    # Controle
    verificado_em = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Verificado em"
    )
    verificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name="Verificado por"
    )
    
    class Meta:
        ordering = ['item_padrao__ordem']
        unique_together = [['checklist', 'item_padrao']]
        verbose_name = 'Item de Checklist Realizado'
        verbose_name_plural = 'Itens de Checklist Realizados'
    
    def __str__(self):
        return f"{self.checklist} - {self.item_padrao.item}"


class AlertaManutencao(models.Model):
    """Alertas de manutenção gerados pelos checklists"""
    
    TIPO_CHOICES = [
        ('PREVENTIVA', 'Manutenção Preventiva'),
        ('CORRETIVA', 'Manutenção Corretiva'),
        ('URGENTE', 'Manutenção Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('NOTIFICADO', 'Notificado'),
        ('RESOLVIDO', 'Resolvido'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    CRITICIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    # Relacionamentos
    equipamento = models.ForeignKey(
        'equipamentos.Equipamento',
        on_delete=models.CASCADE,
        related_name='alertas_manutencao',
        verbose_name="Equipamento"
    )
    checklist_origem = models.ForeignKey(
        ChecklistNR12,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name="Checklist de Origem"
    )
    
    # Dados do alerta
    tipo = models.CharField(
        max_length=15, 
        choices=TIPO_CHOICES, 
        verbose_name="Tipo"
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='ATIVO',
        verbose_name="Status"
    )
    titulo = models.CharField(
        max_length=200, 
        verbose_name="Título"
    )
    descricao = models.TextField(
        verbose_name="Descrição"
    )
    criticidade = models.CharField(
        max_length=10, 
        choices=CRITICIDADE_CHOICES, 
        verbose_name="Criticidade"
    )
    
    # Datas
    data_identificacao = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data de Identificação"
    )
    data_prevista = models.DateField(
        verbose_name="Data Prevista"
    )
    data_notificacao = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data de Notificação"
    )
    data_resolucao = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data de Resolução"
    )
    
    # Auditoria
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Atualizado em"
    )
    
    class Meta:
        ordering = ['-data_prevista', '-criticidade']
        verbose_name = 'Alerta de Manutenção'
        verbose_name_plural = 'Alertas de Manutenção'
    
    def __str__(self):
        return f"{self.equipamento.nome} - {self.titulo}"
    
    @property
    def dias_restantes(self):
        """Dias restantes até a data prevista"""
        return (self.data_prevista - date.today()).days
    
    @property
    def is_urgente(self):
        """Verifica se o alerta é urgente (vence em até 3 dias)"""
        return self.dias_restantes <= 3
    
    @property
    def is_vencido(self):
        """Verifica se o alerta está vencido"""
        return self.data_prevista < date.today()
    
    def marcar_como_notificado(self):
        """Marca o alerta como notificado"""
        self.status = 'NOTIFICADO'
        self.data_notificacao = timezone.now()
        self.save()
    
    def marcar_como_resolvido(self):
        """Marca o alerta como resolvido"""
        self.status = 'RESOLVIDO'
        self.data_resolucao = timezone.now()
        self.save()


class Abastecimento(models.Model):
    """Registro de abastecimentos dos equipamentos"""
    
    TIPO_COMBUSTIVEL_CHOICES = [
        ('DIESEL', 'Diesel'),
        ('GASOLINA', 'Gasolina'),
        ('ETANOL', 'Etanol'),
        ('GNV', 'GNV'),
        ('ELETRICO', 'Elétrico'),
    ]
    
    equipamento = models.ForeignKey(
    'equipamentos.Equipamento',
    on_delete=models.CASCADE,
    related_name='abastecimentos_checklist',
    verbose_name="Equipamento"
)
    
    # Dados do abastecimento
    data_abastecimento = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data do Abastecimento"
    )
    tipo_combustivel = models.CharField(
        max_length=20,
        choices=TIPO_COMBUSTIVEL_CHOICES,
        verbose_name="Tipo de Combustível"
    )
    quantidade_litros = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Quantidade (Litros)"
    )
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Total (R$)"
    )
    valor_por_litro = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Valor por Litro (R$)"
    )
    
    # Horímetro no momento do abastecimento
    horimetro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horímetro"
    )
    
    # Local e responsável
    local_abastecimento = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Local do Abastecimento"
    )
    posto_fornecedor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Posto/Fornecedor"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    # Comprovante
    foto_comprovante = models.ImageField(
        upload_to='abastecimentos/comprovantes/',
        null=True,
        blank=True,
        verbose_name="Foto do Comprovante"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_abastecimento']
        verbose_name = 'Abastecimento'
        verbose_name_plural = 'Abastecimentos'
    
    def __str__(self):
        return f"{self.equipamento.nome} - {self.data_abastecimento.strftime('%d/%m/%Y %H:%M')} - {self.quantidade_litros}L"
    
    @property
    def valor_por_litro_calculado(self):
        """Calcula valor por litro se não informado"""
        if self.valor_por_litro:
            return self.valor_por_litro
        elif self.valor_total and self.quantidade_litros:
            return self.valor_total / self.quantidade_litros
        return None


class Anomalia(models.Model):
    """Registro de anomalias encontradas nos equipamentos"""
    
    TIPO_CHOICES = [
        ('MECANICA', 'Mecânica'),
        ('ELETRICA', 'Elétrica'),
        ('HIDRAULICA', 'Hidráulica'),
        ('PNEUMATICA', 'Pneumática'),
        ('ESTRUTURAL', 'Estrutural'),
        ('SEGURANCA', 'Segurança'),
        ('OPERACIONAL', 'Operacional'),
        ('OUTRAS', 'Outras'),
    ]
    
    SEVERIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica - Parar Operação'),
    ]
    
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANALISE', 'Em Análise'),
        ('EM_REPARO', 'Em Reparo'),
        ('AGUARDANDO_PECA', 'Aguardando Peça'),
        ('RESOLVIDA', 'Resolvida'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    # Identificação
    numero_anomalia = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número da Anomalia"
    )
    equipamento = models.ForeignKey(
        'equipamentos.Equipamento',
        on_delete=models.CASCADE,
        related_name='anomalias',
        verbose_name="Equipamento"
    )
    
    # Dados da anomalia
    data_identificacao = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Identificação"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo"
    )
    severidade = models.CharField(
        max_length=10,
        choices=SEVERIDADE_CHOICES,
        verbose_name="Severidade"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    descricao = models.TextField(
        verbose_name="Descrição"
    )
    
    # Localização no equipamento
    componente_afetado = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Componente Afetado"
    )
    
    # Horímetro quando detectada
    horimetro_deteccao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horímetro na Detecção"
    )
    
    # Status e resolução
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ABERTA',
        verbose_name="Status"
    )
    data_resolucao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Resolução"
    )
    solucao_aplicada = models.TextField(
        blank=True,
        verbose_name="Solução Aplicada"
    )
    
    # Responsáveis
    identificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anomalias_identificadas',
        verbose_name="Identificado por"
    )
    responsavel_reparo = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anomalias_reparadas',
        verbose_name="Responsável pelo Reparo"
    )
    
    # Evidências
    foto_anomalia = models.ImageField(
        upload_to='anomalias/fotos/',
        null=True,
        blank=True,
        verbose_name="Foto da Anomalia"
    )
    foto_reparo = models.ImageField(
        upload_to='anomalias/reparos/',
        null=True,
        blank=True,
        verbose_name="Foto do Reparo"
    )
    
    # Custos
    custo_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo Estimado (R$)"
    )
    custo_real = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo Real (R$)"
    )
    
    # Relacionamento com checklist
    checklist_origem = models.ForeignKey(
        'ChecklistNR12',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Checklist de Origem"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_identificacao']
        verbose_name = 'Anomalia'
        verbose_name_plural = 'Anomalias'
    
    def save(self, *args, **kwargs):
        if not self.numero_anomalia:
            # Gerar número sequencial
            ultimo_numero = Anomalia.objects.filter(
                numero_anomalia__startswith=f"ANO{date.today().year}"
            ).count()
            self.numero_anomalia = f"ANO{date.today().year}{ultimo_numero + 1:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_anomalia} - {self.equipamento.nome} - {self.titulo}"
    
    @property
    def dias_em_aberto(self):
        """Calcula dias que a anomalia está em aberto"""
        if self.status in ['RESOLVIDA', 'CANCELADA']:
            return 0
        return (timezone.now().date() - self.data_identificacao.date()).days
    
    @property
    def is_critica(self):
        """Verifica se é anomalia crítica"""
        return self.severidade == 'CRITICA'


class HistoricoHorimetro(models.Model):
    """Histórico de atualizações do horímetro"""
    
    equipamento = models.ForeignKey(
        'equipamentos.Equipamento',
        on_delete=models.CASCADE,
        related_name='historico_horimetro',
        verbose_name="Equipamento"
    )
    
    data_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data do Registro"
    )
    horimetro_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Horímetro Anterior"
    )
    horimetro_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Horímetro Atual"
    )
    horas_trabalhadas = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Horas Trabalhadas"
    )
    
    # Origem da atualização
    origem = models.CharField(
        max_length=50,
        choices=[
            ('CHECKLIST', 'Checklist NR12'),
            ('ABASTECIMENTO', 'Abastecimento'),
            ('ANOMALIA', 'Registro de Anomalia'),
            ('MANUTENCAO', 'Manutenção'),
            ('MANUAL', 'Atualização Manual'),
        ],
        verbose_name="Origem"
    )
    
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_registro']
        verbose_name = 'Histórico de Horímetro'
        verbose_name_plural = 'Histórico de Horímetros'
    
    def __str__(self):
        return f"{self.equipamento.nome} - {self.data_registro.strftime('%d/%m/%Y %H:%M')} - {self.horimetro_atual}h"




# ================================================================
# FUNÇÃO AUXILIAR PARA DASHBOARD
# ================================================================

def obter_estatisticas_nr12():
    """Retorna estatísticas dos checklists NR12 para dashboard"""
    hoje = date.today()
    
    stats = {
        'checklists_hoje': {
            'total': ChecklistNR12.objects.filter(data_checklist=hoje).count(),
            'pendentes': ChecklistNR12.objects.filter(data_checklist=hoje, status='PENDENTE').count(),
            'concluidos': ChecklistNR12.objects.filter(data_checklist=hoje, status='CONCLUIDO').count(),
            'com_problemas': ChecklistNR12.objects.filter(
                data_checklist=hoje, 
                status='CONCLUIDO', 
                necessita_manutencao=True
            ).count(),
        },
        'alertas_ativos': AlertaManutencao.objects.filter(status__in=['ATIVO', 'NOTIFICADO']).count(),
        'alertas_criticos': AlertaManutencao.objects.filter(
            status__in=['ATIVO', 'NOTIFICADO'], 
            criticidade='CRITICA'
        ).count(),
        'equipamentos_nr12_ativos': None,  # Será calculado se necessário
    }
    
    # Calcular equipamentos NR12 ativos se necessário
    try:
        from backend.apps.equipamentos.models import Equipamento
        stats['equipamentos_nr12_ativos'] = Equipamento.objects.filter(ativo_nr12=True).count()
    except:
        pass
    
    return stats
