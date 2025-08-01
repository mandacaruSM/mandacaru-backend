# ===============================================
# DESCOBRIR ENDPOINT CORRETO - Baseado na API existente
# ===============================================

import asyncio
import httpx

async def find_correct_update_endpoint():
    """Descobre o endpoint correto baseado na API existente"""
    
    base_url = "http://127.0.0.1:8000/api"
    
    print("🔍 DESCOBRINDO ENDPOINT CORRETO")
    print("=" * 50)
    
    # 1. Primeiro, vamos examinar a API que já funciona
    print("1. 📋 Verificando estrutura da API existente...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Testar o endpoint que sabemos que funciona
        endpoints_conhecidos = [
            "/nr12/itens-checklist/",  # Sabemos que existe
            "/nr12/checklists/",       # Sabemos que existe
        ]
        
        for endpoint in endpoints_conhecidos:
            try:
                response = await client.get(f"{base_url}{endpoint}")
                print(f"   ✅ {endpoint} - Status: {response.status_code}")
                
                # Se for 200, ver se tem paginação ou não
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        print(f"      📊 Paginado - {len(data['results'])} itens")
                    elif isinstance(data, list):
                        print(f"      📊 Lista simples - {len(data)} itens")
                        
            except Exception as e:
                print(f"   ❌ {endpoint} - Erro: {e}")
        
        # 2. Agora vamos testar URLs de atualização baseadas no que existe
        print(f"\n2. 🔧 Testando endpoints de atualização...")
        
        item_id = 105
        test_endpoints = [
            # Baseado no padrão Django REST Framework
            f"/nr12/itens-checklist/{item_id}/",
            
            # Talvez seja um endpoint aninhado
            f"/nr12/checklists/23/itens/{item_id}/",
            
            # Ou talvez use um nome diferente
            f"/nr12/item-checklist/{item_id}/",
            f"/nr12/checklist-item/{item_id}/",
            
            # Endpoints customizados que podem existir
            f"/nr12/atualizar-item/{item_id}/",
            f"/nr12/update-item/{item_id}/",
            
            # Endpoints do DRF com nomes longos
            f"/nr12/itemchecklistrealizado/{item_id}/",
            f"/nr12/item-checklist-realizado/{item_id}/",
        ]
        
        for endpoint in test_endpoints:
            url = f"{base_url}{endpoint}"
            
            try:
                # Testar GET primeiro (para ver se existe)
                response = await client.get(url)
                print(f"   GET {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ ENDPOINT EXISTE: {endpoint}")
                    
                    # Testar OPTIONS para ver métodos permitidos
                    try:
                        options_response = await client.request("OPTIONS", url)
                        if options_response.status_code == 200:
                            allow_header = options_response.headers.get('Allow', '')
                            print(f"      🔧 Métodos permitidos: {allow_header}")
                            
                            # Se permite PUT ou PATCH, este é nosso endpoint!
                            if 'PUT' in allow_header or 'PATCH' in allow_header:
                                print(f"   🎉 ENDPOINT DE ATUALIZAÇÃO ENCONTRADO: {endpoint}")
                                return endpoint
                    except:
                        pass
                        
                elif response.status_code == 405:
                    print(f"   ⚠️ Existe mas método GET não permitido: {endpoint}")
                    
                    # Mesmo assim, testar OPTIONS
                    try:
                        options_response = await client.request("OPTIONS", url)
                        allow_header = options_response.headers.get('Allow', '')
                        print(f"      🔧 Métodos permitidos: {allow_header}")
                        
                        if 'PUT' in allow_header or 'PATCH' in allow_header:
                            print(f"   🎉 ENDPOINT DE ATUALIZAÇÃO ENCONTRADO: {endpoint}")
                            return endpoint
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ❌ {endpoint} - Erro: {e}")
    
    print("\n" + "=" * 50)
    print("❌ Nenhum endpoint de atualização encontrado automaticamente")
    print("\n💡 PRÓXIMA AÇÃO:")
    print("Vamos verificar o código Django para ver as URLs configuradas")
    
    return None

if __name__ == "__main__":
    asyncio.run(find_correct_update_endpoint())