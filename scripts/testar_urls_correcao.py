# ================================================================
# SCRIPT PARA TESTAR A CORREÇÃO DAS URLs
# Salve como: testar_urls_correcao.py
# Execute: python testar_urls_correcao.py
# ================================================================

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://127.0.0.1:8000"
TEST_RESULTS = []

def testar_endpoint(method, url, data=None, expected_status=200, description=""):
    """Testa um endpoint e registra o resultado"""
    print(f"\n🔍 {description}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        status_ok = response.status_code == expected_status
        status_icon = "✅" if status_ok else "❌"
        
        print(f"   {status_icon} Status: {response.status_code} (esperado: {expected_status})")
        
        # Tentar exibir conteúdo JSON se possível
        try:
            content = response.json()
            if len(str(content)) < 200:
                print(f"   📄 Resposta: {content}")
            else:
                print(f"   📄 Resposta: {str(content)[:100]}...")
        except:
            print(f"   📄 Resposta: {response.text[:100]}...")
        
        TEST_RESULTS.append({
            'url': url,
            'method': method,
            'status': response.status_code,
            'success': status_ok,
            'description': description
        })
        
        return status_ok, response
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERRO: Servidor não está rodando em {BASE_URL}")
        TEST_RESULTS.append({
            'url': url,
            'method': method,
            'status': 'CONNECTION_ERROR',
            'success': False,
            'description': description
        })
        return False, None
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        TEST_RESULTS.append({
            'url': url,
            'method': method,
            'status': 'ERROR',
            'success': False,
            'description': description
        })
        return False, None

def main():
    print("🚀 TESTANDO CORREÇÃO DAS URLs - Bot Mandacaru")
    print("=" * 60)
    print(f"🌐 Servidor: {BASE_URL}")
    print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # ================================================================
    # TESTE 1: API RAIZ
    # ================================================================
    print("\n📋 TESTE 1: API RAIZ")
    testar_endpoint(
        "GET", 
        f"{BASE_URL}/api/", 
        description="API raiz com informações do sistema"
    )
    
    # ================================================================
    # TESTE 2: ENDPOINTS DO BOT (NOVOS)
    # ================================================================
    print("\n📋 TESTE 2: ENDPOINTS DO BOT")
    
    # Endpoint de login do operador
    testar_endpoint(
        "POST",
        f"{BASE_URL}/api/nr12/bot/operador/login/",
        data={"nome": "Teste", "data_nascimento": "01/01/1990"},
        expected_status=200,  # Status 200 com erro JSON é correto
        description="Login de operador via bot"
    )
    
    # Endpoint de acesso a equipamento
    testar_endpoint(
        "GET",
        f"{BASE_URL}/api/nr12/bot/equipamento/1/",
        expected_status=400,  # Status 400 é correto (falta parâmetro)
        description="Acesso a equipamento via bot"
    )
    
    # ================================================================
    # TESTE 3: ENDPOINTS WEB PÚBLICOS
    # ================================================================
    print("\n📋 TESTE 3: ENDPOINTS WEB PÚBLICOS")
    
    # Lista de checklists (API REST)
    testar_endpoint(
        "GET",
        f"{BASE_URL}/api/nr12/checklists/",
        expected_status=200,
        description="Lista de checklists (API REST)"
    )
    
    # ================================================================
    # TESTE 4: VERIFICAR SE URLs ANTIGAS AINDA EXISTEM (DEVEM FALHAR)
    # ================================================================
    print("\n📋 TESTE 4: URLs ANTIGAS (DEVEM FALHAR)")
    
    # URLs antigas que NÃO devem mais existir
    urls_antigas = [
        "/api/checklists/",  # Estava em backend/urls.py - DEVE FALHAR
        # "/api/nr12/checklists/" - Esta URL DEVE FUNCIONAR (API REST válida)
    ]
    
    for url in urls_antigas:
        testar_endpoint(
            "GET",
            f"{BASE_URL}{url}",
            expected_status=404,
            description=f"URL antiga (deve falhar): {url}"
        )
    
    # ================================================================
    # RESUMO DOS TESTES
    # ================================================================
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    total = len(TEST_RESULTS)
    sucessos = len([r for r in TEST_RESULTS if r['success']])
    falhas = total - sucessos
    
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"📊 Total: {total}")
    
    if falhas > 0:
        print(f"\n❌ FALHAS ENCONTRADAS:")
        for result in TEST_RESULTS:
            if not result['success']:
                print(f"   - {result['method']} {result['url']} -> {result['status']}")
    
    # Verificar se servidor está rodando
    connection_errors = len([r for r in TEST_RESULTS if r['status'] == 'CONNECTION_ERROR'])
    if connection_errors > 0:
        print(f"\n⚠️  IMPORTANTE: {connection_errors} testes falharam por conexão.")
        print("   Execute 'python manage.py runserver' antes de rodar este teste.")
    
    print(f"\n🎯 RESULTADO: {'✅ CORREÇÃO OK' if falhas == 0 else '❌ NECESSITA AJUSTES'}")

if __name__ == "__main__":
    main()