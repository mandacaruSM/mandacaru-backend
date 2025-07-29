# scripts/teste_equipamento_final.py

import httpx
import json

print("🔧 TESTE FINAL - ACESSO A EQUIPAMENTO")
print("="*50)

# Dados corretos
OPERADOR_ID = 9
OPERADOR_CODIGO = "OP0001"
EQUIPAMENTO_ID = 1

print(f"\nDados do teste:")
print(f"- Operador ID: {OPERADOR_ID}")
print(f"- Operador Código: {OPERADOR_CODIGO}")
print(f"- Equipamento ID: {EQUIPAMENTO_ID}")

# Teste 1: Com ID do operador
print("\n1️⃣ Teste com ID do operador:")
try:
    response = httpx.post(
        f"http://127.0.0.1:8000/bot/equipamento/{EQUIPAMENTO_ID}/",
        json={
            "operador_id": OPERADOR_ID,
            "acao": "visualizar"
        },
        timeout=10.0
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print("✅ SUCESSO!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro: {data}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 2: Com código do operador
print("\n2️⃣ Teste com código do operador:")
try:
    response = httpx.post(
        f"http://127.0.0.1:8000/bot/equipamento/{EQUIPAMENTO_ID}/",
        json={
            "codigo_operador": OPERADOR_CODIGO,
            "acao": "visualizar"
        },
        timeout=10.0
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print("✅ SUCESSO!")
        if 'equipamento' in data:
            eq = data['equipamento']
            print(f"\nEquipamento:")
            print(f"- ID: {eq.get('id')}")
            print(f"- Nome: {eq.get('nome')}")
            print(f"- Modelo: {eq.get('modelo')}")
            print(f"- Série: {eq.get('numero_serie', eq.get('n_serie'))}")
            print(f"- Status: {eq.get('status_operacional')}")
            
        if 'acoes_disponiveis' in data:
            print(f"\nAções disponíveis:")
            for acao in data['acoes_disponiveis']:
                print(f"- {acao}")
    else:
        print(f"❌ Erro: {data}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*50)
print("\n🎯 Comandos curl para teste:")
print(f"""
curl -X POST http://127.0.0.1:8000/bot/equipamento/{EQUIPAMENTO_ID}/ \\
  -H "Content-Type: application/json" \\
  -d '{{"operador_id": {OPERADOR_ID}, "acao": "visualizar"}}'
""")

print("\n🤖 Bot está pronto para uso!")
print("Execute: python manage.py run_telegram_bot --debug")