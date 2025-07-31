#!/usr/bin/env python3
# =============================
# create_logs.py
# Script para criar estrutura de logs
# =============================

import os
from pathlib import Path

def create_logs_structure():
    """Cria a estrutura de diretórios e arquivos de log"""
    
    # Criar diretório de logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Criar arquivo .gitkeep para manter o diretório no git
    gitkeep_file = logs_dir / ".gitkeep"
    gitkeep_file.touch()
    
    print("✅ Estrutura de logs criada:")
    print(f"   📁 {logs_dir}")
    print(f"   📄 {gitkeep_file}")
    
    # Criar .gitignore para logs se não existir
    gitignore_content = """
# Logs
logs/*.log
logs/*.txt
!logs/.gitkeep
"""
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content.strip())
        print(f"   📄 {gitignore_file} criado")
    
    print("\n🚀 Estrutura pronta para uso!")

if __name__ == "__main__":
    create_logs_structure()
    # Carrega variáveis do .env
env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    # Tenta encontrar .env em locais alternativos
    alternative_paths = [
        Path(__file__).parent.parent / ".env",
        Path(".env"),
        Path(__file__).parent.parent.parent.parent / ".env"
    ]
    
    for alt_path in alternative_paths:
        if alt_path.exists():
            env_path = alt_path
            break
    else:
        print(f"⚠️ Arquivo .env não encontrado. Tentou em:")
        print(f"   • {Path(__file__).parent.parent.parent / '.env'}")
        for path in alternative_paths:
            print(f"   • {path}")
        print("\n📝 Copie .env.example para .env e configure as variáveis.")

load_dotenv(dotenv_path=env_path)