# apps/financeiro/models.py
from django.db import models
from backend.apps.clientes.models import Cliente
from backend.apps.fornecedor.models import Fornecedor

class ContaFinanceira(models.Model):
    TIPO_CHOICES = [
        ("pagar", "Conta a Pagar"),
        ("receber", "Conta a Receber")
    ]
    FORMA_PAGAMENTO = [
        ("Pix", "Pix"),
        ("Boleto", "Boleto"),
        ("Transferência", "Transferência"),
        ("Dinheiro", "Dinheiro"),
        ("Cartão", "Cartão")
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO)
    status = models.CharField(max_length=20, default="pendente")
    comprovante = models.ImageField(upload_to="comprovantes/", null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    fornecedor = models.ForeignKey(Fornecedor, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_despesa = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.descricao} - R$ {self.valor}"

