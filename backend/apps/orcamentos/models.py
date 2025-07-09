# backend/apps/orcamentos/models.py
from django.db import models
from django.utils import timezone

from backend.apps.clientes.models import Cliente
from backend.apps.empreendimentos.models import Empreendimento
from backend.apps.equipamentos.models import Equipamento

class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aprovado'),
        ('R', 'Rejeitado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.CASCADE, related_name='orcamentos')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='orcamentos')
    data_criacao = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    os_criada = models.BooleanField(default=False)

    def __str__(self):
        return f"Orçamento #{self.id} - {self.get_status_display()}"