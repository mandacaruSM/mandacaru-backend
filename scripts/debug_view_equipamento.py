# scripts/debug_view_equipamento.py

import os
import sys
import django

# Configurar Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("🔍 DEBUG DA VIEW EQUIPAMENTOACESSOBOTVIEW")
print("="*50)

# Importar a view
try:
    from backend.apps.nr12_checklist.bot_views.bot_telegram import EquipamentoAcessoBotView
    
    print("✅ View importada com sucesso!")
    
    # Verificar o código da view
    import inspect
    
    print("\n📄 CÓDIGO DA VIEW:")
    print("-"*50)
    
    # Pegar o código fonte
    source = inspect.getsource(EquipamentoAcessoBotView)
    
    # Procurar por campos esperados
    print("Procurando campos no POST...")
    lines = source.split('\n')
    
    for i, line in enumerate(lines):
        # Procurar por .get() ou [''] que indicam campos esperados
        if any(x in line for x in ['.get(', "['", '["', 'data.get', 'request.POST', 'request.data']):
            print(f"Linha {i}: {line.strip()}")
            
            # Mostrar contexto
            if 'codigo' in line.lower() or 'operador' in line.lower():
                print(f"  >>> CAMPO IMPORTANTE: {line.strip()}")
    
    # Procurar especificamente por validações
    print("\n🔍 VALIDAÇÕES ENCONTRADAS:")
    for i, line in enumerate(lines):
        if 'obrigatório' in line or 'required' in line.lower() or 'if not' in line:
            print(f"Linha {i}: {line.strip()}")
            # Contexto
            if i > 0:
                print(f"  Anterior: {lines[i-1].strip()}")
    
except ImportError as e:
    print(f"❌ Erro ao importar view: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Testar diferentes combinações de campos
print("\n🧪 TESTANDO DIFERENTES CAMPOS:")
print("-"*50)

import httpx
import json

campos_teste = [
    {"codigo_operador": "OP0001", "acao": "visualizar"},
    {"operador_codigo": "OP0001", "acao": "visualizar"},
    {"operador": "OP0001", "acao": "visualizar"},
    {"codigo": "OP0001", "acao": "visualizar"},
    {"operador_id": 9, "codigo_operador": "OP0001", "acao": "visualizar"},
]

for i, campos in enumerate(campos_teste, 1):
    print(f"\nTeste {i}: {campos}")
    
    try:
        response = httpx.post(
            "http://127.0.0.1:8000/bot/equipamento/1/",
            json=campos,
            timeout=5.0
        )
        
        if response.status_code == 200:
            print(f"✅ SUCESSO com campos: {campos}")
            break
        else:
            data = response.json()
            erro = data.get('error', data.get('message', 'Erro desconhecido'))
            print(f"❌ Status {response.status_code}: {erro}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

print("\n" + "="*50)