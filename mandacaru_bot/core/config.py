# ================================
# core/config.py (com URL da API)
# ================================

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="D:/projeto/mandacaru_erp/.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN não encontrado. Verifique o caminho no load_dotenv().")
