from celery import shared_task
from datetime import date
from django.utils import timezone
from backend.apps.nr12_checklist.models import ChecklistNR12
from backend.apps.equipamentos.models import Equipamento

@shared_task
def gerar_checklists_diarios():
    hoje = date.today()
    equipamentos = Equipamento.objects.filter(
        ativo_nr12=True,
        frequencia_checklist='DIARIA'
    )
    for eq in equipamentos:
        ChecklistNR12.objects.get_or_create(
            equipamento=eq,
            data_checklist=hoje,
            turno='MANHA',
            defaults={'frequencia':'DIARIA', 'status':'PENDENTE'}
        )

@shared_task
def gerar_checklists_semanais():
    hoje = date.today()
    # roda toda segunda-feira via schedule
    equipamentos = Equipamento.objects.filter(
        ativo_nr12=True,
        frequencia_checklist='SEMANAL'
    )
    for eq in equipamentos:
        ChecklistNR12.objects.get_or_create(
            equipamento=eq,
            data_checklist=hoje,
            turno='MANHA',
            defaults={'frequencia':'SEMANAL', 'status':'PENDENTE'}
        )

@shared_task
def gerar_checklists_mensais():
    hoje = date.today()
    # roda dia 1º de cada mês via schedule
    equipamentos = Equipamento.objects.filter(
        ativo_nr12=True,
        frequencia_checklist='MENSAL'
    )
    for eq in equipamentos:
        ChecklistNR12.objects.get_or_create(
            equipamento=eq,
            data_checklist=hoje,
            turno='MANHA',
            defaults={'frequencia':'MENSAL', 'status':'PENDENTE'}
        )
