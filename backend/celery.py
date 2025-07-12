# ================================================================
# CRIAR backend/celery.py
# ================================================================

import os
from celery import Celery
from django.conf import settings

# Definir o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('mandacaru')

# Usar configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobrir tasks automaticamente
app.autodiscover_tasks()

# Configurações básicas
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Schedule para tasks periódicas
app.conf.beat_schedule = {
    # Calcular KPIs diários às 6h
    'calcular-kpis-diarios': {
        'task': 'backend.apps.dashboard.tasks.calcular_kpis_diarios',
        'schedule': 60.0 * 60.0 * 6,  # 6 horas em segundos
    },
    
    # Gerar checklists diários às 5h
    'gerar-checklists-diarios': {
        'task': 'backend.apps.dashboard.tasks.gerar_checklists_automatico',
        'schedule': 60.0 * 60.0 * 5,  # 5 horas em segundos
    },
    
    # Verificar alertas de manutenção a cada hora
    'verificar-alertas-manutencao': {
        'task': 'backend.apps.dashboard.tasks.verificar_alertas_manutencao',
        'schedule': 60.0 * 60.0,  # 1 hora
    },
    
    # Limpeza de dados antigos uma vez por semana (domingo às 2h)
    'limpeza-dados-antigos': {
        'task': 'backend.apps.dashboard.tasks.limpeza_dados_antigos',
        'schedule': 60.0 * 60.0 * 24 * 7,  # 1 semana
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')