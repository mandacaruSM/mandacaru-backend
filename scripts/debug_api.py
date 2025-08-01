# ===============================================
# SCRIPT DE DEBUG: Testar API diretamente
# Execute este script na pasta do bot para testar as APIs
# ===============================================

import asyncio
import httpx
import json

async def test_checklist_apis():
    """Testa as APIs do checklist diretamente"""
    
    base_url = "http://127.0.0.1:8000/api"
    
    print("🧪 TESTANDO APIs DO CHECKLIST")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # 1. Testar health check
        print("\n1. 🏥 Testando Health Check...")
        try:
            response = await client.get(f"{base_url}/health/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 2. Testar listagem de checklists
        print("\n2. 📋 Testando listagem de checklists...")
        try:
            response = await client.get(f"{base_url}/nr12/checklists/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Encontrados: {len(data.get('results', data)) if isinstance(data, dict) else len(data)} checklists")
                # Pegar o primeiro checklist para teste
                checklists = data.get('results', []) if isinstance(data, dict) else data
                if checklists:
                    first_checklist = checklists[0]
                    checklist_id = first_checklist.get('id')
                    print(f"   Primeiro checklist ID: {checklist_id}")
                    return checklist_id
            else:
                print(f"   ❌ Erro: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return None

async def test_checklist_items(checklist_id):
    """Testa buscar itens de um checklist específico"""
    
    base_url = "http://127.0.0.1:8000/api"
    
    print(f"\n3. 📝 Testando itens do checklist {checklist_id}...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{base_url}/nr12/checklists/{checklist_id}/itens/")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                itens = data.get('results', []) if isinstance(data, dict) else data
                print(f"   Encontrados: {len(itens)} itens")
                
                if itens:
                    primeiro_item = itens[0]
                    print(f"\n   📋 ESTRUTURA DO PRIMEIRO ITEM:")
                    print(json.dumps(primeiro_item, indent=2, ensure_ascii=False))
                    
                    item_id = primeiro_item.get('id')
                    print(f"\n   🆔 Item ID para teste: {item_id}")
                    return item_id, primeiro_item
            else:
                print(f"   ❌ Erro: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return None, None

async def test_update_item(item_id):
    """Testa atualizar um item do checklist"""
    
    base_url = "http://127.0.0.1:8000/api"
    
    print(f"\n4. ✏️ Testando atualização do item {item_id}...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Testar diferentes endpoints possíveis
        endpoints_to_try = [
            f"/nr12/itens/{item_id}/",
            f"/nr12/checklists/itens/{item_id}/",
            f"/nr12/checklist-itens/{item_id}/",
        ]
        
        data = {
            'status': 'OK',
            'observacao': 'Teste do bot',
        }
        
        for endpoint in endpoints_to_try:
            try:
                print(f"   Tentando: PUT {base_url}{endpoint}")
                response = await client.put(f"{base_url}{endpoint}", json=data)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ Sucesso com endpoint: {endpoint}")
                    return endpoint
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    return None

async def main():
    """Função principal de teste"""
    
    # Testar APIs
    checklist_id = await test_checklist_apis()
    
    if checklist_id:
        item_id, item_data = await test_checklist_items(checklist_id)
        
        if item_id:
            working_endpoint = await test_update_item(item_id)
            
            print("\n" + "=" * 50)
            print("📊 RESUMO DOS TESTES:")
            print(f"✅ Checklist ID encontrado: {checklist_id}")
            print(f"✅ Item ID encontrado: {item_id}")
            
            if working_endpoint:
                print(f"✅ Endpoint funcionando: {working_endpoint}")
            else:
                print("❌ Nenhum endpoint de atualização funcionou")
                
            # Analisar estrutura do item
            print("\n🔍 ANÁLISE DA ESTRUTURA DO ITEM:")
            if item_data:
                if 'item_padrao' in item_data:
                    print("✅ Campo 'item_padrao' encontrado")
                    item_padrao = item_data['item_padrao']
                    if isinstance(item_padrao, dict) and 'descricao' in item_padrao:
                        print(f"✅ Descrição encontrada: {item_padrao.get('descricao')}")
                    else:
                        print("❌ Campo 'descricao' não encontrado em item_padrao")
                        print(f"   Campos disponíveis: {list(item_padrao.keys()) if isinstance(item_padrao, dict) else 'Não é dict'}")
                else:
                    print("❌ Campo 'item_padrao' não encontrado")
                    print(f"   Campos disponíveis: {list(item_data.keys())}")

if __name__ == "__main__":
    asyncio.run(main())