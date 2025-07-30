# ===============================================
# DIAGNÓSTICO SIMPLES - PASSO A PASSO
# CRIAR: diagnostico.py (na raiz do projeto)
# ===============================================

import os
import sys
from pathlib import Path

def check_basic():
    """Verificação básica de arquivos e estrutura"""
    print("🔍 DIAGNÓSTICO MANDACARU BOT")
    print("=" * 50)
    
    # 1. Verificar diretório atual
    current_dir = Path.cwd()
    print(f"📁 Diretório atual: {current_dir}")
    
    # 2. Verificar se estamos no lugar certo
    manage_py = current_dir / "manage.py"
    print(f"✅ manage.py existe: {manage_py.exists()}")
    
    # 3. Verificar .env
    env_file = current_dir / ".env"
    print(f"✅ .env existe: {env_file.exists()}")
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                has_bot_token = 'TELEGRAM_BOT_TOKEN' in content
                has_api_url = 'API_BASE_URL' in content
                print(f"✅ TELEGRAM_BOT_TOKEN configurado: {has_bot_token}")
                print(f"✅ API_BASE_URL configurado: {has_api_url}")
        except Exception as e:
            print(f"❌ Erro ao ler .env: {e}")
    
    # 4. Verificar estrutura do bot
    bot_dir = current_dir / "mandacaru_bot"
    print(f"✅ mandacaru_bot/ existe: {bot_dir.exists()}")
    
    if bot_dir.exists():
        core_dir = bot_dir / "core"
        main_dir = bot_dir / "bot_main"
        print(f"✅ mandacaru_bot/core/ existe: {core_dir.exists()}")
        print(f"✅ mandacaru_bot/bot_main/ existe: {main_dir.exists()}")
    
    # 5. Verificar backend
    backend_dir = current_dir / "backend"
    print(f"✅ backend/ existe: {backend_dir.exists()}")
    
    # 6. Tentar imports básicos
    print("\n🐍 TESTANDO IMPORTS...")
    try:
        # Django setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        import django
        django.setup()
        print("✅ Django setup: OK")
        
        # Testar modelos
        from backend.apps.operadores.models import Operador
        from backend.apps.equipamentos.models import Equipamento
        print("✅ Imports modelos: OK")
        
        # Contar registros
        op_count = Operador.objects.count()
        eq_count = Equipamento.objects.count()
        print(f"📊 Operadores: {op_count}")
        print(f"📊 Equipamentos: {eq_count}")
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
    
    # 7. Verificar se servidor Django está rodando
    print("\n🌐 TESTANDO CONEXÃO API...")
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/", timeout=3)
        print(f"✅ API responde: {response.status_code}")
    except Exception as e:
        print(f"❌ API não responde: {e}")
        print("💡 Execute: python manage.py runserver")

if __name__ == "__main__":
    check_basic()
    print("\n" + "=" * 50)
    print("🎯 PRÓXIMO PASSO:")
    print("1. Se tudo OK: Implementar QR Code")
    print("2. Se erro: Corrigir problemas listados")
    print("3. Executar: python manage.py runserver (em outro terminal)")