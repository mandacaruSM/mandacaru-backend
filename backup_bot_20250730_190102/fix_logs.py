#!/usr/bin/env python3
# =============================
# fix_logs.py - Corrigir estrutura de logs
# =============================

import os
from pathlib import Path

def fix_logs_structure():
    """Corrige a estrutura de logs"""
    print("Corrigindo estrutura de logs...")
    
    # Criar diretório logs se não existir
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Diretório {logs_dir} criado/verificado")
    
    # Criar arquivo de log vazio se não existir
    log_file = logs_dir / "bot.log"
    log_file.touch()
    print(f"✅ Arquivo {log_file} criado/verificado")
    
    # Criar .gitkeep
    gitkeep = logs_dir / ".gitkeep"
    gitkeep.touch()
    print(f"✅ Arquivo {gitkeep} criado")
    
    print("\n✅ Estrutura de logs corrigida!")
    print(f"📁 Diretório: {logs_dir.absolute()}")
    print(f"📄 Log: {log_file.absolute()}")

if __name__ == "__main__":
    fix_logs_structure()