# backend/apps/financeiro/models/__init__.py

from .conta_financeira import ContaFinanceira

class ContaReceber(ContaFinanceira):
    class Meta:
        proxy = True
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
