# ================================================================
# ARQUIVO: backend/settings_production.py
# Configurações específicas para produção
# ================================================================

from .settings import *
import dj_database_url
from decouple import config

# ================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ================================================================

# Sempre usar HTTPS em produção
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# ================================================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ================================================================

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Pool de conexões para PostgreSQL
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'OPTIONS': {
        'MAX_CONNS': 20,
        'sslmode': 'require',
    }
}

# ================================================================
# CONFIGURAÇÕES DE CACHE
# ================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'TIMEOUT': 300,  # 5 minutos
        'KEY_PREFIX': 'mandacaru_prod',
    }
}

# Session engine usando Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ================================================================
# CONFIGURAÇÕES DE EMAIL
# ================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@mandacaru.com')

# Lista de emails para relatórios
RELATORIO_EMAIL_DESTINATARIOS = config(
    'RELATORIO_EMAIL_DESTINATARIOS', 
    default='admin@mandacaru.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# ================================================================
# CONFIGURAÇÕES DE ARQUIVOS ESTÁTICOS E MÍDIA
# ================================================================

# AWS S3 para arquivos estáticos e mídia (opcional)
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # Configurações do S3
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    
    # Storage backends
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    
    # URLs
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    
    # Configurações de cache
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
else:
    # Usar storage local com WhiteNoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================================================
# CONFIGURAÇÕES DE LOGGING
# ================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/mandacaru.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'backend': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ================================================================
# CONFIGURAÇÕES DO CELERY PARA PRODUÇÃO
# ================================================================

CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')

# Configurações otimizadas para produção
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_ENABLE_UTC = True

# Worker configurações
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Configurações de retry
CELERY_TASK_RETRY_DELAY = 60  # 1 minuto
CELERY_TASK_MAX_RETRIES = 3

# Beat schedule otimizado para produção
CELERY_BEAT_SCHEDULE = {
    # KPIs diários às 6h
    'calcular-kpis-diarios': {
        'task': 'backend.apps.core.tasks.calcular_kpis_diarios',
        'schedule': crontab(hour=6, minute=0),
    },
    
    # Gerar checklists às 5h
    'gerar-checklists-diarios': {
        'task': 'backend.apps.core.tasks.gerar_checklists_diarios',
        'schedule': crontab(hour=5, minute=0),
    },
    
    # Verificar alertas a cada hora
    'verificar-alertas-manutencao': {
        'task': 'backend.apps.core.tasks.verificar_alertas_manutencao',
        'schedule': crontab(minute=0),
    },
    
    # Verificar checklists atrasados a cada 2 horas
    'notificar-checklists-atrasados': {
        'task': 'backend.apps.bot_telegram.notifications.notificar_checklists_atrasados',
        'schedule': crontab(minute=0, hour='8-18/2'),  # Das 8h às 18h, a cada 2h
    },
    
    # Verificar contas vencidas diariamente às 9h
    'verificar-contas-vencidas': {
        'task': 'backend.apps.core.tasks.verificar_contas_vencidas',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Verificar estoque baixo diariamente às 10h
    'verificar-estoque-baixo': {
        'task': 'backend.apps.core.tasks.verificar_estoque_baixo',
        'schedule': crontab(hour=10, minute=0),
    },
    
    # Resumo diário às 18h
    'enviar-resumo-diario': {
        'task': 'backend.apps.bot_telegram.notifications.enviar_resumo_diario_task',
        'schedule': crontab(hour=18, minute=0),
    },
    
    # Backup diário às 2h
    'backup-dados-importantes': {
        'task': 'backend.apps.core.tasks.backup_dados_importantes',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Limpeza semanal aos domingos às 3h
    'limpeza-dados-antigos': {
        'task': 'backend.apps.core.tasks.limpeza_dados_antigos',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Domingo
    },
    
    # Monitoramento do sistema a cada 30 minutos
    'monitoramento-sistema': {
        'task': 'backend.apps.core.tasks.monitoramento_sistema',
        'schedule': crontab(minute='*/30'),
    },
}

# ================================================================
# CONFIGURAÇÕES DE MONITORAMENTO
# ================================================================

# Sentry para monitoramento de erros
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% das transações
        send_default_pii=False,
        environment='production',
        release=config('APP_VERSION', default='1.0.0'),
    )

# ================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ================================================================

# Database connection pooling
DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# ================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO MANDACARU
# ================================================================

# URL base para QR codes e links
BASE_URL = config('BASE_URL', default='https://mandacaru-erp.com')

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_WEBHOOK_URL = config('TELEGRAM_WEBHOOK_URL', default='')

# Configurações de backup
BACKUP_RETENTION_DAYS = config('BACKUP_RETENTION_DAYS', default=30, cast=int)
BACKUP_S3_BUCKET = config('BACKUP_S3_BUCKET', default='')

# Configurações de relatórios
RELATORIO_LOGO_URL = config('RELATORIO_LOGO_URL', default='')
EMPRESA_NOME = config('EMPRESA_NOME', default='Mandacaru ERP')
EMPRESA_ENDERECO = config('EMPRESA_ENDERECO', default='')
EMPRESA_TELEFONE = config('EMPRESA_TELEFONE', default='')

# Configurações NR12
NR12_FREQUENCIA_PADRAO = config('NR12_FREQUENCIA_PADRAO', default='DIARIO')
NR12_NOTIFICAR_ATRASOS = config('NR12_NOTIFICAR_ATRASOS', default=True, cast=bool)
NR12_TEMPO_LIMITE_CHECKLIST = config('NR12_TEMPO_LIMITE_CHECKLIST', default=120, cast=int)  # minutos

# Configurações financeiras
MOEDA_PADRAO = config('MOEDA_PADRAO', default='BRL')
TARIFA_DESLOCAMENTO_KM = config('TARIFA_DESLOCAMENTO_KM', default=2.50, cast=float)
JUROS_MORA_DIARIO = config('JUROS_MORA_DIARIO', default=0.033, cast=float)  # 1% ao mês

# ================================================================
# CONFIGURAÇÕES DE CORS PARA PRODUÇÃO
# ================================================================

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://mandacaru-frontend.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

CORS_ALLOW_CREDENTIALS = True

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ================================================================
# CONFIGURAÇÕES DE API RATE LIMITING
# ================================================================

REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
})

# ================================================================
# CONFIGURAÇÕES ADICIONAIS DE SEGURANÇA
# ================================================================

# Allowed hosts específicos
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='mandacaru-erp.com,www.mandacaru-erp.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Admin URL personalizada para segurança
ADMIN_URL = config('ADMIN_URL', default='admin/')

# ================================================================
# MIDDLEWARE ADICIONAL PARA PRODUÇÃO
# ================================================================

MIDDLEWARE.insert(1, 'django.middleware.cache.UpdateCacheMiddleware')
MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# Middleware de rate limiting
MIDDLEWARE.insert(-1, 'ratelimit.middleware.RatelimitMiddleware')

# ================================================================
# CONFIGURAÇÕES DE INTERNACIONALIZAÇÃO
# ================================================================

# Timezone brasileiro
USE_TZ = True
TIME_ZONE = 'America/Sao_Paulo'

# Formato de data/hora brasileiro
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Configurações de localização
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','

# ================================================================
# CONFIGURAÇÕES DE HEALTH CHECK
# ================================================================

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # Máximo 90% de uso do disco
    'MEMORY_MIN': 100 * 1024 * 1024,  # Mínimo 100MB de RAM livre
}

# URLs para health check
HEALTH_CHECK_URLS = [
    'health/',
    'health/ready/',
    'health/live/',
]

# ================================================================
# CONFIGURAÇÕES DE BACKUP AUTOMÁTICO
# ================================================================

BACKUP_SETTINGS = {
    'ENABLED': config('BACKUP_ENABLED', default=True, cast=bool),
    'SCHEDULE': '0 2 * * *',  # Diariamente às 2h
    'RETENTION_DAYS': config('BACKUP_RETENTION_DAYS', default=30, cast=int),
    'COMPRESS': True,
    'INCLUDE_MEDIA': config('BACKUP_INCLUDE_MEDIA', default=True, cast=bool),
    'S3_BUCKET': config('BACKUP_S3_BUCKET', default=''),
    'NOTIFICATION_EMAIL': config('BACKUP_NOTIFICATION_EMAIL', default=''),
}

# ================================================================
# CONFIGURAÇÕES DE MÉTRICAS E MONITORING
# ================================================================

# Prometheus metrics (opcional)
PROMETHEUS_METRICS_EXPORT_PORT = config('PROMETHEUS_PORT', default=None, cast=int)

if PROMETHEUS_METRICS_EXPORT_PORT:
    INSTALLED_APPS.append('django_prometheus')
    MIDDLEWARE.insert(0, 'django_prometheus.middleware.PrometheusBeforeMiddleware')
    MIDDLEWARE.append('django_prometheus.middleware.PrometheusAfterMiddleware')

# ================================================================
# CONFIGURAÇÕES DE OTIMIZAÇÃO DE QUERIES
# ================================================================

# Configurações do ORM
DATABASES['default']['OPTIONS'].update({
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
    'autocommit': True,
})

# Debug toolbar desabilitado em produção
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# ================================================================
# CONFIGURAÇÕES FINAIS
# ================================================================

# Validação de configurações críticas
def validate_production_settings():
    """Valida configurações críticas para produção"""
    errors = []
    
    if DEBUG:
        errors.append("DEBUG deve ser False em produção")
    
    if SECRET_KEY == 'unsafe-secret-key':
        errors.append("SECRET_KEY deve ser alterada em produção")
    
    if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['*']:
        errors.append("ALLOWED_HOSTS deve ser configurado corretamente")
    
    if not config('DATABASE_URL', default=''):
        errors.append("DATABASE_URL deve ser configurada")
    
    if errors:
        raise ImproperlyConfigured(
            "Configurações de produção inválidas:\n" + "\n".join(f"- {error}" for error in errors)
        )

# Executar validação
from django.core.exceptions import ImproperlyConfigured
validate_production_settings()

# ================================================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO LOCAL (sobrescrever se necessário)
# ================================================================

if config('ENVIRONMENT', default='production') == 'development':
    DEBUG = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
    # Usar console para emails em desenvolvimento
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
    # Logging simplificado
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    LOGGING['loggers']['backend']['level'] = 'DEBUG'