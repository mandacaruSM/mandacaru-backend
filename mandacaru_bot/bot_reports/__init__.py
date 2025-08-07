# ===============================================
# ARQUIVO: mandacaru_bot/bot_reports/__init__.py
# Módulo de Relatórios
# ===============================================

"""
Módulo de Relatórios - Bot Mandacaru

Este módulo fornece funcionalidades para visualização
de relatórios, históricos e estatísticas de checklists
e equipamentos.

Funcionalidades:
- Relatórios detalhados de checklists
- Histórico por equipamento
- Estatísticas de performance
- Tendências e análises
"""

__version__ = "1.0.0"
__author__ = "Mandacaru ERP"

from .handlers import register_handlers

__all__ = [
    'register_handlers'
]