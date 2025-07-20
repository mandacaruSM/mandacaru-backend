# backend/apps/bot_telegram/services/equipamento_service.py
from asgiref.sync import sync_to_async
from backend.apps.equipamentos.models import Equipamento

async def get_equipamento_by_id(equipamento_id: int):
    return await sync_to_async(
        lambda: Equipamento.objects.select_related('cliente').get(id=equipamento_id)
    )()

async def list_equipamentos_ativos(limit: int = 10):
    return await sync_to_async(
        lambda: list(
            Equipamento.objects.filter(ativo_nr12=True)
            .select_related('cliente')
            .order_by('nome')[:limit]
        )
    )()
