# ================================================================
# ATUALIZAR backend/settings.py - ADICIONAR dashboard
# ================================================================

from pathlib import Path
from decouple import config
import os
import dj_database_url
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Terceiros
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',

    # Apps internos - personalizados do seu projeto
    'backend.apps.auth_cliente',
    #'backend.apps.bot_telegram',
    'backend.apps.shared',
    'backend.apps.cliente_portal',
    'backend.apps.clientes',
    'backend.apps.dashboard',
    'backend.apps.equipamentos',
    'backend.apps.empreendimentos',
    'backend.apps.financeiro',
    'backend.apps.fornecedor',
    'backend.apps.manutencao',
    'backend.apps.nr12_checklist',
    'backend.apps.operadores',
    'backend.apps.ordens_servico',
    'backend.apps.orcamentos',
    'backend.apps.almoxarifado',
    'backend.apps.abastecimento',
    'backend.apps.relatorios',
    'backend.apps.core',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ✅ Configuração do Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

ROOT_URLCONF = 'backend.urls'

# ✅ Usar o modelo customizado de usuário
AUTH_USER_MODEL = 'auth_cliente.UsuarioCliente'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        BASE_DIR / 'backend/apps/templates',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mandacaru_erp',
        'USER': 'postgres',
        'PASSWORD': 'mandacaru',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://mandacaru-frontend-ovld.onrender.com",
]

# Upload de arquivos
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ✅ Configurações do Telegram Bot
TELEGRAM_BOT_USERNAME = config('TELEGRAM_BOT_USERNAME', default='Mandacarusmbot')
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_WEBHOOK_URL = config('TELEGRAM_WEBHOOK_URL', default='')
TELEGRAM_BOT_URL = 'https://t.me/Mandacarusmbot'
BASE_URL = 'http://localhost:8000'  # ou sua URL de produção

# ✅ Configurações do Celery (opcionais por enquanto)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Adicionar ao settings.py:

# Configurações de QR Code
QR_LOGO_PATH = os.path.join(BASE_DIR, 'static', 'img', 'logo.png')
QR_DEFAULT_SIZE = 'medium'
QR_INCLUDE_LOGO = True


# Criar diretório de QR codes
QR_CODES_DIR = os.path.join(MEDIA_ROOT, 'qr_codes')
QR_LOGO_PATH = os.path.join(BASE_DIR, 'static', 'img', 'logo.png')  # se tiver logo
QR_DEFAULT_SIZE = 'medium'
QR_INCLUDE_LOGO = True
BASE_URL = 'http://localhost:8000'  # ou sua URL de produção

# ✅ ADICIONE ESTAS LINHAS NO FINAL DO ARQUIVO

# Configurações do Bot Telegram (novas/atualizadas)
API_BASE_URL = 'http://127.0.0.1:8000/api'
BOT_DEBUG = config('BOT_DEBUG', default=True, cast=bool)
SESSION_TIMEOUT_HOURS = config('SESSION_TIMEOUT_HOURS', default=24, cast=int)
ADMIN_IDS = config('ADMIN_IDS', default='').split(',') if config('ADMIN_IDS', default='') else []

# Para leitura de QR Code
QR_CODE_ENABLED = True
QR_CODE_SIZE = (300, 300)

CELERY_BEAT_SCHEDULE = {
    'checklists_diarios_6h': {
        'task': 'backend.apps.core.tasks.gerar_checklists_automatico',  # ✅ EXISTE
        'schedule': crontab(hour=6, minute=0),
    },
    'checklists_semanais_segunda_6h': {
        'task': 'backend.apps.core.tasks.gerar_checklists_automatico',  # ✅ EXISTE
        'schedule': crontab(hour=6, minute=0, day_of_week=1),  # 1 = segunda
    },
    'checklists_mensais_1_6h': {
        'task': 'backend.apps.core.tasks.gerar_checklists_automatico',  # ✅ EXISTE
        'schedule': crontab(hour=6, minute=0, day_of_month=1),
    },
}
# ================================================================
# CONFIGURAÇÕES CELERY (adicionar no final do arquivo)
# ================================================================

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Configurações básicas
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_ENABLE_UTC = True

# Configurações para Windows
CELERY_WORKER_POOL = 'threads'
CELERY_WORKER_CONCURRENCY = 1
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True