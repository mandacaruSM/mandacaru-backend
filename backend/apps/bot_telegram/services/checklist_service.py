# backend/apps/bot_telegram/services/checklist_service.py
from asgiref.sync import sync_to_async
from backend.apps.nr12_checklist.models import ChecklistNR12
from datetime import date

async def get_checklist_do_dia(equipamento_id: int):
    hoje = date.today()
    return await sync_to_async(
        lambda: ChecklistNR12.objects.filter(
            equipamento_id=equipamento_id,
            data_checklist=hoje
        ).first()
    )()

async def list_checklists_pendentes(turno: str = None, limit: int = 10):
    hoje = date.today()
    qs = ChecklistNR12.objects.filter(
        data_checklist=hoje,
        status__in=['PENDENTE', 'EM_ANDAMENTO']
    )
    if turno:
        qs = qs.filter(turno=turno)
    return await sync_to_async(lambda: list(qs.select_related('equipamento')[:limit]))()
