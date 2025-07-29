# scripts/teste_direto_equipamento.py

import httpx
import json

print("🎯 TESTE DIRETO - CAMPO CÓDIGO_OPERADOR")
print("="*50)

# Teste com o campo que provavelmente é esperado
campos = {
    "codigo_operador": "OP0001",  # Campo mais provável
    "acao": "visualizar"
}

print(f"\nTestando com: {json.dumps(campos, indent=2)}")

try:
    response = httpx.post(
        "http://127.0.0.1:8000/bot/equipamento/1/",
        json=campos,
        timeout=10.0
    )
    
    print(f"\nStatus: {response.status_code}")
    
    try:
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and data.get('success'):
            print("\n✅ SUCESSO! Campo correto é 'codigo_operador'")
            
            if 'equipamento' in data:
                eq = data['equipamento']
                print(f"\n📋 Dados do Equipamento:")
                print(f"  - ID: {eq.get('id')}")
                print(f"  - Nome: {eq.get('nome')}")
                print(f"  - Modelo: {eq.get('modelo')}")
                print(f"  - Marca: {eq.get('marca')}")
                print(f"  - Série: {eq.get('n_serie')}")
                print(f"  - Status: {eq.get('status_operacional')}")
                
            if 'acoes_disponiveis' in data:
                print(f"\n🎮 Ações Disponíveis:")
                for acao in data['acoes_disponiveis']:
                    if isinstance(acao, dict):
                        print(f"  - {acao.get('texto', acao.get('acao'))}")
                    else:
                        print(f"  - {acao}")
                        
    except json.JSONDecodeError:
        print(f"Resposta (não é JSON): {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n💡 Comando curl correto:")
print("""
curl -X POST http://127.0.0.1:8000/bot/equipamento/1/ \\
  -H "Content-Type: application/json" \\
  -d '{"codigo_operador": "OP0001", "acao": "visualizar"}'
""")

print("\n🤖 Se funcionou, o bot está pronto!")
print("Execute: python manage.py run_telegram_bot --debug")