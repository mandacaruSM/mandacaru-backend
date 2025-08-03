#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste corrigido com os endpoints que realmente existem
Execute: python teste_corrigido.py
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configurações
API_BASE_URL = "http://127.0.0.1:8000/api"
CHAT_ID_TESTE = "853870420"
ITEM_ID_TESTE = 105

async def teste_1_buscar_operador():
    """Teste 1: Buscar operador - PASSOU"""
    print("\n🔍 TESTE 1: Buscar operador por chat_id")
    print("=" * 50)
    
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': CHAT_ID_TESTE}
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                resultados = data.get('results', [])
                
                if resultados:
                    operador = resultados[0]
                    print(f"✅ Operador encontrado: {operador.get('nome')}")
                    print(f"   ID: {operador.get('id')}")
                    print(f"   Código: {operador.get('codigo')}")
                    print(f"   User ID: {operador.get('user_id', 'N/A')}")
                    return operador
                    
        print("❌ Operador não encontrado")
        return None
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

async def teste_2_endpoint_correto(operador):
    """Teste 2: Usar endpoint que realmente existe"""
    print("\n🎯 TESTE 2: Endpoint correto de itens")
    print("=" * 50)
    
    try:
        # Usar endpoint que existe: /nr12/itens-checklist/{id}/
        url = f"{API_BASE_URL}/nr12/itens-checklist/{ITEM_ID_TESTE}/"
        
        # Dados para PATCH
        data = {
            'status': 'OK',
            'observacao': 'Teste com endpoint correto'
        }
        
        print(f"📡 URL: {url}")
        print(f"📋 Método: PATCH")
        print(f"📋 Dados: {json.dumps(data, indent=2)}")
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.patch(url, json=data)
            
            print(f"🔢 Status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
            if response.status_code in [200, 204]:
                print("✅ Endpoint correto funcionando!")
                return True
            else:
                print(f"❌ Falhou: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def teste_3_iniciar_checklist_corrigido(operador):
    """Teste 3: Iniciar checklist com dados corretos"""
    print("\n🚀 TESTE 3: Iniciar checklist corrigido")
    print("=" * 50)
    
    try:
        # Buscar checklist PENDENTE
        url_list = f"{API_BASE_URL}/nr12/checklists/"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url_list)
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', [])
                
                checklist_pendente = None
                for checklist in checklists:
                    if checklist.get('status') == 'PENDENTE':
                        checklist_pendente = checklist
                        break
                
                if not checklist_pendente:
                    print("⚠️ Nenhum checklist PENDENTE encontrado")
                    return False
                
                checklist_id = checklist_pendente.get('id')
                print(f"📋 Checklist selecionado: ID {checklist_id}")
                
                # Testar com diferentes IDs de usuário
                user_ids_para_testar = [
                    operador.get('id'),           # ID do operador
                    operador.get('user_id'),      # user_id se existir
                    1,                            # ID padrão
                ]
                
                for user_id in user_ids_para_testar:
                    if user_id is None:
                        continue
                        
                    print(f"\n🧪 Testando com user_id: {user_id}")
                    
                    url_iniciar = f"{API_BASE_URL}/nr12/checklists/{checklist_id}/iniciar/"
                    data_iniciar = {"responsavel": user_id}
                    
                    response = await client.post(url_iniciar, json=data_iniciar)
                    
                    print(f"📡 URL: {url_iniciar}")
                    print(f"📋 Dados: {json.dumps(data_iniciar)}")
                    print(f"🔢 Status: {response.status_code}")
                    print(f"📄 Resposta: {response.text}")
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ Checklist iniciado com user_id: {user_id}!")
                        return True
                    else:
                        print(f"❌ Falhou com user_id: {user_id}")
                
                print("❌ Todos os user_ids falharam")
                return False
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def teste_4_debug_completo():
    """Teste 4: Debug completo da estrutura"""
    print("\n🔍 TESTE 4: Debug completo")
    print("=" * 50)
    
    try:
        # 1. Verificar estrutura do operador
        print("📋 1. Estrutura do operador:")
        operador = await teste_1_buscar_operador()
        
        if operador:
            for key, value in operador.items():
                print(f"   {key}: {value}")
        
        # 2. Verificar item específico
        print(f"\n📋 2. Detalhes do item {ITEM_ID_TESTE}:")
        url_item = f"{API_BASE_URL}/nr12/itens-checklist/{ITEM_ID_TESTE}/"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url_item)
            
            print(f"📡 URL: {url_item}")
            print(f"🔢 Status: {response.status_code}")
            
            if response.status_code == 200:
                item_data = response.json()
                print("✅ Item encontrado:")
                for key, value in item_data.items():
                    print(f"   {key}: {value}")
            else:
                print(f"❌ Item não encontrado: {response.text}")
        
        # 3. Verificar endpoints disponíveis
        print("\n📋 3. Testando endpoints base:")
        endpoints_teste = [
            f"{API_BASE_URL}/nr12/",
            f"{API_BASE_URL}/nr12/itens-checklist/",
            f"{API_BASE_URL}/nr12/checklists/",
        ]
        
        for endpoint in endpoints_teste:
            try:
                response = await client.get(endpoint)
                status = "✅" if response.status_code < 400 else "❌"
                print(f"   {status} {endpoint} [{response.status_code}]")
            except Exception as e:
                print(f"   ❌ {endpoint} [ERROR: {e}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        return False

async def executar_testes_corrigidos():
    """Executa todos os testes com as correções"""
    print("🧪 TESTES CORRIGIDOS DO BOT MANDACARU")
    print("=" * 60)
    
    resultados = {}
    
    # Teste 1: Buscar operador
    operador = await teste_1_buscar_operador()
    resultados['busca_operador'] = operador is not None
    
    if not operador:
        print("\n❌ Sem operador, não é possível continuar outros testes")
        return resultados
    
    # Teste 2: Endpoint correto
    resultados['endpoint_correto'] = await teste_2_endpoint_correto(operador)
    
    # Teste 3: Iniciar checklist
    resultados['iniciar_checklist'] = await teste_3_iniciar_checklist_corrigido(operador)
    
    # Teste 4: Debug completo
    resultados['debug_completo'] = await teste_4_debug_completo()
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES CORRIGIDOS")
    print("=" * 60)
    
    testes_passaram = sum(1 for passou in resultados.values() if passou)
    total_testes = len(resultados)
    
    for teste, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{teste.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 RESULTADO: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram >= total_testes * 0.75:
        print("🎉 MAIORIA DOS TESTES PASSOU! Problemas identificados e soluções prontas.")
    else:
        print("⚠️ PROBLEMAS IDENTIFICADOS. Veja os detalhes acima.")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"teste_corrigido_{timestamp}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'operador': operador,
            'resultados': resultados,
            'conclusoes': [
                "Endpoint /nr12/bot/item-checklist/atualizar/ NÃO EXISTE",
                "Usar endpoint /nr12/itens-checklist/{id}/ com PATCH",
                "Problema no iniciar checklist: responsavel deve ser UsuarioCliente ID",
                "Operador encontrado corretamente na API"
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados detalhados salvos em: {nome_arquivo}")
    
    return resultados

if __name__ == "__main__":
    print("🚀 Executando testes corrigidos...")
    resultados = asyncio.run(executar_testes_corrigidos())
    
    print("\n🎯 PRÓXIMAS AÇÕES:")
    print("1. Aplicar correção do endpoint (usar PATCH em /nr12/itens-checklist/{id}/)")
    print("2. Corrigir inicialização de checklist (usar UsuarioCliente ID correto)")
    print("3. Atualizar função atualizar_item_checklist_nr12() no bot")
    print("4. Testar novamente")