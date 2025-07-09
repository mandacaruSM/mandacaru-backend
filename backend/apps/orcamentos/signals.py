# backend/apps/orcamentos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Orcamento
from backend.apps.ordens_servico.models import OrdemServico

@receiver(post_save, sender=Orcamento)
def criar_os_apos_aprovacao(sender, instance, created, **kwargs):
    # se atualização e status aprovado e ainda não criou OS
    if not created and instance.status == 'A' and not instance.os_criada:
        OrdemServico.objects.create(
            orcamento=instance,
            cliente=instance.cliente,
            equipamento=instance.equipamento,
            data_abertura=timezone.now(),
            descricao=f"OS gerada a partir do orçamento #{instance.id}",
            finalizada=False,
        )
        instance.os_criada = True
        instance.save(update_fields=['os_criada'])
