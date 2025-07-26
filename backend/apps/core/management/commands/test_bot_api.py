#!/usr/bin/env python3
# test_bot_api.py - Script para testar os endpoints do bot

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000/api/nr12/bot"
HEADERS = {"Content-Type": "application/json"}

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testando: {name}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️ {msg}{Colors.ENDC}")

def print_json(data):
    print(f"{Colors.OKBLUE}{json.dumps(data, indent=2, ensure_ascii=False)}{Colors.ENDC}")

# Testes
def test_operador_login():
    """Testa login de operador"""
    print_test("Login de Operador")
    
    # Teste com código direto
    data = {
        "qr_code": "OP0001",
        "chat_id": "123456789"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/operador/login/", 
                               json=data, 
                               headers=HEADERS)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Login realizado com sucesso!")
                print_info(f"Operador: {result['operador']['nome']}")
                return result['operador']['codigo']
            else:
                print_error(f"Login falhou: {result.get('error')}")
        else:
            print_error(f"Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print_error(f"Erro na requisição: {e}")
    
    return None

def test_equipamento_acesso(operador_codigo):
    """Testa acesso a equipamento"""
    print_test("Acesso a Equipamento")
    
    equipamento_id = 1  # ID do equipamento de teste
    
    try:
        # GET - Obter informações
        response = requests.get(
            f"{BASE_URL}/equipamento/{equipamento_id}/",
            params={"operador": operador_codigo}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Equipamento acessado!")
                print_info(f"Modelo: {result['equipamento']['modelo']}")
                print_info(f"Ações disponíveis: {len(result['acoes_disponiveis'])}")
                print_json(result['acoes_disponiveis'])
                return True
            else:
                print_error(f"Erro: {result.get('error')}")
        else:
            print_error(f"Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print_error(f"Erro na requisição: {e}")
    
    return False

def test_criar_checklist(operador_codigo):
    """Testa criação de checklist"""
    print_test("Criar Checklist")
    
    equipamento_id = 1
    data = {
        "acao": "criar_checklist",
        "operador_codigo": operador_codigo,
        "turno": "MANHA",
        "frequencia": "DIARIA"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/equipamento/{equipamento_id}/",
            json=data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Checklist criado!")
                print_info(f"ID: {result['checklist']['id']}")
                print_info(f"Total de itens: {result['checklist']['total_itens']}")
                return result['checklist']['id']
            else:
                print_error(f"Erro: {result.get('error')}")
        else:
            print_error(f"Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print_error(f"Erro na requisição: {e}")
    
    return None

def test_atualizar_item(operador_codigo, item_id=1):
    """Testa atualização de item"""
    print_test("Atualizar Item Checklist")
    
    data = {
        "item_id": item_id,
        "status": "OK",
        "observacao": "Teste via script",
        "operador_codigo": operador_codigo
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/item-checklist/atualizar/",
            json=data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Item atualizado!")
                print_info(f"Status: {result['item_atualizado']['status']}")
                print_info(f"Progresso: {result['checklist']['percentual']}%")
                if result.get('proximo_item'):
                    print_info(f"Próximo: {result['proximo_item']['descricao']}")
                return True
            else:
                print_error(f"Erro: {result.get('error')}")
        else:
            print_error(f"Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print_error(f"Erro na requisição: {e}")
    
    return False

def run_all_tests():
    """Executa todos os testes"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("=" * 50)
    print("🤖 TESTE DA API DO BOT TELEGRAM MANDACARU")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    print_info(f"URL Base: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Login
    operador_codigo = test_operador_login()
    if not operador_codigo:
        print_error("Falha no login. Abortando testes.")
        return
    
    # 2. Acesso equipamento
    if not test_equipamento_acesso(operador_codigo):
        print_error("Falha no acesso ao equipamento.")
        return
    
    # 3. Criar checklist
    checklist_id = test_criar_checklist(operador_codigo)
    if not checklist_id:
        print_warning("Não foi possível criar checklist (pode já existir para hoje)")
    
    # 4. Atualizar item (usando ID fixo para teste)
    test_atualizar_item(operador_codigo, item_id=1)
    
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}")
    print("=" * 50)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 50)
    print(f"{Colors.ENDC}")

if __name__ == "__main__":
    run_all_tests()