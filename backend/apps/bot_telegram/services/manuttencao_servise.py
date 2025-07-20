# backend/apps/bot_telegram/services/manutencao_service.py
from asgiref.sync import sync_to_async
from backend.apps.manutencao.models import HistoricoManutencao

async def get_ultima_manutencao(equipamento_id: int):
    return await sync_to_async(
        lambda: HistoricoManutencao.objects.filter(
            equipamento_id=equipamento_id
        ).order_by('-data').first()
    )()

async def list_historico(equipamento_id: int, limit: int = 5):
    return await sync_to_async(
        lambda: list(
            HistoricoManutencao.objects.filter(
                equipamento_id=equipamento_id
            ).order_by('-data')[:limit]
        )
    )()
