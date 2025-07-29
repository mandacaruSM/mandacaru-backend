# scripts/testar_api_corrigido.py

import os
import json
import httpx
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api')
print(f"🔌 Testando API em: {API_BASE_URL}\n")

# Dados do operador real
OPERADOR_CODIGO = "OP0001"  # Código correto com 4 zeros
OPERADOR_CHAT_ID = "853870420"  # Chat ID real do operador

print("🧪 TESTE DE API PARA BOT TELEGRAM - DADOS REAIS")
print("="*50)

def verificar_servidor():
    """Verifica se o Django está rodando"""
    print("🔍 Verificando servidor Django...")
    try:
        response = httpx.get("http://127.0.0.1:8000/admin/", timeout=5.0)
        if response.status_code in [200, 301, 302]:
            print("✅ Servidor Django está rodando!")
            return True
    except:
        print("❌ Servidor Django NÃO está rodando!")
        print("   Execute: python manage.py runserver")
        return False

def testar_login_operador():
    """Testa login com operador real"""
    print("\n1️⃣ Testando login de operador...")
    print(f"   Usando código: {OPERADOR_CODIGO}")
    
    try:
        response = httpx.post(
            "http://127.0.0.1:8000/bot/operador/login/",
            json={
                "qr_code": OPERADOR_CODIGO,
                "chat_id": "123456789"  # Novo chat ID para teste
            },
            timeout=10.0
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LOGIN FUNCIONOU!")
            print(f"   Mensagem: {data.get('message')}")
            
            if 'operador' in data:
                op = data['operador']
                print(f"\n   Dados do operador:")
                print(f"   - ID: {op.get('id')}")
                print(f"   - Nome: {op.get('nome')}")
                print(f"   - Código: {op.get('codigo')}")
                print(f"   - Chat ID: {op.get('chat_id')}")
                print(f"   - Ativo: {op.get('ativo')}")
                
                # Guardar ID para próximo teste
                return op.get('id')
        else:
            try:
                data = response.json()
                print(f"   ❌ Erro: {data}")
            except:
                print(f"   ❌ Erro: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    return None

def testar_acesso_equipamento(operador_id):
    """Testa acesso a equipamento"""
    print("\n2️⃣ Testando acesso a equipamento...")
    
    if not operador_id:
        print("   ⚠️ Pulando teste - sem ID de operador")
        return
    
    try:
        # Primeiro, tentar com o operador pelo ID
        response = httpx.post(
            "http://127.0.0.1:8000/bot/equipamento/1/",
            json={
                "operador_id": operador_id,
                "acao": "visualizar"
            },
            timeout=10.0
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Equipamento acessado!")
            
            if 'equipamento' in data:
                eq = data['equipamento']
                print(f"\n   Dados do equipamento:")
                for key, value in eq.items():
                    if value is not None:
                        print(f"   - {key}: {value}")
        else:
            try:
                data = response.json()
                print(f"   ❌ Erro: {data}")
                
                # Tentar com código do operador
                print("\n   Tentando com código do operador...")
                response2 = httpx.post(
                    "http://127.0.0.1:8000/bot/equipamento/1/",
                    json={
                        "codigo_operador": OPERADOR_CODIGO,
                        "acao": "visualizar"
                    },
                    timeout=10.0
                )
                
                if response2.status_code == 200:
                    print("   ✅ Funcionou com código!")
                else:
                    print(f"   ❌ Também falhou: {response2.json()}")
                    
            except:
                print(f"   ❌ Erro: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")

def testar_api_operadores():
    """Testa API geral de operadores"""
    print("\n3️⃣ Testando API de operadores...")
    
    try:
        response = httpx.get(
            f"{API_BASE_URL}/operadores/",
            timeout=10.0
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                data = response.json()
                
                # Verificar formato da resposta
                if isinstance(data, dict) and 'results' in data:
                    # Formato paginado
                    count = data.get('count', 0)
                    results = data.get('results', [])
                    print(f"   ✅ Total de operadores: {count}")
                    
                    if results:
                        print(f"   Primeiro operador: {results[0].get('nome', 'N/A')}")
                elif isinstance(data, list):
                    # Lista direta
                    print(f"   ✅ Total de operadores: {len(data)}")
                    
                    if data:
                        print(f"   Primeiro operador: {data[0].get('nome', 'N/A')}")
                else:
                    print(f"   ⚠️ Formato desconhecido: {type(data)}")
            else:
                print(f"   ⚠️ Resposta não é JSON. Content-Type: {content_type}")
                
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def mostrar_comandos_curl():
    """Mostra comandos curl para teste manual"""
    print("\n💡 COMANDOS CURL PARA TESTE MANUAL:")
    
    print(f"\n# Login com operador real:")
    print(f'curl -X POST http://127.0.0.1:8000/bot/operador/login/ \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"qr_code": "{OPERADOR_CODIGO}", "chat_id": "123456789"}}\'')
    
    print(f"\n# Acesso a equipamento:")
    print(f'curl -X POST http://127.0.0.1:8000/bot/equipamento/1/ \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"operador_id": 9, "acao": "visualizar"}}\'')

# Executar testes
if __name__ == "__main__":
    if verificar_servidor():
        operador_id = testar_login_operador()
        testar_acesso_equipamento(operador_id)
        testar_api_operadores()
        mostrar_comandos_curl()
        
        print("\n✅ Testes concluídos!")
        print("\n🤖 Agora você pode testar o bot no Telegram:")
        print("   python manage.py run_telegram_bot --debug")