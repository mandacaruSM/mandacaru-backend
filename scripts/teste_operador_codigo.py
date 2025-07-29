# scripts/teste_operador_codigo.py

import httpx
import json

print("🎯 TESTE COM CAMPO CORRETO: operador_codigo")
print("="*50)

# O debug mostrou que o campo correto é 'operador_codigo'
# E o teste 2 retornou erro diferente, então o campo foi aceito!

# Vamos testar com ações válidas
acoes_possiveis = [
    "criar_checklist",
    "iniciar_checklist", 
    "continuar_checklist",
    "listar_checklists",
    "status"
]

print("\n🧪 Testando ações disponíveis:")

for acao in acoes_possiveis:
    print(f"\nTestando ação: {acao}")
    
    try:
        response = httpx.post(
            "http://127.0.0.1:8000/bot/equipamento/1/",
            json={
                "operador_codigo": "OP0001",
                "acao": acao
            },
            timeout=10.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCESSO com ação '{acao}'!")
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            break
        else:
            data = response.json()
            erro = data.get('error', 'Erro desconhecido')
            print(f"❌ Erro: {erro}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

# Teste sem ação (pode ser o padrão)
print("\n🧪 Testando SEM especificar ação:")
try:
    response = httpx.post(
        "http://127.0.0.1:8000/bot/equipamento/1/",
        json={
            "operador_codigo": "OP0001"
        },
        timeout=10.0
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print("✅ SUCESSO sem especificar ação!")
        print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
    else:
        print(f"❌ Erro: {data}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*50)