# TASK PARA CALCULAR KPIS AUTOMATICAMENTE
# ================================================================

# backend/apps/dashboard/tasks.py
from celery import shared_task
from .models import KPISnapshot

@shared_task
def calcular_kpis_diarios():
    """Task para calcular KPIs diários automaticamente"""
    snapshot = KPISnapshot.calcular_kpis_hoje()
    return f"KPIs calculados para {snapshot.data_snapshot}"