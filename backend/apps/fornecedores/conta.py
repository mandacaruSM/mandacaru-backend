from django.db import models
from backend.apps.clientes.models import Cliente
from backend.apps.financeiro.models.fornecedor import Fornecedor


class ContaFinanceira(models.Model):
    TIPO_CHOICES = (
        ('pagar', 'Pagar'),
        ('receber', 'Receber'),
    )
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
    )

    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    forma_pagamento = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    comprovante = models.FileField(upload_to='comprovantes/', null=True, blank=True)

    def __str__(self):
        return f"{self.descricao} - {self.tipo} - {self.status}"
