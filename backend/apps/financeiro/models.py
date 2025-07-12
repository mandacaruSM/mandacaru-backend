from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date, timedelta

class ContaFinanceira(models.Model):
    """Modelo unificado para contas a pagar e receber"""
    
    TIPO_CHOICES = [
        ('PAGAR', 'Conta a Pagar'),
        ('RECEBER', 'Conta a Receber'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('VENCIDO', 'Vencido'),
        ('CANCELADO', 'Cancelado'),
        ('PARCIAL', 'Pago Parcial'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('PIX', 'PIX'),
        ('BOLETO', 'Boleto'),
        ('TRANSFERENCIA', 'Transferência'),
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('CHEQUE', 'Cheque'),
    ]
    
    CATEGORIA_CHOICES = [
        # Receitas
        ('SERVICO', 'Serviços Prestados'),
        ('VENDA_PRODUTO', 'Venda de Produtos'),
        ('ALUGUEL_RECEBIDO', 'Aluguel Recebido'),
        
        # Despesas
        ('FORNECEDOR', 'Pagamento a Fornecedor'),
        ('SALARIO', 'Salários e Encargos'),
        ('ALUGUEL_PAGO', 'Aluguel Pago'),
        ('COMBUSTIVEL', 'Combustível'),
        ('MANUTENCAO', 'Manutenção'),
        ('DESPESA_OPERACIONAL', 'Despesa Operacional'),
        ('IMPOSTO', 'Impostos e Taxas'),
        ('OUTROS', 'Outros'),
    ]
    
    # Campos principais
    numero = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Numeração sequencial automática"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    
    # Valores
    valor_original = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor_pago = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    valor_desconto = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    valor_juros = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Datas
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    data_competencia = models.DateField(default=date.today)
    
    # Status e forma
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES)
    
    # Relacionamentos
    cliente = models.ForeignKey(
        'clientes.Cliente', 
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='contas_financeiras'
    )
    fornecedor = models.ForeignKey(
        'fornecedor.Fornecedor',
        on_delete=models.PROTECT, 
        null=True, blank=True,
        related_name='contas_financeiras'
    )
    ordem_servico = models.ForeignKey(
        'ordens_servico.OrdemServico',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contas_financeiras'
    )
    
    # Documentação
    documento_numero = models.CharField(max_length=100, blank=True)
    comprovante = models.FileField(
        upload_to='comprovantes/%Y/%m/', 
        null=True, blank=True
    )
    observacoes = models.TextField(blank=True)
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth_cliente.UsuarioCliente',
        on_delete=models.PROTECT,
        related_name='contas_criadas'
    )
    
    class Meta:
        ordering = ['-data_vencimento', '-created_at']
        verbose_name = 'Conta Financeira'
        verbose_name_plural = 'Contas Financeiras'
        indexes = [
            models.Index(fields=['tipo', 'status']),
            models.Index(fields=['data_vencimento']),
            models.Index(fields=['data_competencia']),
            models.Index(fields=['numero']),
        ]
    
    def __str__(self):
        return f"{self.numero} - {self.descricao} - R$ {self.valor_original}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._gerar_numero()
        
        # Atualizar status baseado no pagamento
        self._atualizar_status()
        
        super().save(*args, **kwargs)
    
    def _gerar_numero(self):
        """Gera número sequencial"""
        ano_atual = date.today().year
        prefixo = f"{self.tipo[0]}{ano_atual}"
        
        ultimo = ContaFinanceira.objects.filter(
            numero__startswith=prefixo
        ).order_by('-numero').first()
        
        if ultimo:
            ultimo_num = int(ultimo.numero.split('-')[-1])
            proximo = ultimo_num + 1
        else:
            proximo = 1
            
        return f"{prefixo}-{proximo:06d}"
    
    def _atualizar_status(self):
        """Atualiza status baseado nos valores"""
        if self.valor_pago == 0:
            if self.data_vencimento < date.today():
                self.status = 'VENCIDO'
            else:
                self.status = 'PENDENTE'
        elif self.valor_pago >= self.valor_final:
            self.status = 'PAGO'
        else:
            self.status = 'PARCIAL'
    
    @property
    def valor_final(self):
        """Valor final considerando descontos e juros"""
        return self.valor_original - self.valor_desconto + self.valor_juros
    
    @property
    def valor_restante(self):
        """Valor ainda a ser pago"""
        return max(0, self.valor_final - self.valor_pago)
    
    @property
    def dias_vencimento(self):
        """Dias até/desde o vencimento (negativo = vencido)"""
        return (self.data_vencimento - date.today()).days
    
    @property
    def esta_vencido(self):
        """Verifica se está vencido"""
        return self.data_vencimento < date.today() and self.status != 'PAGO'
    
    def registrar_pagamento(self, valor, data_pagamento=None, observacao=''):
        """Registra um pagamento"""
        if not data_pagamento:
            data_pagamento = date.today()
            
        valor = Decimal(str(valor))
        
        if valor <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        if self.valor_pago + valor > self.valor_final:
            raise ValueError("Valor excede o valor total da conta")
        
        # Atualizar valores
        self.valor_pago += valor
        self.data_pagamento = data_pagamento
        
        if observacao:
            self.observacoes += f"\nPagamento R$ {valor} em {data_pagamento} - {observacao}"
        
        self.save()
        
        # Criar histórico
        HistoricoPagamento.objects.create(
            conta=self,
            valor=valor,
            data_pagamento=data_pagamento,
            observacao=observacao
        )


class HistoricoPagamento(models.Model):
    """Histórico de pagamentos de uma conta"""
    
    conta = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.CASCADE,
        related_name='historico_pagamentos'
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_pagamento = models.DateField()
    forma_pagamento = models.CharField(
        max_length=20, 
        choices=ContaFinanceira.FORMA_PAGAMENTO_CHOICES
    )
    observacao = models.TextField(blank=True)
    comprovante = models.FileField(
        upload_to='comprovantes/%Y/%m/', 
        null=True, blank=True
    )
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth_cliente.UsuarioCliente',
        on_delete=models.PROTECT
    )
    
    class Meta:
        ordering = ['-data_pagamento', '-created_at']
        verbose_name = 'Histórico de Pagamento'
        verbose_name_plural = 'Histórico de Pagamentos'
    
    def __str__(self):
        return f"{self.conta.numero} - R$ {self.valor} - {self.data_pagamento}"


class CentroCusto(models.Model):
    """Centros de custo para categorização"""
    
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    
    # Hierarquia
    centro_pai = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='subcentros'
    )
    
    class Meta:
        ordering = ['codigo']
        verbose_name = 'Centro de Custo'
        verbose_name_plural = 'Centros de Custo'
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"


# Adicionar campo centro_custo em ContaFinanceira
ContaFinanceira.add_to_class(
    'centro_custo',
    models.ForeignKey(
        CentroCusto,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='contas'
    )
)