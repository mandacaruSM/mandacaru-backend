from django.db import models
from backend.apps.clientes.models import Cliente
from backend.apps.empreendimentos.models import Empreendimento
from backend.apps.equipamentos.models import Equipamento
from django.utils import timezone

class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.CASCADE)
    equipamentos = models.ManyToManyField(Equipamento)
    data_criacao = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')

    def __str__(self):
        return f"Orçamento #{self.id} - {self.cliente.razao_social} - {self.status}"
