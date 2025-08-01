# ===============================================
# SCRIPT: Encontrar endpoint de atualização correto
# Execute: python find_update_endpoint.py
# ===============================================

import asyncio
import httpx

async def find_update_endpoints():
    """Encontra os endpoints corretos para atualização"""
    
    base_url = "http://127.0.0.1:8000/api"
    
    print("🔍 PROCURANDO ENDPOINTS DE ATUALIZAÇÃO")
    print("=" * 50)
    
    # Lista de endpoints para testar
    endpoints_to_test = [
        # Baseado no que vimos no Django Admin
        "/nr12/item-checklist-realizado/105/",
        "/nr12/itens-realizados/105/",
        "/nr12/checklist-realizado/105/",
        
        # Outros padrões possíveis
        "/nr12/item-realizado/105/",
        "/nr12/items/105/",
        "/nr12/checklist-items/105/",
        
        # Endpoints aninhados
        "/nr12/checklists/23/itens/105/",
        "/nr12/checklists/23/items/105/",
        
        # Padrão Django REST
        "/nr12/itemchecklistrealizado/105/",
        "/nr12/item_checklist_realizado/105/",
        
        # Endpoints customizados do bot
        "/nr12/bot/atualizar-item/",
        "/nr12/bot/item/105/",
        "/bot/nr12/item/105/",
    ]
    
    data = {
        'status': 'OK',
        'observacao': 'Teste do bot'
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            
            print(f"\n🧪 Testando: {endpoint}")
            
            # Testar GET primeiro (para ver se existe)
            try:
                response = await client.get(url)
                print(f"   GET: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Endpoint existe!")
                    
                    # Testar PUT
                    try:
                        put_response = await client.put(url, json=data)
                        print(f"   PUT: {put_response.status_code}")
                        if put_response.status_code in [200, 201]:
                            print(f"   🎉 SUCESSO! Endpoint funcionando: {endpoint}")
                            return endpoint
                    except:
                        pass
                    
                    # Testar PATCH
                    try:
                        patch_response = await client.patch(url, json=data)
                        print(f"   PATCH: {patch_response.status_code}")
                        if patch_response.status_code in [200, 201]:
                            print(f"   🎉 SUCESSO! Endpoint funcionando: {endpoint}")
                            return endpoint
                    except:
                        pass
                
                elif response.status_code == 404:
                    print("   ❌ Não existe")
                elif response.status_code == 405:
                    print("   ⚠️ Existe mas método não permitido")
                else:
                    print(f"   ⚠️ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("❌ Nenhum endpoint de atualização encontrado")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Verificar as URLs do Django em backend/apps/nr12_checklist/urls.py")
    print("2. Ou criar um endpoint customizado para o bot")
    
    return None

if __name__ == "__main__":
    asyncio.run(find_update_endpoints())