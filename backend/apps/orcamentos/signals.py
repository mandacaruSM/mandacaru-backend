# ================================================================
# SUBSTITUIR COMPLETAMENTE backend/apps/orcamentos/signals.py
# ================================================================

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Sum, F
from .models import Orcamento, OrcamentoItem

@receiver(pre_save, sender=Orcamento)
def calcular_deslocamento_e_total(sender, instance, **kwargs):
    """Calcula custo de deslocamento baseado na distância do empreendimento"""
    if instance.empreendimento:
        instance.distancia_km = instance.empreendimento.distancia_km
        # Assumindo uma tarifa por km (pode ser configurável depois)
        tarifa_por_km = 2.50  # R$ 2,50 por km
        instance.custo_deslocamento = instance.distancia_km * tarifa_por_km

@receiver(post_save, sender=Orcamento)
def atualizar_valor_total(sender, instance, created, **kwargs):
    """Atualiza valor total do orçamento baseado nos itens"""
    if not created:  # Só calcular se não for criação inicial
        total_itens = instance.itens.aggregate(
            soma=Sum(F('subtotal'))
        )['soma'] or 0
        
        novo_valor_total = float(total_itens) + float(instance.custo_deslocamento)
        
        # Evita recursão infinita
        if instance.valor_total != novo_valor_total:
            Orcamento.objects.filter(pk=instance.pk).update(valor_total=novo_valor_total)

@receiver(post_save, sender=OrcamentoItem)
def recalcular_orcamento_ao_salvar_item(sender, instance, **kwargs):
    """Recalcula total do orçamento quando um item é adicionado/modificado"""
    orcamento = instance.orcamento
    total_itens = orcamento.itens.aggregate(
        soma=Sum(F('subtotal'))
    )['soma'] or 0
    
    novo_valor_total = float(total_itens) + float(orcamento.custo_deslocamento)
    
    # Atualizar sem triggerar signals
    Orcamento.objects.filter(pk=orcamento.pk).update(valor_total=novo_valor_total)

# ================================================================
# COMENTAR A INTEGRAÇÃO COM ORDEM DE SERVIÇO POR ENQUANTO
# ================================================================

# @receiver(post_save, sender=Orcamento)
# def criar_os_quando_aprovado(sender, instance, **kwargs):
#     """Cria ordem de serviço quando orçamento é aprovado"""
#     if instance.status == 'APROVADO':
#         from backend.apps.ordens_servico.models import OrdemServico
#         if not OrdemServico.objects.filter(orcamento=instance).exists():
#             OrdemServico.objects.create(
#                 orcamento=instance,
#                 cliente=instance.cliente,
#                 # equipamento será definido depois
#                 descricao=f"OS gerada a partir do Orçamento #{instance.pk}",
#             )