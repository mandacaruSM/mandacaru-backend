# ================================================================
# CONFIGURAÇÃO COMPLETA DO CELERY - AUTOMAÇÃO DE CHECKLISTS
# backend/celery.py - VERSÃO FINAL COMPLETA
# ================================================================

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Definir o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Criar instância do Celery
app = Celery('mandacaru_erp')

# Usar configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobrir tasks automaticamente em todos os apps
app.autodiscover_tasks()

# ================================================================
# CONFIGURAÇÕES BÁSICAS DO CELERY
# ================================================================

app.conf.update(
    # Serialização
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='America/Sao_Paulo',
    enable_utc=True,
    
    # Configurações de task
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Configurações de resultado
    result_expires=3600,  # 1 hora
    result_backend='redis://localhost:6379/0',
    
    # Configurações de broker
    broker_url='redis://localhost:6379/0',
    broker_transport_options={'visibility_timeout': 3600},
)

# ================================================================
# AGENDAMENTOS AUTOMÁTICOS - CHECKLISTS NR12
# ================================================================

app.conf.beat_schedule = {
    
    # ===============================================
    # 🕕 AUTOMAÇÃO PRINCIPAL DE CHECKLISTS
    # ===============================================
    
    # GERAÇÃO AUTOMÁTICA às 6h da manhã (DIÁRIO/SEMANAL/MENSAL)
    'gerar-checklists-automaticos': {
        'task': 'backend.apps.core.tasks.gerar_checklists_automatico',
        'schedule': crontab(hour=6, minute=0),  # Todo dia às 6:00
        'options': {
            'queue': 'checklists',
            'priority': 9,  # Alta prioridade
        },
    },
    
    # VERIFICAR CHECKLISTS ATRASADOS às 7h da manhã
    'verificar-checklists-atrasados': {
        'task': 'backend.apps.core.tasks.verificar_checklists_atrasados',
        'schedule': crontab(hour=7, minute=0),  # Todo dia às 7:00
        'options': {
            'queue': 'checklists',
            'priority': 8,
        },
    },
    
    # NOTIFICAR CHECKLISTS PENDENTES a cada 2h (8h às 18h)
    'notificar-checklists-pendentes': {
        'task': 'backend.apps.core.tasks.notificar_checklists_pendentes',
        'schedule': crontab(minute=0, hour='8,10,12,14,16,18'),
        'options': {
            'queue': 'notifications',
            'priority': 7,
        },
    },
    
    # RELATÓRIO SEMANAL toda segunda-feira às 7:30
    'relatorio-checklists-semanal': {
        'task': 'backend.apps.core.tasks.gerar_relatorio_checklists_semanal',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),  # Segunda-feira
        'options': {
            'queue': 'reports',
            'priority': 5,
        },
    },
    
    # ===============================================
    # 🔧 MANUTENÇÃO E INTEGRIDADE
    # ===============================================
    
    # VERIFICAR INTEGRIDADE DOS DADOS às 4h da manhã
    'verificar-integridade-dados': {
        'task': 'backend.apps.core.tasks.verificar_integridade_dados',
        'schedule': crontab(hour=4, minute=0),  # Todo dia às 4:00
        'options': {
            'queue': 'maintenance',
            'priority': 4,
        },
    },
    
    # LIMPEZA DE CHECKLISTS ANTIGOS todo domingo às 3h
    'limpar-checklists-antigos': {
        'task': 'backend.apps.core.tasks.limpar_checklists_antigos',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Domingo às 3:00
        'options': {
            'queue': 'maintenance',
            'priority': 3,
        },
    },
    
    # ===============================================
    # 📊 DASHBOARD E KPIS
    # ===============================================
    
    # CALCULAR KPIS DIÁRIOS às 5h da manhã
    'calcular-kpis-diarios': {
        'task': 'backend.apps.dashboard.tasks.calcular_kpis_diarios',
        'schedule': crontab(hour=5, minute=0),  # Todo dia às 5:00
        'options': {
            'queue': 'dashboard',
            'priority': 6,
        },
    },
    
    # ===============================================
    # 🔲 QR CODES
    # ===============================================
    
    # GERAR QR CODES DIÁRIOS às 5:30 da manhã
    'gerar-qr-codes-diarios': {
        'task': 'backend.apps.nr12_checklist.qr_manager.gerar_qr_codes_diarios',
        'schedule': crontab(hour=5, minute=30),  # Todo dia às 5:30
        'options': {
            'queue': 'qrcodes',
            'priority': 5,
        },
    },
    
    # LIMPAR QR CODES ANTIGOS todo domingo às 4h
    'limpar-qr-codes-antigos': {
        'task': 'backend.apps.nr12_checklist.qr_manager.limpar_qr_codes_antigos',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),  # Domingo às 4:00
        'options': {
            'queue': 'qrcodes',
            'priority': 3,
        },
    },
    
    # ===============================================
    # 📦 ALMOXARIFADO E ESTOQUE
    # ===============================================
    
    # VERIFICAR ESTOQUES BAIXOS às 8h da manhã
    'verificar-estoques-baixos': {
        'task': 'backend.apps.almoxarifado.tasks.verificar_estoques_baixos',
        'schedule': crontab(hour=8, minute=0),  # Todo dia às 8:00
        'options': {
            'queue': 'inventory',
            'priority': 6,
        },
    },
    
    # CONSOLIDAR MOVIMENTAÇÕES DIÁRIAS às 23h
    'consolidar-movimentacoes-diarias': {
        'task': 'backend.apps.almoxarifado.tasks.consolidar_movimentacoes_diarias',
        'schedule': crontab(hour=23, minute=0),  # Todo dia às 23:00
        'options': {
            'queue': 'inventory',
            'priority': 4,
        },
    },
    
    # ===============================================
    # 🚨 ALERTAS E MANUTENÇÃO
    # ===============================================
    
    # VERIFICAR ALERTAS DE MANUTENÇÃO a cada hora (7h às 19h)
    'verificar-alertas-manutencao': {
        'task': 'backend.apps.core.tasks.verificar_alertas_manutencao',
        'schedule': crontab(minute=0, hour='7-19'),  # A cada hora das 7h às 19h
        'options': {
            'queue': 'alerts',
            'priority': 7,
        },
    },
    
    # ===============================================
    # 🤖 BOT TELEGRAM E NOTIFICAÇÕES
    # ===============================================
    
    # RESUMO DIÁRIO VIA TELEGRAM às 18h
    'enviar-resumo-diario-telegram': {
        'task': 'backend.apps.bot_telegram.notifications.enviar_resumo_diario_task',
        'schedule': crontab(hour=18, minute=0),  # Todo dia às 18:00
        'options': {
            'queue': 'notifications',
            'priority': 6,
        },
    },
    
    # NOTIFICAR CHECKLISTS ATRASADOS VIA TELEGRAM às 9h e 15h
    'notificar-telegram-checklists-atrasados': {
        'task': 'backend.apps.bot_telegram.notifications.notificar_checklists_atrasados',
        'schedule': crontab(minute=0, hour='9,15'),  # Às 9h e 15h
        'options': {
            'queue': 'notifications',
            'priority': 7,
        },
    },
    
    # ===============================================
    # 💰 FINANCEIRO
    # ===============================================
    
    # VERIFICAR CONTAS VENCIDAS às 9h da manhã
    'verificar-contas-vencidas': {
        'task': 'backend.apps.financeiro.tasks.verificar_contas_vencidas',
        'schedule': crontab(hour=9, minute=0),  # Todo dia às 9:00
        'options': {
            'queue': 'financial',
            'priority': 6,
        },
    },
    
    # RELATÓRIO FINANCEIRO MENSAL no dia 1º às 8h
    'relatorio-financeiro-mensal': {
        'task': 'backend.apps.financeiro.tasks.gerar_relatorio_mensal',
        'schedule': crontab(hour=8, minute=0, day_of_month=1),  # Dia 1º às 8:00
        'options': {
            'queue': 'reports',
            'priority': 5,
        },
    },
    
    # ===============================================
    # 🔄 BACKUP E SEGURANÇA
    # ===============================================
    
    # BACKUP DIÁRIO às 2h da manhã
    'backup-dados-importantes': {
        'task': 'backend.apps.core.tasks.backup_dados_importantes',
        'schedule': crontab(hour=2, minute=0),  # Todo dia às 2:00
        'options': {
            'queue': 'backup',
            'priority': 8,
        },
    },
    
    # BACKUP SEMANAL COMPLETO todo domingo às 1h
    'backup-completo-semanal': {
        'task': 'backend.apps.core.tasks.backup_completo_semanal',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),  # Domingo às 1:00
        'options': {
            'queue': 'backup',
            'priority': 9,
        },
    },
    
    # ===============================================
    # 📈 MONITORAMENTO SISTEMA
    # ===============================================
    
    # MONITORAMENTO DO SISTEMA a cada 30 minutos
    'monitoramento-sistema': {
        'task': 'backend.apps.core.tasks.monitoramento_sistema',
        'schedule': crontab(minute='*/30'),  # A cada 30 minutos
        'options': {
            'queue': 'monitoring',
            'priority': 4,
        },
    },
    
    # HEALTH CHECK a cada 5 minutos
    'health-check-sistema': {
        'task': 'backend.apps.core.tasks.health_check_sistema',
        'schedule': crontab(minute='*/5'),  # A cada 5 minutos
        'options': {
            'queue': 'monitoring',
            'priority': 3,
        },
    },
    
    # ===============================================
    # 🧹 LIMPEZA GERAL
    # ===============================================
    
    # LIMPEZA DE LOGS ANTIGOS todo domingo às 2h
    'limpeza-logs-antigos': {
        'task': 'backend.apps.core.tasks.limpeza_logs_antigos',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Domingo às 2:00
        'options': {
            'queue': 'maintenance',
            'priority': 2,
        },
    },
    
    # LIMPEZA DE CACHE todo domingo às 2:30
    'limpeza-cache': {
        'task': 'backend.apps.core.tasks.limpeza_cache',
        'schedule': crontab(hour=2, minute=30, day_of_week=0),  # Domingo às 2:30
        'options': {
            'queue': 'maintenance',
            'priority': 2,
        },
    },
}

# ================================================================
# CONFIGURAÇÕES DE FILAS E ROTEAMENTO
# ================================================================

# Definir filas de processamento
app.conf.task_routes = {
    # Checklists (alta prioridade)
    'backend.apps.core.tasks.gerar_checklists_automatico': {'queue': 'checklists'},
    'backend.apps.core.tasks.verificar_checklists_atrasados': {'queue': 'checklists'},
    'backend.apps.core.tasks.notificar_checklists_pendentes': {'queue': 'checklists'},
    
    # Notificações (alta prioridade)
    'backend.apps.bot_telegram.*': {'queue': 'notifications'},
    
    # Dashboard e KPIs
    'backend.apps.dashboard.*': {'queue': 'dashboard'},
    
    # QR Codes
    'backend.apps.nr12_checklist.qr_manager.*': {'queue': 'qrcodes'},
    
    # Almoxarifado
    'backend.apps.almoxarifado.*': {'queue': 'inventory'},
    
    # Financeiro
    'backend.apps.financeiro.*': {'queue': 'financial'},
    
    # Relatórios
    '*.gerar_relatorio_*': {'queue': 'reports'},
    
    # Alertas
    '*.verificar_alertas_*': {'queue': 'alerts'},
    
    # Backup
    '*.backup_*': {'queue': 'backup'},
    
    # Manutenção
    '*.limpar_*': {'queue': 'maintenance'},
    '*.limpeza_*': {'queue': 'maintenance'},
    
    # Monitoramento
    '*.monitoramento_*': {'queue': 'monitoring'},
    '*.health_check_*': {'queue': 'monitoring'},
}

# ================================================================
# CONFIGURAÇÕES DE RETRY E TIMEOUT
# ================================================================

app.conf.task_annotations = {
    # Tasks críticas de checklist
    'backend.apps.core.tasks.gerar_checklists_automatico': {
        'rate_limit': '1/m',
        'time_limit': 600,  # 10 minutos
        'soft_time_limit': 540,  # 9 minutos
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 60,  # 1 minuto
            'interval_max': 300,  # 5 minutos
        }
    },
    
    'backend.apps.core.tasks.verificar_checklists_atrasados': {
        'rate_limit': '1/m',
        'time_limit': 300,  # 5 minutos
        'retry_policy': {
            'max_retries': 2,
            'interval_start': 30,
            'interval_step': 30,
            'interval_max': 120,
        }
    },
    
    # Tasks de notificação
    'backend.apps.bot_telegram.*': {
        'rate_limit': '10/m',
        'time_limit': 120,  # 2 minutos
        'retry_policy': {
            'max_retries': 5,
            'interval_start': 10,
            'interval_step': 10,
            'interval_max': 60,
        }
    },
    
    # Tasks de backup
    'backend.apps.core.tasks.backup_dados_importantes': {
        'time_limit': 1800,  # 30 minutos
        'soft_time_limit': 1500,  # 25 minutos
        'retry_policy': {
            'max_retries': 2,
            'interval_start': 300,  # 5 minutos
            'interval_step': 300,
            'interval_max': 900,  # 15 minutos
        }
    },
    
    # Tasks de relatório
    '*.gerar_relatorio_*': {
        'time_limit': 900,  # 15 minutos
        'soft_time_limit': 720,  # 12 minutos
        'retry_policy': {
            'max_retries': 2,
            'interval_start': 60,
            'interval_step': 60,
            'interval_max': 180,
        }
    },
    
    # Tasks de monitoramento
    'backend.apps.core.tasks.health_check_sistema': {
        'time_limit': 60,  # 1 minuto
        'retry_policy': {
            'max_retries': 1,
            'interval_start': 10,
            'interval_step': 10,
            'interval_max': 30,
        }
    },
}

# ================================================================
# CONFIGURAÇÕES ADICIONAIS
# ================================================================

# Worker configuration
app.conf.worker_hijack_root_logger = False
app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Beat configuration
app.conf.beat_schedule_filename = 'celerybeat-schedule'

# Task result configuration
app.conf.result_expires = 3600  # 1 hora

# ================================================================
# TASK DE DEBUG
# ================================================================

@app.task(bind=True)
def debug_task(self):
    """Task de debug para testar funcionamento do Celery"""
    print(f'Request: {self.request!r}')
    return f'Debug task executada às {timezone.now()}'

# ================================================================
# CONFIGURAÇÃO DE LOGGING
# ================================================================

import logging
from celery.utils.log import get_task_logger

# Configurar logger para tasks
logger = get_task_logger(__name__)

@app.task
def test_logging():
    """Task para testar logging"""
    logger.info('✅ Task de teste executada com sucesso')
    return 'Logging funcionando'