# scripts/verificar_operador_teste.py

import os
import sys
import django
import json
import httpx

# Configurar Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento

print("🔍 VERIFICANDO DADOS PARA TESTE DO BOT")
print("="*50)

# 1. Listar operadores
print("\n📋 OPERADORES CADASTRADOS:")
operadores = Operador.objects.all()
for op in operadores:
    print(f"\n  ID: {op.id}")
    print(f"  Nome: {op.nome}")
    print(f"  Código: {op.codigo}")
    print(f"  Status: {op.status}")
    print(f"  Ativo Bot: {op.ativo_bot}")
    print(f"  Chat ID: {op.chat_id_telegram}")
    
    # Testar método verificar_qr_code
    if hasattr(Operador, 'verificar_qr_code'):
        resultado = Operador.verificar_qr_code(op.codigo)
        print(f"  Teste verificar_qr_code('{op.codigo}'): {'✅ OK' if resultado else '❌ Falhou'}")

# 2. Criar operador de teste se não existir
if operadores.count() == 0 or not Operador.objects.filter(codigo='OP001').exists():
    print("\n🔨 CRIANDO OPERADOR DE TESTE...")
    try:
        op_teste = Operador.objects.create(
            nome="Operador Teste Bot",
            codigo="OP001",
            status="ATIVO",
            ativo_bot=True,
            funcao="Operador",
            data_admissao="2023-01-01",
            data_nascimento="1990-01-01"
        )
        print("✅ Operador de teste criado!")
    except Exception as e:
        print(f"❌ Erro ao criar operador: {e}")

# 3. Listar equipamentos
print("\n🔧 EQUIPAMENTOS CADASTRADOS:")
equipamentos = Equipamento.objects.filter(ativo_nr12=True)
for eq in equipamentos:
    print(f"\n  ID: {eq.id}")
    print(f"  Número Série: {eq.numero_serie}")
    print(f"  Modelo: {eq.modelo}")
    print(f"  Ativo NR12: {eq.ativo_nr12}")

# 4. Testar login com dados reais
print("\n🧪 TESTANDO LOGIN COM DADOS REAIS:")

# Pegar o primeiro operador ativo
operador_teste = Operador.objects.filter(status='ATIVO', ativo_bot=True).first()
if operador_teste:
    print(f"\nUsando operador: {operador_teste.nome} (código: {operador_teste.codigo})")
    
    # Testar via API
    try:
        response = httpx.post(
            "http://127.0.0.1:8000/bot/operador/login/",
            json={
                "qr_code": operador_teste.codigo,
                "chat_id": "123456789"
            },
            timeout=10.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN FUNCIONOU!")
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            data = response.json()
            print(f"❌ Erro: {data}")
            
            # Debug do método verificar_qr_code
            print("\n🔍 DEBUG DO MÉTODO verificar_qr_code:")
            print(f"  - Tentando com código: '{operador_teste.codigo}'")
            
            # Testar diretamente
            resultado = Operador.verificar_qr_code(operador_teste.codigo)
            print(f"  - Resultado direto: {resultado}")
            
            # Verificar filtros
            print(f"\n  Verificando filtros:")
            print(f"  - Total operadores: {Operador.objects.count()}")
            print(f"  - Com status ATIVO: {Operador.objects.filter(status='ATIVO').count()}")
            print(f"  - Com ativo_bot=True: {Operador.objects.filter(ativo_bot=True).count()}")
            print(f"  - Com código '{operador_teste.codigo}': {Operador.objects.filter(codigo=operador_teste.codigo).count()}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
else:
    print("❌ Nenhum operador ativo encontrado!")

# 5. Sugestões de teste manual
print("\n💡 COMANDOS PARA TESTE MANUAL:")
if operador_teste:
    print(f"\n# Teste com operador real (código: {operador_teste.codigo}):")
    print(f'curl -X POST http://127.0.0.1:8000/bot/operador/login/ \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"qr_code": "{operador_teste.codigo}", "chat_id": "123456789"}}\'')

print("\n" + "="*50)