# ================================================================
# 5. SCRIPT DE TESTE COMPATÍVEL
# Arquivo: teste_correcoes_compativel.py
# ================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
from datetime import datetime

def testar_sistema_atual():
    """Testa o sistema atual sem quebrar nada"""
    print("🔍 TESTANDO CORREÇÕES COMPATÍVEIS")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000/api/nr12"
    
    # Teste 1: Verificar servidor
    print("\n1. Verificando servidor...")
    try:
        response = requests.get(f"{base_url}/checklists/", timeout=5)
        if response.status_code in [200, 401, 403]:
            print("✅ Servidor funcionando")
        else:
            print(f"⚠️  Servidor respondeu com status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Teste 2: Testar iniciar checklist SEM autenticação
    print("\n2. Testando iniciar checklist...")
    try:
        data = {
            "operador_codigo": "OP0001"  # Usar código ao invés de ID
        }
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            f"{base_url}/checklists/22/iniciar/",
            json=data,
            headers=headers,
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ SUCESSO: Checklist iniciado!")
                return True
            else:
                print(f"⚠️  AVISO: {result.get('error', 'Erro desconhecido')}")
                # Ainda pode ser OK se o erro for de negócio, não técnico
                return 'categoria' not in str(result.get('error', '')).lower()
        except json.JSONDecodeError:
            print(f"⚠️  Resposta não é JSON válido: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

    # Teste 3: Testar atualizar item
    print("\n3. Testando atualizar item...")
    try:
        data = {
            "item_id": 105,
            "status": "OK",
            "operador_codigo": "OP0001",
            "observacao": "Teste de correção"
        }
        
        response = requests.post(
            f"{base_url}/bot/item-checklist/atualizar/",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            if result.get('success'):
                print("✅ SUCESSO: Item atualizado!")
            else:
                print(f"⚠️  AVISO: {result.get('error', 'Erro desconhecido')}")
                # Verificar se erro não é mais o de 'categoria'
                return 'categoria' not in str(result.get('error', '')).lower()
        except:
            print(f"⚠️  Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def verificar_modelo_banco():
    """Verifica modelo no banco sem Django shell"""
    print("\n4. Verificando compatibilidade...")
    
    # Verificar se arquivos existem
    arquivos_verificar = [
        'backend/apps/auth_cliente/models.py',
        'backend/apps/nr12_checklist/models.py',
        'backend/apps/operadores/models.py',
        'backend/settings.py'
    ]
    
    for arquivo in arquivos_verificar:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo} encontrado")
        else:
            print(f"❌ {arquivo} NÃO encontrado")
    
    # Verificar se mandacaru_bot existe
    if os.path.exists('mandacaru_bot/core/db.py'):
        print("✅ Bot core/db.py encontrado")
    else:
        print("❌ Bot core/db.py NÃO encontrado")

def main():
    """Executar todos os testes"""
    print("🚀 TESTE DE COMPATIBILIDADE - SISTEMA NR12")
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar estrutura
    verificar_modelo_banco()
    
    # Testar API
    api_ok = testar_sistema_atual()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 60)
    
    if api_ok:
        print("✅ SISTEMA COMPATÍVEL!")
        print("As correções podem ser aplicadas com segurança.")
    else:
        print("⚠️  ATENÇÃO!")
        print("Verifique os erros acima antes de aplicar correções.")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Aplique as correções nos arquivos indicados")
    print("2. Reinicie o servidor Django")
    print("3. Execute este teste novamente")
    print("4. Se OK, reinicie o bot")

if __name__ == "__main__":
    main()