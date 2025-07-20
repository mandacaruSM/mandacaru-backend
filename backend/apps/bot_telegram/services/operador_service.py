# backend/apps/bot_telegram/services/operador_service.py
from asgiref.sync import sync_to_async
from backend.apps.operadores.models import Operador

async def get_operador_por_codigo(codigo: str):
    return await sync_to_async(
        lambda: Operador.objects.get(codigo=codigo.upper(), status='ATIVO')
    )()

async def list_operadores_ativos(limit: int = 20):
    return await sync_to_async(
        lambda: list(
            Operador.objects.filter(status='ATIVO')
            .order_by('nome')[:limit]
        )
    )()
