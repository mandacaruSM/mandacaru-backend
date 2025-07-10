# backend/apps/orcamentos/models.py
from django.db import models
from django.db.models import Sum, F

class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('CONVERTIDO', 'Convertido'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey('cliente.Cliente', on_delete=models.CASCADE, related_name='orcamentos')
    empreendimento = models.ForeignKey(
        'empreendimentos.Empreendimento', on_delete=models.PROTECT, related_name='orcamentos'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_vencimento = models.DateField()
    distancia_km = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    custo_deslocamento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    aprovado_por_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.cliente.nome}"

class OrcamentoItem(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(
        'almoxarifado.Produto', on_delete=models.PROTECT, related_name='+')
    quantidade = models.DecimalField(max_digits=8, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
