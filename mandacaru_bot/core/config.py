# ===============================================
# ARQUIVO: mandacaru_bot/core/config.py
# Configuração centralizada do bot
# ===============================================

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# ===============================================
# CONFIGURAÇÕES PRINCIPAIS
# ===============================================

# Bot Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN não configurado no arquivo .env")

# API Django
API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

# Administradores
ADMIN_IDS = [
    int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') 
    if x.strip().isdigit()
]

# ===============================================
# CONFIGURAÇÕES DE SESSÃO
# ===============================================

SESSION_TIMEOUT_HOURS = int(os.getenv('SESSION_TIMEOUT_HOURS', '24'))
CLEANUP_INTERVAL_MINUTES = int(os.getenv('CLEANUP_INTERVAL_MINUTES', '60'))

# ===============================================
# CONFIGURAÇÕES DE INTERFACE
# ===============================================

ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', '10'))
MAX_MESSAGE_LENGTH = 4000

# ===============================================
# CONFIGURAÇÕES DE LOGGING
# ===============================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '3'))

# ===============================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ===============================================

DEBUG = os.getenv('BOT_DEBUG', 'False').lower() == 'true'

# ===============================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# ===============================================

def validar_configuracao():
    """Valida se todas as configurações obrigatórias estão presentes"""
    erros = []
    
    if not TELEGRAM_TOKEN:
        erros.append("TELEGRAM_BOT_TOKEN não configurado")
    
    if not API_BASE_URL:
        erros.append("API_BASE_URL não configurado")
    
    if not ADMIN_IDS:
        erros.append("ADMIN_IDS não configurado")
    
    if erros:
        raise ValueError(f"❌ Configuração inválida:\n" + "\n".join(f"  • {erro}" for erro in erros))
    
    return True

# ===============================================
# CONFIGURAÇÃO DE PATHS
# ===============================================

# Diretório base do bot
BOT_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BOT_DIR.parent

# Diretórios de trabalho
LOGS_DIR = BOT_DIR / "logs"
TEMP_DIR = BOT_DIR / "temp"

# Criar diretórios se não existirem
LOGS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# ===============================================
# VALIDAR CONFIGURAÇÃO NO IMPORT
# ===============================================

try:
    validar_configuracao()
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        print("🔧 Configuração do bot carregada em modo DEBUG")
except Exception as e:
    print(f"❌ Erro na configuração: {e}")
    raise