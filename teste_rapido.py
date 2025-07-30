# ===============================================
# SCRIPT DE TESTE RÁPIDO - 5 MINUTOS
# CRIAR: teste_rapido.py (na raiz do projeto)
# ===============================================

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'mandacaru_bot'))

def print_header(titulo):
    print("\n" + "="*60)
    print(f"🧪 {titulo}")
    print("="*60)

def print_check(texto, status):
    emoji = "✅" if status else "❌"
    print(f"{emoji} {texto}")
    return status

async def teste_completo():
    """Executa bateria completa de testes"""
    
    print_header("TESTE RÁPIDO - BOT MANDACARU")
    
    todos_ok = True
    
    # ========================================
    # 1. VERIFICAR ARQUIVO .ENV
    # ========================================
    print("\n📋 1. VERIFICANDO CONFIGURAÇÕES...")
    
    env_path = Path('.env')
    if env_path.exists():
        print_check("Arquivo .env encontrado", True)
        
        # Ler variáveis importantes
        with open('.env', 'r') as f:
            env_content = f.read()
        
        checks = [
            ('TELEGRAM_BOT_TOKEN', 'Token do bot configurado'),
            ('API_BASE_URL', 'URL da API configurada'),
            ('TELEGRAM_BOT_USERNAME', 'Username do bot configurado')
        ]
        
        for var, desc in checks:
            if var in env_content and not env_content.split(f'{var}=')[1].split('\n')[0].strip() == '':
                print_check(desc, True)
            else:
                print_check(f"{desc} - FALTANDO!", False)
                todos_ok = False
    else:
        print_check("Arquivo .env - FALTANDO!", False)
        todos_ok = False
    
    # ========================================
    # 2. VERIFICAR ESTRUTURA DE ARQUIVOS
    # ========================================
    print("\n📁 2. VERIFICANDO ESTRUTURA...")
    
    arquivos_necessarios = [
        'mandacaru_bot/core/config.py',
        'mandacaru_bot/core/db.py', 
        'mandacaru_bot/bot_main/handlers.py',
        'mandacaru_bot/start.py',
        'backend/apps/operadores/models.py',
        'backend/apps/equipamentos/models.py'
    ]
    
    for arquivo in arquivos_necessarios:
        existe = Path(arquivo).exists()
        print_check(f"Arquivo {arquivo}", existe)
        if not existe:
            todos_ok = False
    
    # ========================================
    # 3. TESTAR IMPORTS DO BOT
    # ========================================
    print("\n🐍 3. TESTANDO IMPORTS...")
    
    try:
        # Simular imports do bot
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        
        import django
        django.setup()
        
        # Testar imports Django
        from backend.apps.operadores.models import Operador
        from backend.apps.equipamentos.models import Equipamento
        print_check("Imports Django OK", True)
        
        # Testar se existem dados
        op_count = Operador.objects.count()
        eq_count = Equipamento.objects.count()
        print_check(f"Operadores cadastrados: {op_count}", op_count > 0)
        print_check(f"Equipamentos cadastrados: {eq_count}", eq_count > 0)
        
        if op_count == 0 or eq_count == 0:
            print("💡 DICA: Execute 'python manage.py loaddata fixtures/dados_teste.json'")
        
    except Exception as e:
        print_check(f"Imports Django - ERRO: {e}", False)
        todos_ok = False
    
    # ========================================
    # 4. TESTAR API
    # ========================================
    print("\n🌐 4. TESTANDO API...")
    
    try:
        api_url = "http://127.0.0.1:8000/api"
        
        async with httpx.AsyncClient() as client:
            # Testar endpoint principal
            response = await client.get(f"{api_url}/", timeout=5)
            api_ok = response.status_code == 200
            print_check("API principal respondendo", api_ok)
            
            if api_ok:
                # Testar endpoints específicos
                endpoints = [
                    ('operadores/', 'Endpoint operadores'),
                    ('equipamentos/', 'Endpoint equipamentos')
                ]
                
                for endpoint, desc in endpoints:
                    try:
                        resp = await client.get(f"{api_url}/{endpoint}", timeout=5)
                        endpoint_ok = resp.status_code == 200
                        print_check(desc, endpoint_ok)
                        
                        if endpoint_ok and endpoint == 'equipamentos/':
                            data = resp.json()
                            if 'results' in data and len(data['results']) > 0:
                                eq = data['results'][0]
                                print(f"   📌 Exemplo: {eq.get('nome', 'N/A')} (UUID: {eq.get('uuid', 'N/A')[:8]}...)")
                    except Exception as e:
                        print_check(f"{desc} - ERRO: {e}", False)
                        todos_ok = False
            else:
                print_check("API não está rodando", False)
                todos_ok = False
                
    except Exception as e:
        print_check(f"Teste API - ERRO: {e}", False)
        todos_ok = False
    
    # ========================================
    # 5. TESTAR CONFIGURAÇÃO DO BOT
    # ========================================
    print("\n🤖 5. TESTANDO CONFIGURAÇÃO BOT...")
    
    try:
        # Verificar se consegue importar configurações
        if Path('mandacaru_bot/core/config.py').exists():
            sys.path.insert(0, 'mandacaru_bot')
            from core.config import TELEGRAM_TOKEN, API_BASE_URL
            
            print_check("Configurações do bot carregadas", True)
            print_check("Token configurado", bool(TELEGRAM_TOKEN))
            print_check("API URL configurada", bool(API_BASE_URL))
            
            # Testar se token parece válido
            if TELEGRAM_TOKEN and ':' in TELEGRAM_TOKEN:
                print_check("Formato do token válido", True)
            else:
                print_check("Formato do token inválido", False)
                todos_ok = False
                
        else:
            print_check("Arquivo de configuração do bot", False)
            todos_ok = False
            
    except Exception as e:
        print_check(f"Configuração do bot - ERRO: {e}", False)
        todos_ok = False
    
    # ========================================
    # 6. RESULTADO FINAL
    # ========================================
    print_header("RESULTADO DO TESTE")
    
    if todos_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ Sistema pronto para implementar QR Code")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Implementar handler QR Code no bot")
        print("   2. Adicionar endpoint UUID no Django")
        print("   3. Gerar QR codes dos equipamentos")
        print("   4. Testar fluxo completo")
    else:
        print("⚠️  ALGUNS PROBLEMAS ENCONTRADOS")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("   1. Corrigir problemas listados acima")
        print("   2. Verificar configurações do .env")
        print("   3. Confirmar se Django está rodando")
        print("   4. Re-executar este teste")
    
    return todos_ok

# ===============================================
# FUNÇÃO AUXILIAR PARA CRIAR DADOS DE TESTE
# ===============================================

def criar_dados_teste():
    """Cria dados básicos para teste"""
    print_header("CRIANDO DADOS DE TESTE")
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()
        
        from backend.apps.operadores.models import Operador
        from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
        from datetime import date
        import uuid
        
        # Criar categoria se não existir
        categoria, created = CategoriaEquipamento.objects.get_or_create(
            nome="Escavadeira",
            defaults={'descricao': 'Equipamentos de escavação'}
        )
        if created:
            print_check("Categoria 'Escavadeira' criada", True)
        
        # Criar operador teste se não existir
        if not Operador.objects.filter(nome__icontains="teste").exists():
            operador = Operador.objects.create(
                nome="João Silva Teste",
                data_nascimento=date(1990, 5, 15),
                status="ATIVO",
                ativo_bot=True
            )
            print_check(f"Operador teste criado: {operador.codigo}", True)
        
        # Criar equipamento teste se não existir
        if not Equipamento.objects.filter(nome__icontains="teste").exists():
            equipamento = Equipamento.objects.create(
                nome="Escavadeira CAT 320D - TESTE",
                numero_serie="TEST001",
                modelo="320D",
                fabricante="Caterpillar",
                categoria=categoria,
                ativo_nr12=True,
                uuid=uuid.uuid4()
            )
            print_check(f"Equipamento teste criado: {equipamento.codigo}", True)
        
        print("\n✅ Dados de teste criados com sucesso!")
        
    except Exception as e:
        print_check(f"Erro ao criar dados: {e}", False)

# ===============================================
# SCRIPT PRINCIPAL
# ===============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste rápido do sistema Bot + API')
    parser.add_argument('--criar-dados', action='store_true', help='Criar dados de teste')
    
    args = parser.parse_args()
    
    if args.criar_dados:
        criar_dados_teste()
    
    # Executar testes
    sucesso = asyncio.run(teste_completo())
    
    # Exit code
    sys.exit(0 if sucesso else 1)

# ===============================================
# COMO EXECUTAR:
# python teste_rapido.py
# python teste_rapido.py --criar-dados
# ===============================================