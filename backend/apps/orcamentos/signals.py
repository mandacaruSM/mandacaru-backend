
# apps/orcamentos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from backend.apps.orcamentos.models import Orcamento
from backend.apps.ordens_servico.models import OrdemServico

@receiver(post_save, sender=Orcamento)
def criar_ordem_servico(sender, instance, created, **kwargs):
    if instance.status == 'aprovado':
        OrdemServico.objects.get_or_create(orcamento=instance)
