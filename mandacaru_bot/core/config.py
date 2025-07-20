# ================================
# core/config.py (melhorado)
# ================================

import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis do .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configurações do Telegram - usando as variáveis existentes do Django
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN não encontrado no arquivo .env")

# Configurações da API - baseado no BASE_URL do Django
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_BASE_URL = os.getenv("API_BASE_URL", f"{BASE_URL}/api")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

# Configurações do banco de dados (reutilizando do Django)
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurações de logging do bot
LOG_LEVEL = os.getenv("BOT_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO"))
LOG_FILE = os.getenv("BOT_LOG_FILE", "logs/bot.log")

# Configurações de sessão
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
CLEANUP_INTERVAL_MINUTES = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "60"))

# Configurações de paginação
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))
MAX_ITEMS_PER_PAGE = int(os.getenv("MAX_ITEMS_PER_PAGE", "50"))

# Configurações de segurança
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))
LOGIN_TIMEOUT_MINUTES = int(os.getenv("LOGIN_TIMEOUT_MINUTES", "15"))

# IDs de administradores (separados por vírgula)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip().isdigit()]

# Configurações de desenvolvimento - usando variáveis do Django
DEBUG = os.getenv("BOT_DEBUG", os.getenv("DEBUG", "False")).lower() in ("true", "1", "yes")
ENVIRONMENT = os.getenv("BOT_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))

# Webhook para produção
WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL", os.getenv("TELEGRAM_WEBHOOK_URL"))

# Configurações específicas do Mandacaru
EMPRESA_NOME = os.getenv("EMPRESA_NOME", "Mandacaru ERP")
EMPRESA_TELEFONE = os.getenv("EMPRESA_TELEFONE", "(11) 99999-9999")

# Configurações NR12
NR12_TEMPO_LIMITE_CHECKLIST = int(os.getenv("NR12_TEMPO_LIMITE_CHECKLIST", "120"))
NR12_FREQUENCIA_PADRAO = os.getenv("NR12_FREQUENCIA_PADRAO", "DIARIO")
NR12_NOTIFICAR_ATRASOS = os.getenv("NR12_NOTIFICAR_ATRASOS", "True").lower() in ("true", "1", "yes")

# Validações
def validar_configuracoes():
    """Valida se todas as configurações necessárias estão presentes"""
    erros = []
    
    if not TELEGRAM_TOKEN:
        erros.append("TELEGRAM_BOT_TOKEN é obrigatório")
    
    if not API_BASE_URL:
        erros.append("API_BASE_URL é obrigatório")
    
    if API_TIMEOUT <= 0:
        erros.append("API_TIMEOUT deve ser maior que 0")
    
    if SESSION_TIMEOUT_HOURS <= 0:
        erros.append("SESSION_TIMEOUT_HOURS deve ser maior que 0")
    
    if erros:
        raise ValueError(f"Erros de configuração: {', '.join(erros)}")

# Executar validação na importação
validar_configuracoes()

# Configurações por ambiente
class Config:
    """Classe base de configuração"""
    TELEGRAM_TOKEN = TELEGRAM_TOKEN
    API_BASE_URL = API_BASE_URL
    API_TIMEOUT = API_TIMEOUT
    DEBUG = DEBUG
    EMPRESA_NOME = EMPRESA_NOME
    EMPRESA_TELEFONE = EMPRESA_TELEFONE

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    LOG_LEVEL = "INFO"

# Selecionar configuração baseada no ambiente
if ENVIRONMENT.lower() == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()

# Exportar configuração ativa
__all__ = [
    "TELEGRAM_TOKEN", "API_BASE_URL", "API_TIMEOUT",
    "SESSION_TIMEOUT_HOURS", "CLEANUP_INTERVAL_MINUTES",
    "ITEMS_PER_PAGE", "MAX_ITEMS_PER_PAGE",
    "MAX_LOGIN_ATTEMPTS", "LOGIN_TIMEOUT_MINUTES",
    "ADMIN_IDS", "DEBUG", "LOG_LEVEL", "LOG_FILE",
    "EMPRESA_NOME", "EMPRESA_TELEFONE",
    "NR12_TEMPO_LIMITE_CHECKLIST", "NR12_FREQUENCIA_PADRAO", "NR12_NOTIFICAR_ATRASOS",
    "config"
]