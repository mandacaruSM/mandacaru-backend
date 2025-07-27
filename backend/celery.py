# backend/celery.py - Configuração DEFINITIVA para Windows

import os
from celery import Celery
from celery.schedules import crontab

# Configuração obrigatória para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Criar app Celery
app = Celery('mandacaru_erp')

# Configurações básicas
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ================================================================
# CONFIGURAÇÃO ESPECÍFICA PARA WINDOWS
# ================================================================

app.conf.update(
    # BROKER E BACKEND
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    
    # SERIALIZAÇÃO
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # TIMEZONE
    timezone='America/Sao_Paulo',
    enable_utc=True,
    
    # CONFIGURAÇÕES CRÍTICAS PARA WINDOWS
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    
    # WORKER POOL - THREADS para Windows
    worker_pool='threads',
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    
    # TIMEOUTS
    task_time_limit=300,  # 5 minutos
    task_soft_time_limit=240,  # 4 minutos
    
    # CONFIGURAÇÕES DE TASK
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # RESULTADO
    result_expires=3600,
    
    # BROKER OPTIONS
    broker_transport_options={
        'visibility_timeout': 3600,
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    },
)

# ================================================================
# AGENDAMENTOS
# ================================================================

app.conf.beat_schedule = {
    'gerar-checklists-diarios': {
        'task': 'backend.apps.nr12_checklist.tasks.gerar_checklists_diarios',
        'schedule': crontab(hour=6, minute=0),
    },
    'gerar-checklists-semanais': {
        'task': 'backend.apps.nr12_checklist.tasks.gerar_checklists_semanais',
        'schedule': crontab(hour=6, minute=0, day_of_week=1),
    },
    'gerar-checklists-mensais': {
        'task': 'backend.apps.nr12_checklist.tasks.gerar_checklists_mensais',
        'schedule': crontab(hour=6, minute=0, day_of_month=1),
    },
}

app.conf.task_default_queue = 'default'

# ================================================================
# TASKS DE TESTE
# ================================================================

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return f'Task executada com sucesso!'

@app.task
def test_simple():
    import datetime
    return f'Teste executado em {datetime.datetime.now()}'