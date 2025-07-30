#!/usr/bin/env python
import requests
import json

def testar_apis():
    print("🧪 TESTANDO APIs DO BOT")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8000"
    
    testes = [
        {
            'nome': 'Operador por Chat ID',
            'url': f'{base_url}/api/operadores/?chat_id_telegram=853870420',
        },
        {
            'nome': 'Equipamento Prisma por UUID',
            'url': f'{base_url}/api/equipamentos/por-uuid/ea23d82d-549b-44bf-8981-7f94e6802461/',
        },
        {
            'nome': 'Equipamento EH01 por UUID',
            'url': f'{base_url}/api/equipamentos/por-uuid/9cca38f1-a244-4911-8875-19f1191dd045/',
        },
        {
            'nome': 'Checklists (novo endpoint)',
            'url': f'{base_url}/api/checklists/?operador_id=9',
        },
        {
            'nome': 'Equipamentos (novo endpoint)',
            'url': f'{base_url}/api/equipamentos/?operador_id=9',
        },
        {
            'nome': 'Equipamentos do Operador',
            'url': f'{base_url}/api/operadores/9/equipamentos/',
        },
        {
            'nome': 'Checklists do Equipamento 1',
            'url': f'{base_url}/api/equipamentos/1/checklists/',
        },
    ]
    
    for teste in testes:
        try:
            response = requests.get(teste['url'], timeout=5)
            status = "✅" if response.status_code < 400 else "❌"
            print(f"{status} {teste['nome']}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'count' in data:
                        print(f"   📊 {data['count']} registros")
                    elif isinstance(data, list):
                        print(f"   📊 {len(data)} registros")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ {teste['nome']}: {e}")
    
    print("\n🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_apis()
