# backend/apps/orcamentos/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Orcamento, OrcamentoItem
from apps.ordem_servico.models import OrdemServico

@receiver(pre_save, sender=Orcamento)
def calcular_deslocamento_e_total(sender, instance, **kwargs):
    emp = instance.empreendimento
    # assume Empreendimento tem campo distancia_km e tarifa_km
    instance.distancia_km = emp.distancia_km
    instance.custo_deslocamento = emp.distancia_km * emp.tarifa_km

@receiver(post_save, sender=Orcamento)
def atualizar_valor_total(sender, instance, created, **kwargs):
    total_itens = instance.itens.aggregate(
        soma=Sum(F('subtotal'))
    )['soma'] or 0
    instance.valor_total = total_itens + instance.custo_deslocamento
    # evita recursão infinita
    Orcamento.objects.filter(pk=instance.pk).update(valor_total=instance.valor_total)

@receiver(post_save, sender=Orcamento)
def criar_os_quando_aprovado(sender, instance, **kwargs):
    if instance.status == 'APROVADO':
        if not OrdemServico.objects.filter(orcamento=instance).exists():
            OrdemServico.objects.create(
                orcamento=instance,
                cliente=instance.cliente,
                equipamento=None,  # definir padrão ou capturar do primeiro item
                descricao=f"OS gerada a partir do Orçamento #{instance.pk}",
            )