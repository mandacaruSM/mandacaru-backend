#!/usr/bin/env python3
# scripts/verificar_bot.py

import os
import sys

# Adicionar o diretório raiz ao Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, TipoEquipamentoNR12

print("\n🔍 Verificando sistema para Bot...\n")

# 1. Verificar operadores
print("📋 OPERADORES:")
try:
    operadores_total = Operador.objects.count()
    operadores_ativos = Operador.objects.filter(status='ATIVO').count()
    operadores_bot = Operador.objects.filter(ativo_bot=True).count()
    operadores_com_chat = Operador.objects.exclude(chat_id_telegram__isnull=True).exclude(chat_id_telegram='').count()
    
    print(f"  - Total cadastrados: {operadores_total}")
    print(f"  - Ativos: {operadores_ativos}")
    print(f"  - Ativos para bot: {operadores_bot}")
    print(f"  - Com chat_id: {operadores_com_chat}")
    
    # Verificar métodos do bot
    metodos_necessarios = ['verificar_qr_code', 'atualizar_ultimo_acesso', 'get_resumo_para_bot']
    for metodo in metodos_necessarios:
        if hasattr(Operador, metodo):
            print(f"  ✅ Método {metodo} existe")
        else:
            print(f"  ❌ Método {metodo} NÃO existe")
    
    # Mostrar um operador de exemplo
    if operadores_bot > 0:
        op = Operador.objects.filter(ativo_bot=True).first()
        print(f"\n  Exemplo de operador:")
        print(f"    - Nome: {op.nome}")
        print(f"    - Código: {op.codigo}")
        print(f"    - Chat ID: {op.chat_id_telegram}")
        
except Exception as e:
    print(f"  ❌ Erro ao verificar operadores: {e}")

# 2. Verificar equipamentos
print("\n🔧 EQUIPAMENTOS:")
try:
    equipamentos_total = Equipamento.objects.count()
    equipamentos_nr12 = Equipamento.objects.filter(ativo_nr12=True).count()
    
    print(f"  - Total cadastrados: {equipamentos_total}")
    print(f"  - Ativos NR12: {equipamentos_nr12}")
    
    # Verificar tipos NR12 (ajustado para campos corretos)
    tipos_nr12 = TipoEquipamentoNR12.objects.all().count()
    print(f"  - Tipos NR12 total: {tipos_nr12}")
    
    # Verificar métodos do equipamento
    if hasattr(Equipamento, 'get_tipo_nr12'):
        print("  ✅ Método get_tipo_nr12 existe")
    else:
        print("  ❌ Método get_tipo_nr12 NÃO existe")
    
    # Mostrar um equipamento de exemplo
    if equipamentos_nr12 > 0:
        eq = Equipamento.objects.filter(ativo_nr12=True).first()
        print(f"\n  Exemplo de equipamento:")
        print(f"    - Número série: {eq.numero_serie}")
        print(f"    - Modelo: {eq.modelo}")
        if hasattr(eq, 'tipo_nr12'):
            print(f"    - Tipo NR12: {eq.tipo_nr12.nome if eq.tipo_nr12 else 'Não definido'}")
    
except Exception as e:
    print(f"  ❌ Erro ao verificar equipamentos: {e}")

# 3. Verificar checklists (ajustado para campo data_checklist)
print("\n📋 CHECKLISTS:")
try:
    checklists_total = ChecklistNR12.objects.count()
    # Usar data_checklist ao invés de data_realizacao
    checklists_hoje = ChecklistNR12.objects.filter(
        data_checklist=timezone.now().date()
    ).count()
    checklists_pendentes = ChecklistNR12.objects.filter(status='PENDENTE').count()
    checklists_andamento = ChecklistNR12.objects.filter(status='EM_ANDAMENTO').count()
    
    print(f"  - Total: {checklists_total}")
    print(f"  - Hoje: {checklists_hoje}")
    print(f"  - Pendentes: {checklists_pendentes}")
    print(f"  - Em andamento: {checklists_andamento}")
    
    # Verificar campos disponíveis
    if checklists_total > 0:
        checklist = ChecklistNR12.objects.first()
        print("\n  Campos do checklist:")
        campos_importantes = ['uuid', 'equipamento', 'responsavel', 'data_checklist', 'status', 'turno']
        for campo in campos_importantes:
            if hasattr(checklist, campo):
                print(f"    ✅ {campo}")
            else:
                print(f"    ❌ {campo}")
    
except Exception as e:
    print(f"  ❌ Erro ao verificar checklists: {e}")

# 4. Testar endpoints
print("\n🌐 ENDPOINTS:")
try:
    from django.urls import reverse
    
    endpoints = [
        ('bot-operador-login', '/bot/operador/login/'),
        ('bot-equipamento-acesso', '/bot/equipamento/<id>/'),
        ('bot-atualizar-item', '/bot/item-checklist/atualizar/'),
    ]
    
    for name, path in endpoints:
        try:
            if '<id>' not in path:
                url = reverse(name)
                print(f"  ✅ {name}: {url}")
            else:
                print(f"  ✅ {name}: {path}")
        except:
            print(f"  ❌ {name}: NÃO ENCONTRADO")
            
except Exception as e:
    print(f"  ❌ Erro ao verificar endpoints: {e}")

# 5. Verificar configurações
print("\n⚙️ CONFIGURAÇÕES:")
try:
    # Ler .env
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
            
        configs = {
            'TELEGRAM_BOT_TOKEN': 'TELEGRAM_BOT_TOKEN' in env_content,
            'API_BASE_URL': 'API_BASE_URL' in env_content,
            'ADMIN_IDS': 'ADMIN_IDS' in env_content,
        }
        
        for key, exists in configs.items():
            if exists:
                print(f"  ✅ {key}: Configurado")
            else:
                print(f"  ❌ {key}: NÃO configurado")
    else:
        print("  ❌ Arquivo .env não encontrado!")
            
except Exception as e:
    print(f"  ❌ Erro ao verificar configurações: {e}")

# 6. Verificar pasta do bot
print("\n📁 ESTRUTURA DO BOT:")
bot_path = os.path.join(project_root, 'mandacaru_bot')
if os.path.exists(bot_path):
    print(f"  ✅ Pasta mandacaru_bot existe")
    
    # Verificar arquivos principais
    files_to_check = ['start.py', 'core/config.py', 'core/db.py', 'bot_main/main.py']
    for file in files_to_check:
        file_path = os.path.join(bot_path, file)
        if os.path.exists(file_path):
            print(f"  ✅ {file} existe")
        else:
            print(f"  ❌ {file} NÃO existe")
else:
    print(f"  ❌ Pasta mandacaru_bot NÃO existe!")

# 7. Testar conexão com API
print("\n🔌 TESTE DE API:")
try:
    import httpx
    from dotenv import load_dotenv
    
    load_dotenv()
    api_base_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api')
    
    # Testar se a API está respondendo
    try:
        response = httpx.get(f"{api_base_url}/operadores/", timeout=5.0)
        if response.status_code == 200:
            print(f"  ✅ API respondendo em: {api_base_url}")
        else:
            print(f"  ⚠️ API retornou status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ API não está acessível: {e}")
        
except ImportError:
    print("  ⚠️ httpx não instalado - instale com: pip install httpx")

print("\n" + "="*50)
print("🎯 RESUMO DO STATUS:")
print("="*50)

# Resumo final
problemas = []
if operadores_bot == 0:
    problemas.append("Nenhum operador ativo para bot")
if equipamentos_nr12 == 0:
    problemas.append("Nenhum equipamento ativo NR12")
if not os.path.exists(bot_path):
    problemas.append("Pasta do bot não encontrada")

if problemas:
    print("⚠️ Problemas encontrados:")
    for p in problemas:
        print(f"  - {p}")
else:
    print("✅ Sistema pronto para executar o bot!")
    print("\n🚀 Para iniciar o bot, execute:")
    print("   python manage.py run_telegram_bot --debug")

print("="*50)