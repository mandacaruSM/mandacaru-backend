# =============================
# 7. SCRIPT DE CONFIGURAÇÃO INICIAL
# Salve como: setup_bot_integration.py na raiz do projeto
# =============================

#!/usr/bin/env python3
"""
Script para configurar integração do Bot Telegram com Django
Execute: python setup_bot_integration.py
"""

import os
import sys
from pathlib import Path
import shutil

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🤖 SETUP INTEGRAÇÃO BOT MANDACARU             ║
║                                                              ║
║  Este script irá configurar a integração do bot Telegram    ║
║  com o sistema Django Mandacaru                             ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_django_project():
    """Verifica se é um projeto Django"""
    manage_py = Path("manage.py")
    if not manage_py.exists():
        print("❌ Arquivo manage.py não encontrado!")
        print("   Execute este script na raiz do projeto Django")
        return False
    
    print("✅ Projeto Django detectado")
    return True

def check_bot_location():
    """Verifica localização do bot"""
    bot_locations = [
        Path("mandacaru_bot"),
        Path("backend/mandacaru_bot"), 
        Path("../mandacaru_bot")
    ]
    
    for location in bot_locations:
        if location.exists():
            print(f"✅ Bot encontrado em: {location}")
            return location
    
    print("❌ Pasta mandacaru_bot não encontrada!")
    print("   Locais verificados:")
    for loc in bot_locations:
        print(f"   • {loc}")
    return None

def move_bot_to_correct_location(current_location):
    """Move bot para localização correta"""
    if current_location == Path("mandacaru_bot"):
        print("✅ Bot já está na localização correta")
        return True
    
    target = Path("mandacaru_bot")
    if target.exists():
        print("⚠️ Pasta mandacaru_bot já existe na raiz")
        response = input("Deseja substituir? (s/N): ")
        if response.lower() != 's':
            return False
        shutil.rmtree(target)
    
    try:
        shutil.move(str(current_location), str(target))
        print(f"✅ Bot movido de {current_location} para {target}")
        return True
    except Exception as e:
        print(f"❌ Erro ao mover bot: {e}")
        return False

def create_bot_views():
    """Cria arquivos de views para o bot"""
    files_to_create = {
        "backend/apps/operadores/views_bot.py": '''# Views específicas para bot Telegram
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Operador

@csrf_exempt
def operador_login_bot(request):
    """Login para bot telegram"""
    # Implementação básica - expandir conforme necessário
    return JsonResponse({"message": "Bot login endpoint"})
''',
        "backend/apps/operadores/urls_bot.py": '''# URLs específicas para bot
from django.urls import path
from . import views_bot

urlpatterns = [
    path('operador/login/', views_bot.operador_login_bot, name='operador_login_bot'),
]
''',
    }
    
    for file_path, content in files_to_create.items():
        path = Path(file_path)
        
        # Criar diretórios se não existem
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.exists():
            print(f"⚠️ Arquivo já existe: {file_path}")
            continue
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Criado: {file_path}")
        except Exception as e:
            print(f"❌ Erro ao criar {file_path}: {e}")

def update_main_urls():
    """Atualiza URLs principais"""
    urls_patterns = [
        "backend/urls.py",
        "backend/config/urls.py", 
        "config/urls.py"
    ]
    
    urls_file = None
    for pattern in urls_patterns:
        if Path(pattern).exists():
            urls_file = Path(pattern)
            break
    
    if not urls_file:
        print("❌ Arquivo de URLs principais não encontrado")
        print("   Configure manualmente as URLs do bot")
        return
    
    # Ler arquivo atual
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem configuração do bot
        if 'urls_bot' in content:
            print("✅ URLs do bot já configuradas")
            return
        
        # Adicionar URLs do bot
        if "path('bot/" not in content:
            # Encontrar onde adicionar
            if 'urlpatterns = [' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'urlpatterns = [' in line:
                        # Adicionar após a linha
                        lines.insert(i + 1, "    # URLs para Bot Telegram")
                        lines.insert(i + 2, "    path('bot/', include('backend.apps.operadores.urls_bot')),")
                        break
                
                new_content = '\n'.join(lines)
                
                # Backup do arquivo original
                backup_file = urls_file.with_suffix('.py.backup')
                shutil.copy2(urls_file, backup_file)
                print(f"📄 Backup criado: {backup_file}")
                
                # Escrever novo conteúdo
                with open(urls_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ URLs do bot adicionadas em: {urls_file}")
            else:
                print("⚠️ Não foi possível adicionar URLs automaticamente")
                print("   Adicione manualmente: path('bot/', include('backend.apps.operadores.urls_bot')),")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar URLs: {e}")

def create_management_command():
    """Cria comando de management para o bot"""
    command_dir = Path("backend/apps/core/management/commands")
    command_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar __init__.py se não existir
    for init_dir in [Path("backend/apps/core/management"), command_dir]:
        init_file = init_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    command_file = command_dir / "run_telegram_bot.py"
    
    if command_file.exists():
        print("✅ Comando management já existe")
        return
    
    command_content = '''import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Executa o bot do Telegram'

    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help='Modo debug')

    def handle(self, *args, **options):
        bot_path = os.path.join(settings.BASE_DIR, 'mandacaru_bot')
        
        if not os.path.exists(bot_path):
            self.stdout.write(self.style.ERROR(f'Bot não encontrado em: {bot_path}'))
            return
        
        sys.path.insert(0, bot_path)
        
        try:
            from start import main
            import asyncio
            self.stdout.write(self.style.SUCCESS('🤖 Iniciando bot...'))
            asyncio.run(main())
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Erro de import: {e}'))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Bot interrompido'))
'''
    
    try:
        with open(command_file, 'w', encoding='utf-8') as f:
            f.write(command_content)
        print(f"✅ Comando management criado: {command_file}")
    except Exception as e:
        print(f"❌ Erro ao criar comando: {e}")

def check_env_configuration():
    """Verifica configuração do .env"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️ Arquivo .env não encontrado")
        print("   Copie .env.example para .env e configure as variáveis")
        return
    
    # Verificar variáveis essenciais do bot
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'API_BASE_URL', 
        'ADMIN_IDS'
    ]
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print("⚠️ Variáveis faltantes no .env:")
            for var in missing_vars:
                print(f"   • {var}")
            
            # Adicionar variáveis faltantes
            with open(env_file, 'a', encoding='utf-8') as f:
                f.write("\n# Configurações do Bot Telegram\n")
                for var in missing_vars:
                    if var == 'TELEGRAM_BOT_TOKEN':
                        f.write(f"{var}=seu_token_aqui\n")
                    elif var == 'API_BASE_URL':
                        f.write(f"{var}=http://127.0.0.1:8000/api\n")
                    elif var == 'ADMIN_IDS':
                        f.write(f"{var}=123456789,987654321\n")
            
            print("✅ Variáveis adicionadas ao .env - configure os valores")
        else:
            print("✅ Variáveis do bot configuradas no .env")
    
    except Exception as e:
        print(f"❌ Erro ao verificar .env: {e}")

def run_setup():
    """Executa setup completo"""
    print_banner()
    
    # 1. Verificar projeto Django
    if not check_django_project():
        return
    
    # 2. Verificar localização do bot
    bot_location = check_bot_location()
    if not bot_location:
        print("\n❌ Setup interrompido - bot não encontrado")
        return
    
    # 3. Mover bot se necessário
    if not move_bot_to_correct_location(bot_location):
        print("\n❌ Setup interrompido - erro ao mover bot")
        return
    
    # 4. Criar arquivos de integração
    print("\n📝 Criando arquivos de integração...")
    create_bot_views()
    
    # 5. Atualizar URLs principais
    print("\n🌐 Configurando URLs...")
    update_main_urls()
    
    # 6. Criar comando management
    print("\n⚙️ Criando comando management...")
    create_management_command()
    
    # 7. Verificar configuração .env
    print("\n🔧 Verificando configuração...")
    check_env_configuration()
    
    # 8. Instruções finais
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ SETUP CONCLUÍDO!                       ║
╚══════════════════════════════════════════════════════════════╝

🎯 PRÓXIMOS PASSOS:

1. 🔑 Configure o .env com seu token do bot:
   • Obtenha token no @BotFather
   • Configure seu ID de admin (@userinfobot)

2. 📦 Instale dependências do bot:
   pip install aiogram httpx python-dotenv psutil

3. 🗄️ Execute migrações (se necessário):
   python manage.py makemigrations
   python manage.py migrate

4. 🚀 Teste a integração:
   python manage.py run_telegram_bot --debug

5. 🌐 Inicie o Django em outro terminal:
   python manage.py runserver

6. 📱 Teste o bot no Telegram!

🐛 TROUBLESHOOTING:
   • Logs do bot: mandacaru_bot/logs/
   • Execute diagnóstico: python mandacaru_bot/diagnose.py
   • Verifique URLs: curl http://127.0.0.1:8000/bot/operador/login/

""")

if __name__ == "__main__":
    run_setup()