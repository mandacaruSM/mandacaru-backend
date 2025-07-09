# backend/apps/ordens_servico/models.py
from django.db import models
from django.utils import timezone

from backend.apps.clientes.models import Cliente
from backend.apps.equipamentos.models import Equipamento
from backend.apps.orcamentos.models import Orcamento

class OrdemServico(models.Model):
    orcamento = models.OneToOneField(
        Orcamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordem_servico'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='ordens_servico'
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.CASCADE,
        related_name='ordens_servico'
    )
    data_abertura = models.DateTimeField(default=timezone.now)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    finalizada = models.BooleanField(default=False)

    def __str__(self):
        status = 'Finalizada' if self.finalizada else 'Aberta'
        return f"OS #{self.id} - {status}"