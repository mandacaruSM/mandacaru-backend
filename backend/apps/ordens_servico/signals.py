# apps/ordens_servico/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from backend.apps.ordens_servico.models import OrdemServico
from backend.apps.financeiro.models import ContaFinanceira

@receiver(post_save, sender=OrdemServico)
def gerar_conta_a_receber(sender, instance, **kwargs):
    if instance.finalizada:
        # Verifica se já existe conta para esta OS
        existe = ContaFinanceira.objects.filter(descricao=f"Ordem de Serviço #{instance.id}").exists()
        if not existe:
            ContaFinanceira.objects.create(
                tipo="receber",
                descricao=f"Ordem de Serviço #{instance.id}",
                valor=instance.orcamento.valor,
                vencimento=instance.data_execucao,
                forma_pagamento="Pix",  # valor padrão, pode ser ajustado no frontend depois
                cliente=instance.orcamento.cliente,
                status="pendente"
            )
