# ===============================================
# ARQUIVO: mandacaru_bot/bot_qr/__init__.py
# Módulo de QR Codes
# ===============================================

"""
Módulo de QR Codes - Bot Mandacaru

Este módulo processa QR Codes de equipamentos e checklists,
fornecendo acesso rápido às funcionalidades através de
códigos escaneados.

Funcionalidades:
- Processamento de QR Codes de equipamentos
- Acesso direto a checklists
- Validação de UUIDs
- Menu contextual por equipamento
"""

__version__ = "1.0.0"
__author__ = "Mandacaru ERP"

from .handlers import register_handlers, processar_qr_code_start

__all__ = [
    'register_handlers',
    'processar_qr_code_start'
]