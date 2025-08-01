# ===============================================
# SCRIPT: Verificar estrutura real do checklist
# ===============================================

import asyncio
import httpx
import json

async def verificar_checklist_completo(checklist_id: int = 23):
    """Verifica a estrutura completa do checklist"""
    
    print("🔍 VERIFICANDO ESTRUTURA DO CHECKLIST")
    print("=" * 50)
    
    # 1. Verificar dados do checklist principal
    print(f"📋 1. DADOS DO CHECKLIST {checklist_id}")
    print("-" * 30)
    
    try:
        url = f"http://127.0.0.1:8000/api/nr12/checklists/{checklist_id}/"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                checklist = response.json()
                print(f"✅ Checklist encontrado:")
                print(f"   - ID: {checklist.get('id')}")
                print(f"   - UUID: {checklist.get('uuid')}")
                print(f"   - Status: {checklist.get('status')}")
                print(f"   - Equipamento: {checklist.get('equipamento_nome')}")
                print(f"   - Data: {checklist.get('data_checklist')}")
                print(f"   - Turno: {checklist.get('turno')}")
                print(f"   - Responsável: {checklist.get('responsavel_nome') or 'Nenhum'}")
                
                # Verificar se tem estatísticas
                if 'total_itens' in checklist:
                    print(f"   - Total de itens: {checklist.get('total_itens')}")
                    print(f"   - Itens OK: {checklist.get('itens_ok', 0)}")
                    print(f"   - Itens NOK: {checklist.get('itens_nok', 0)}")
                    print(f"   - Itens pendentes: {checklist.get('itens_pendentes', 0)}")
                    print(f"   - % Conclusão: {checklist.get('percentual_conclusao', 0)}%")
                
            else:
                print(f"❌ Erro {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar checklist: {e}")
        return False
    
    # 2. Verificar itens realizados
    print(f"\n📝 2. ITENS REALIZADOS DO CHECKLIST")
    print("-" * 30)
    
    try:
        url = f"http://127.0.0.1:8000/api/nr12/checklists/{checklist_id}/itens/"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                itens = response.json()
                
                # Se é paginado
                if isinstance(itens, dict) and 'results' in itens:
                    itens_lista = itens['results']
                    total = itens.get('count', len(itens_lista))
                    print(f"✅ Total de itens: {total}")
                else:
                    itens_lista = itens
                    print(f"✅ Total de itens: {len(itens_lista)}")
                
                if itens_lista:
                    print(f"\n📊 Amostra dos primeiros 3 itens:")
                    
                    for i, item in enumerate(itens_lista[:3]):
                        print(f"\n   Item {i+1}:")
                        print(f"     - ID: {item.get('id')}")
                        print(f"     - Descrição: {item.get('item_padrao_nome', 'N/A')}")
                        print(f"     - Status: {item.get('status')}")
                        print(f"     - Criticidade: {item.get('item_padrao_criticidade', 'N/A')}")
                        print(f"     - Observação: {item.get('observacao') or 'Nenhuma'}")
                        print(f"     - Verificado por: {item.get('verificado_por') or 'Ninguém'}")
                        print(f"     - Data verificação: {item.get('verificado_em') or 'Não verificado'}")
                
                # Contar por status
                status_count = {}
                for item in itens_lista:
                    status = item.get('status', 'UNKNOWN')
                    status_count[status] = status_count.get(status, 0) + 1
                
                print(f"\n📈 Distribuição por status:")
                for status, count in status_count.items():
                    emoji = {"PENDENTE": "🟡", "OK": "✅", "NOK": "❌", "NA": "⚪"}.get(status, "❓")
                    print(f"     {emoji} {status}: {count}")
                
            else:
                print(f"❌ Erro {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar itens: {e}")
        return False
    
    # 3. Testar endpoint de atualização com dados fictícios
    print(f"\n🧪 3. TESTE DO ENDPOINT DE ATUALIZAÇÃO")
    print("-" * 30)
    
    try:
        # Pegar o primeiro item pendente para teste
        primeiro_pendente = None
        for item in itens_lista:
            if item.get('status') == 'PENDENTE':
                primeiro_pendente = item
                break
        
        if primeiro_pendente:
            print(f"🎯 Testando com item ID {primeiro_pendente.get('id')}")
            
            url = "http://127.0.0.1:8000/api/nr12/bot/item-checklist/atualizar/"
            
            # Dados de teste (não vai realmente atualizar)
            test_data = {
                "item_id": primeiro_pendente.get('id'),
                "status": "OK",
                "observacao": "Teste de conectividade",
                "operador_codigo": "OP0001"
            }
            
            print(f"📤 Enviando dados de teste: {test_data}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=test_data)
                
                print(f"📊 Status da resposta: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ ENDPOINT FUNCIONANDO!")
                    print(f"   Resposta: {result}")
                elif response.status_code == 400:
                    try:
                        error = response.json()
                        print(f"⚠️  Erro 400 (esperado): {error}")
                    except:
                        print(f"⚠️  Erro 400: {response.text}")
                else:
                    print(f"❌ Erro {response.status_code}: {response.text}")
        else:
            print("⚠️  Nenhum item pendente encontrado para teste")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    print(f"\n🎉 VERIFICAÇÃO COMPLETA!")
    return True

async def main():
    """Função principal"""
    await verificar_checklist_completo(23)

if __name__ == "__main__":
    asyncio.run(main())