# ================================================================
# SCRIPT PARA TESTAR A CORREÇÃO DOS CAMPOS PADRONIZADOS
# Salve como: testar_campos_padronizados.py
# Execute: python testar_campos_padronizados.py
# ================================================================

import requests
import json
from datetime import datetime, date

# Configurações
BASE_URL = "http://127.0.0.1:8000"
TEST_RESULTS = []

def testar_endpoint_com_campos(description, method, endpoint, data=None, expected_fields=None):
    """Testa endpoint e verifica se os campos estão padronizados"""
    print(f"\n🔍 {description}")
    print(f"   {method} {endpoint}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=data, timeout=10)
        elif method == "POST":
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"   📊 Status: {response.status_code}")
        
        try:
            response_data = response.json()
        except:
            print(f"   ❌ Resposta não é JSON válido")
            return False
        
        # Verificar estrutura de resposta padronizada
        if 'success' in response_data:
            success = response_data.get('success')
            message = response_data.get('message', '')
            error = response_data.get('error')
            data_content = response_data.get('data', {})
            
            print(f"   ✅ Estrutura padronizada: success={success}")
            if success:
                print(f"   📝 Mensagem: {message}")
                if expected_fields and data_content:
                    verificar_campos_esperados(data_content, expected_fields)
            else:
                print(f"   ❌ Erro: {error}")
        else:
            print(f"   ⚠️  Resposta sem campo 'success' (formato legado)")
            if expected_fields:
                verificar_campos_esperados(response_data, expected_fields)
        
        TEST_RESULTS.append({
            'description': description,
            'status_code': response.status_code,
            'has_standard_structure': 'success' in response_data,
            'success': response_data.get('success', None)
        })
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERRO: Servidor não está rodando")
        return False
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        return False

def verificar_campos_esperados(data, expected_fields):
    """Verifica se os campos esperados estão presentes"""
    print(f"   🔍 Verificando campos esperados...")
    
    for field in expected_fields:
        if field in data:
            print(f"   ✅ Campo '{field}' presente")
        else:
            print(f"   ❌ Campo '{field}' AUSENTE")

def main():
    print("🚀 TESTANDO CORREÇÃO DOS CAMPOS PADRONIZADOS")
    print("=" * 60)
    print(f"🌐 Servidor: {BASE_URL}")
    print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # ================================================================
    # TESTE 1: VERIFICAR RESPOSTA PADRONIZADA - LOGIN OPERADOR
    # ================================================================
    print("\n📋 TESTE 1: LOGIN OPERADOR (RESPOSTA PADRONIZADA)")
    
    testar_endpoint_com_campos(
        "Login operador com dados inválidos",
        "POST",
        "/api/nr12/bot/operador/login/",
        data={"nome": "Teste Inexistente", "data_nascimento": "01/01/1990"},
        expected_fields=['success', 'message', 'error', 'data']
    )
    
    # ================================================================
    # TESTE 2: VERIFICAR CAMPOS PADRONIZADOS - EQUIPAMENTO
    # ================================================================
    print("\n📋 TESTE 2: ACESSO A EQUIPAMENTO (CAMPOS PADRONIZADOS)")
    
    testar_endpoint_com_campos(
        "Acesso a equipamento (deve ter equipamento, checklists_hoje, acoes_disponiveis)",
        "GET",
        "/api/nr12/bot/equipamento/1/",
        expected_fields=['equipamento', 'checklists_hoje', 'acoes_disponiveis']
    )
    
    # ================================================================
    # TESTE 3: VERIFICAR CAMPOS DE CHECKLIST
    # ================================================================
    print("\n📋 TESTE 3: LISTA DE CHECKLISTS (CAMPOS PADRONIZADOS)")
    
    testar_endpoint_com_campos(
        "Lista checklists - verificar campo data_checklist (não data_realizacao)",
        "GET",
        "/api/nr12/checklists/",
        expected_fields=['results']
    )
    
    # ================================================================
    # TESTE 4: VERIFICAR CRIAÇÃO DE CHECKLIST COM CAMPOS CORRETOS
    # ================================================================
    print("\n📋 TESTE 4: CRIAÇÃO DE CHECKLIST (CAMPOS PADRONIZADOS)")
    
    testar_endpoint_com_campos(
        "Criar checklist com campos padronizados",
        "POST",
        "/api/nr12/bot/equipamento/1/",
        data={
            "acao": "criar_checklist",
            "operador_codigo": "OP001",
            "turno": "MANHA",
            "data_checklist": date.today().isoformat(),  # ✅ CAMPO PADRONIZADO
            "observacoes": "Teste de padronização"
        },
        expected_fields=['checklist_id', 'uuid', 'data']
    )
    
    # ================================================================
    # TESTE 5: VERIFICAR ATUALIZAÇÃO DE ITEM
    # ================================================================
    print("\n📋 TESTE 5: ATUALIZAÇÃO DE ITEM (ENDPOINT CORRETO)")
    
    testar_endpoint_com_campos(
        "Atualizar item de checklist",
        "POST",
        "/api/nr12/bot/item-checklist/atualizar/",
        data={
            "item_id": 1,
            "status": "OK",
            "operador_codigo": "OP001",
            "observacao": "Teste de atualização"
        },
        expected_fields=['item_atualizado', 'proximo_item', 'checklist_status']
    )
    
    # ================================================================
    # TESTE 6: VERIFICAR ESTRUTURA DE RESPOSTA DA API
    # ================================================================
    print("\n📋 TESTE 6: ESTRUTURA DA API RAIZ")
    
    testar_endpoint_com_campos(
        "API raiz - informações do bot",
        "GET",
        "/api/",
        expected_fields=['bot_telegram', 'endpoints_principais']
    )
    
    # ================================================================
    # ANÁLISE DOS RESULTADOS
    # ================================================================
    print("\n" + "=" * 60)
    print("📊 ANÁLISE DOS RESULTADOS")
    print("=" * 60)
    
    total = len(TEST_RESULTS)
    com_estrutura_padrao = len([r for r in TEST_RESULTS if r['has_standard_structure']])
    sucessos = len([r for r in TEST_RESULTS if r['success'] == True])
    
    print(f"📋 Total de testes: {total}")
    print(f"✅ Com estrutura padronizada (campo 'success'): {com_estrutura_padrao}")
    print(f"🎯 Sucessos (success=True): {sucessos}")
    
    # Verificar problemas específicos
    problemas = []
    
    if com_estrutura_padrao < total:
        problemas.append(f"❌ {total - com_estrutura_padrao} endpoints SEM estrutura padronizada")
    
    # Verificar se servidor está rodando
    connection_errors = len([r for r in TEST_RESULTS if r['status_code'] == 'CONNECTION_ERROR'])
    if connection_errors > 0:
        problemas.append(f"🔌 {connection_errors} testes falharam por conexão")
    
    if problemas:
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   {problema}")
    
    # ================================================================
    # VERIFICAÇÕES ESPECÍFICAS DE CAMPOS
    # ================================================================
    print(f"\n🔍 VERIFICAÇÕES ESPECÍFICAS:")
    print(f"1. ✅ Endpoints do bot devem usar estrutura: {{'success': bool, 'message': str, 'error': str|null, 'data': dict}}")
    print(f"2. ✅ Campo de data deve ser 'data_checklist' (não 'data_realizacao')")
    print(f"3. ✅ Responses devem ser consistentes entre todos os endpoints")
    print(f"4. ✅ Campos de equipamento, operador e checklist padronizados")
    
    # ================================================================
    # RECOMENDAÇÕES
    # ================================================================
    print(f"\n💡 RECOMENDAÇÕES:")
    
    if com_estrutura_padrao == total:
        print(f"✅ EXCELENTE: Todos os endpoints usam estrutura padronizada!")
    else:
        print(f"🔧 Aplicar BotResponseSerializer nos endpoints restantes")
    
    if connection_errors == 0:
        print(f"✅ Servidor está funcionando corretamente")
    else:
        print(f"🚨 Execute 'python manage.py runserver' antes de rodar o teste")
    
    # Resultado final
    if com_estrutura_padrao == total and connection_errors == 0:
        resultado = "✅ CORREÇÃO 2 APLICADA COM SUCESSO"
    else:
        resultado = "⚠️  CORREÇÃO 2 PRECISA DE AJUSTES"
    
    print(f"\n🎯 RESULTADO FINAL: {resultado}")
    
    # ================================================================
    # PRÓXIMOS PASSOS
    # ================================================================
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print(f"1. Se todos os testes passaram: prosseguir para Correção 3")
    print(f"2. Se há problemas: aplicar as correções nos arquivos indicados")
    print(f"3. Re-executar este teste até todos passarem")
    print(f"4. Testar integração com bot Telegram")

if __name__ == "__main__":
    main()