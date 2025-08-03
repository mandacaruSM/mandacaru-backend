# ===============================================
# TESTE 3: Script para testar as correções da API
# mandacaru_bot/testes/teste_correcoes_api.py
# ===============================================

import asyncio
import httpx
import json
from datetime import datetime

# Configurações
API_BASE_URL = "http://127.0.0.1:8000/api"
CHAT_ID_TESTE = "853870420"  # Seu chat_id
ITEM_ID_TESTE = 105  # Item que estava falhando

async def testar_busca_operador():
    """Teste 1: Buscar operador por chat_id"""
    print("\n🔍 TESTE 1: Buscar operador por chat_id")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': CHAT_ID_TESTE}
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            
            print(f"📡 URL: {url}")
            print(f"📋 Parâmetros: {params}")
            print(f"🔢 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                resultados = data.get('results', [])
                
                if resultados:
                    operador = resultados[0]
                    print(f"✅ Operador encontrado:")
                    print(f"    👤 Nome: {operador.get('nome')}")
                    print(f"    🔑 Código: {operador.get('codigo')}")
                    print(f"    📱 Chat ID: {operador.get('chat_id_telegram')}")
                    return operador.get('codigo')
                else:
                    print("❌ Nenhum operador encontrado")
                    return None
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"📄 Resposta: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

async def testar_endpoint_bot(operador_codigo):
    """Teste 2: Endpoint específico do bot"""
    print("\n🤖 TESTE 2: Endpoint do bot")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/nr12/bot/item-checklist/atualizar/"
        
        data = {
            'item_id': ITEM_ID_TESTE,
            'status': 'OK',
            'observacao': 'Teste de correção da API',
            'operador_codigo': operador_codigo or 'BOT001'
        }
        
        print(f"📡 URL: {url}")
        print(f"📋 Dados: {json.dumps(data, indent=2)}")
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=data)
            
            print(f"🔢 Status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Endpoint do bot funcionando!")
                    return True
                else:
                    print(f"❌ Bot retornou erro: {result.get('error')}")
                    return False
            else:
                print("❌ Endpoint do bot falhou")
                return False
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

async def testar_endpoint_direto(operador_codigo):
    """Teste 3: Endpoint direto da API"""
    print("\n🎯 TESTE 3: Endpoint direto")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/nr12/item-checklist/{ITEM_ID_TESTE}/atualizar/"
        
        data = {
            'status': 'OK',
            'observacao': 'Teste endpoint direto',
            'operador_codigo': operador_codigo or 'BOT001'
        }
        
        print(f"📡 URL: {url}")
        print(f"📋 Dados: {json.dumps(data, indent=2)}")
        
        async with httpx.AsyncClient(timeout=10) as client:
            # Tentar PATCH primeiro
            response = await client.patch(url, json=data)
            
            print(f"🔢 Status PATCH: {response.status_code}")
            
            if response.status_code not in [200, 204]:
                # Tentar POST se PATCH falhar
                response = await client.post(url, json=data)
                print(f"🔢 Status POST: {response.status_code}")
            
            print(f"📄 Resposta: {response.text}")
            
            if response.status_code in [200, 204]:
                print("✅ Endpoint direto funcionando!")
                return True
            else:
                print("❌ Endpoint direto falhou")
                return False
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

async def testar_listar_checklists():
    """Teste 4: Listar checklists do operador"""
    print("\n📋 TESTE 4: Listar checklists")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/nr12/checklists/"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            
            print(f"📡 URL: {url}")
            print(f"🔢 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', []) if isinstance(data, dict) else data
                
                print(f"✅ Encontrados {len(checklists)} checklists")
                
                for i, checklist in enumerate(checklists[:3], 1):
                    print(f"  {i}. ID: {checklist.get('id')} | Status: {checklist.get('status')} | Turno: {checklist.get('turno', 'N/A')}")
                
                return len(checklists) > 0
            else:
                print(f"❌ Erro ao listar checklists: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

async def testar_iniciar_checklist():
    """Teste 5: Iniciar checklist (que estava falhando)"""
    print("\n🚀 TESTE 5: Iniciar checklist")
    print("=" * 50)
    
    try:
        # Primeiro, encontrar um checklist PENDENTE
        url_list = f"{API_BASE_URL}/nr12/checklists/"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url_list)
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', []) if isinstance(data, dict) else data
                
                checklist_pendente = None
                for checklist in checklists:
                    if checklist.get('status') == 'PENDENTE':
                        checklist_pendente = checklist
                        break
                
                if not checklist_pendente:
                    print("⚠️ Nenhum checklist PENDENTE encontrado para teste")
                    return False
                
                checklist_id = checklist_pendente.get('id')
                print(f"📋 Tentando iniciar checklist ID: {checklist_id}")
                
                # Tentar iniciar
                url_iniciar = f"{API_BASE_URL}/nr12/checklists/{checklist_id}/iniciar/"
                
                data_iniciar = {
                    "responsavel": 1,  # ID do operador
                    "horimetro_inicial": None
                }
                
                response = await client.post(url_iniciar, json=data_iniciar)
                
                print(f"📡 URL: {url_iniciar}")
                print(f"📋 Dados: {json.dumps(data_iniciar, indent=2)}")
                print(f"🔢 Status: {response.status_code}")
                print(f"📄 Resposta: {response.text}")
                
                if response.status_code in [200, 201]:
                    print("✅ Checklist iniciado com sucesso!")
                    return True
                else:
                    print("❌ Falha ao iniciar checklist")
                    return False
            else:
                print("❌ Erro ao buscar checklists")
                return False
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

async def executar_todos_os_testes():
    """Executa todos os testes em sequência"""
    print("🧪 INICIANDO TESTES DAS CORREÇÕES DA API")
    print("=" * 60)
    
    resultados = {}
    
    # Teste 1: Buscar operador
    operador_codigo = await testar_busca_operador()
    resultados['busca_operador'] = operador_codigo is not None
    
    # Teste 2: Endpoint do bot
    if operador_codigo:
        resultados['endpoint_bot'] = await testar_endpoint_bot(operador_codigo)
    else:
        print("\n⚠️ Pulando teste do endpoint bot (operador não encontrado)")
        resultados['endpoint_bot'] = False
    
    # Teste 3: Endpoint direto
    resultados['endpoint_direto'] = await testar_endpoint_direto(operador_codigo)
    
    # Teste 4: Listar checklists
    resultados['listar_checklists'] = await testar_listar_checklists()
    
    # Teste 5: Iniciar checklist
    resultados['iniciar_checklist'] = await testar_iniciar_checklist()
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    testes_passaram = 0
    total_testes = len(resultados)
    
    for teste, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{teste.replace('_', ' ').title()}: {status}")
        if passou:
            testes_passaram += 1
    
    print(f"\n🎯 RESULTADO: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! As correções estão funcionando.")
    elif testes_passaram >= total_testes * 0.8:
        print("👍 MAIORIA DOS TESTES PASSOU! Pequenos ajustes podem ser necessários.")
    else:
        print("⚠️ VÁRIOS TESTES FALHARAM. Correções adicionais são necessárias.")
    
    return resultados

# ===============================================
# FUNÇÃO PRINCIPAL
# ===============================================

if __name__ == "__main__":
    print("🚀 Executando testes das correções...")
    resultados = asyncio.run(executar_todos_os_testes())
    
    # Salvar resultados em arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"teste_resultados_{timestamp}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'chat_id_teste': CHAT_ID_TESTE,
            'item_id_teste': ITEM_ID_TESTE,
            'resultados': resultados
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {nome_arquivo}")

# ===============================================
# FUNÇÕES AUXILIARES PARA DEBUGGING
# ===============================================

async def debug_operador_especifico(chat_id: str):
    """Debug específico para um operador"""
    print(f"\n🔍 DEBUG OPERADOR - Chat ID: {chat_id}")
    print("=" * 50)
    
    try:
        # Buscar por chat_id
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"📄 Resposta completa: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                resultados = data.get('results', [])
                if resultados:
                    operador = resultados[0]
                    print(f"\n✅ Operador encontrado:")
                    for key, value in operador.items():
                        print(f"    {key}: {value}")
                else:
                    print("❌ Operador não encontrado")
                    
                    # Tentar buscar todos os operadores
                    response_all = await client.get(f"{API_BASE_URL}/operadores/")
                    if response_all.status_code == 200:
                        all_data = response_all.json()
                        all_operadores = all_data.get('results', [])
                        
                        print(f"\n📋 Total de operadores no sistema: {len(all_operadores)}")
                        print("🔍 Operadores com chat_id:")
                        
                        for op in all_operadores:
                            if op.get('chat_id_telegram'):
                                print(f"    {op.get('nome')} - Chat ID: {op.get('chat_id_telegram')}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"📄 Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

async def testar_urls_alternativas():
    """Testa URLs alternativas que podem existir"""
    print("\n🔗 TESTANDO URLs ALTERNATIVAS")
    print("=" * 50)
    
    urls_teste = [
        f"{API_BASE_URL}/operadores/por-chat-id/?chat_id={CHAT_ID_TESTE}",
        f"{API_BASE_URL}/operadores/buscar/?chat_id_telegram={CHAT_ID_TESTE}",
        f"{API_BASE_URL}/nr12/bot/operador/por-chat/{CHAT_ID_TESTE}/",
        f"{API_BASE_URL}/bot/operador/{CHAT_ID_TESTE}/",
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for url in urls_teste:
            try:
                response = await client.get(url)
                print(f"📡 {url}")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ FUNCIONOU!")
                    try:
                        data = response.json()
                        print(f"   📄 Dados: {json.dumps(data, indent=6)[:200]}...")
                    except:
                        print(f"   📄 Resposta: {response.text[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")

# ===============================================
# SCRIPT PARA CORRIGIR CHAT_ID DO OPERADOR
# ===============================================

async def corrigir_chat_id_operador(operador_id: int, novo_chat_id: str):
    """Corrige o chat_id de um operador específico"""
    print(f"\n🔧 CORRIGINDO CHAT_ID DO OPERADOR {operador_id}")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/"
        
        data = {
            'chat_id_telegram': novo_chat_id
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            # Tentar PATCH primeiro
            response = await client.patch(url, json=data)
            
            print(f"📡 URL: {url}")
            print(f"📋 Dados: {json.dumps(data, indent=2)}")
            print(f"🔢 Status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
            if response.status_code in [200, 204]:
                print("✅ Chat ID atualizado com sucesso!")
                return True
            else:
                print("❌ Falha ao atualizar chat ID")
                return False
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False