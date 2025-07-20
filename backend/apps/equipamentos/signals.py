from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import (
    ChecklistNR12,
    ItemChecklistPadrao,
    ItemChecklistRealizado
)

@receiver(post_save, sender=Equipamento)
def gerar_checklists_automaticamente(sender, instance, created, **kwargs):
    """
    Ao salvar um equipamento, gera automaticamente checklists NR12 para cada
    frequência marcada (DIARIA, SEMANAL, MENSAL), vinculando os itens padrão.
    """
    if not instance.ativo_nr12 or not instance.tipo_nr12:
        return

    frequencias = instance.frequencias_checklist or []
    hoje = timezone.now().date()

    for freq in frequencias:
        checklist, criado = ChecklistNR12.objects.get_or_create(
            equipamento=instance,
            data_checklist=hoje,
            turno='MANHA',
            defaults={
                'status': 'PENDENTE',
                'frequencia': freq
            }
        )
        if criado:
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=instance.tipo_nr12
            )
            for item in itens_padrao:
                ItemChecklistRealizado.objects.create(
                    checklist=checklist,
                    item_padrao=item,
                    status='PENDENTE'
                )
