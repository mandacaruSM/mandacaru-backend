# backend/apps/financeiro/models/conta_receber.py
from django.db import models
from backend.apps.clientes.models import Cliente

class ContaReceber(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(blank=True, null=True)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente.nome_fantasia} - R$ {self.valor}"
