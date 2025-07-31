#!/usr/bin/env python3
# =============================
# install_deps.py - Instalador de dependências
# =============================

import subprocess
import sys
from pathlib import Path

def install_package(package):
    """Instala um pacote via pip"""
    print(f"-> Instalando {package}...")
    try:
        cmd = [sys.executable, "-m", "pip", "install", package]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print(f"   [OK] {package} instalado com sucesso")
            return True
        else:
            print(f"   [ERRO] Falha ao instalar {package}")
            print(f"   Detalhes: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   [ERRO] Exceção ao instalar {package}: {e}")
        return False

def upgrade_pip():
    """Atualiza o pip"""
    print("-> Atualizando pip...")
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   [OK] pip atualizado")
            return True
        else:
            print("   [AVISO] Não foi possível atualizar o pip")
            return False
    except Exception as e:
        print(f"   [AVISO] Erro ao atualizar pip: {e}")
        return False

def main():
    print("="*60)
    print("     INSTALADOR DE DEPENDENCIAS - BOT MANDACARU")
    print("="*60)
    
    # Listar pacotes necessários
    packages = [
        "aiogram==3.4.1",
        "httpx==0.26.0", 
        "python-dotenv==1.0.0",
        "psutil==5.9.8"
    ]
    
    print(f"\nPacotes a serem instalados:")
    for package in packages:
        print(f"  * {package}")
    
    print(f"\nUsando Python: {sys.executable}")
    print(f"Versão: {sys.version}")
    
    input("\nPressione ENTER para continuar...")
    
    # Atualizar pip primeiro
    upgrade_pip()
    
    # Instalar cada pacote
    print(f"\n-> Instalando {len(packages)} pacotes...")
    
    success_count = 0
    failed_packages = []
    
    for package in packages:
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
    
    # Resultado final
    print("\n" + "="*60)
    print("RESULTADO DA INSTALAÇÃO")
    print("="*60)
    
    print(f"Sucesso: {success_count}/{len(packages)} pacotes")
    
    if failed_packages:
        print(f"\nPacotes que falharam:")
        for package in failed_packages:
            print(f"  * {package}")
        
        print(f"\nTente instalar manualmente:")
        for package in failed_packages:
            print(f"  pip install {package}")
    else:
        print("\n[SUCESSO] Todos os pacotes foram instalados!")
        
        # Verificar se funcionou
        print("\n-> Testando imports...")
        
        import_tests = [
            ("aiogram", "from aiogram import Bot"),
            ("httpx", "import httpx"),
            ("dotenv", "from dotenv import load_dotenv"),
            ("psutil", "import psutil")
        ]
        
        for name, import_cmd in import_tests:
            try:
                exec(import_cmd)
                print(f"   [OK] {name}")
            except ImportError:
                print(f"   [ERRO] {name} - import falhou")
        
        print("\n[PRONTO] Agora você pode executar:")
        print("  python start.py")
        print("\nOu fazer diagnóstico:")
        print("  python diagnose_windows.py")

if __name__ == "__main__":
    main()