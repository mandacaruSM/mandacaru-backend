from django.db import models
from apps.ordens_servico.models import OrdemServico

class Lancamento(models.Model):
    TIPO_CHOICES = (
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    )
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo.upper()} - R$ {self.valor:.2f} - {self.data}"
