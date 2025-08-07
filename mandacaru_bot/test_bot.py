# ===============================================
# ARQUIVO: mandacaru_bot/test_bot.py
# Script de teste para validar o bot
# ===============================================

import asyncio
import sys
import logging
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("🔍 Testando imports...")
    
    try:
        print("  ✓ Testando core.config...")
        from core.config import TELEGRAM_TOKEN, API_BASE_URL
        print(f"    Token configurado: {'Sim' if TELEGRAM_TOKEN else 'Não'}")
        print(f"    API URL: {API_BASE_URL}")
        
        print("  ✓ Testando core.session...")
        from core.session import iniciar_sessao, obter_sessao
        
        print("  ✓ Testando core.db...")
        from core.db import verificar_status_api
        
        print("  ✓ Testando core.templates...")
        from core.templates import MessageTemplates
        
        print("  ✓ Testando core.utils...")
        from core.utils import Validators
        
        print("  ✓ Testando bot_main.handlers...")
        from bot_main.handlers import register_handlers
        
        print("  ✓ Testando bot_checklist.handlers...")
        from bot_checklist.handlers import register_handlers as register_checklist
        
        print("  ✓ Testando bot_qr.handlers...")
        from bot_qr.handlers import register_handlers as register_qr
        
        print("  ✓ Testando bot_reports.handlers...")
        from bot_reports.handlers import register_handlers as register_reports
        
        print("✅ Todos os imports funcionaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no import: {e}")
        return False

async def test_api_connection():
    """Testa conexão com a API"""
    print("🌐 Testando conexão com API...")
    
    try:
        from core.db import verificar_status_api
        
        status = await verificar_status_api()
        if status:
            print("✅ Conexão com API funcionando!")
        else:
            print("⚠️ API não está respondendo")
        
        return status
        
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

def test_session_system():
    """Testa sistema de sessões"""
    print("🔐 Testando sistema de sessões...")
    
    try:
        from core.session import (
            iniciar_sessao, obter_sessao, atualizar_sessao,
            autenticar_operador, verificar_autenticacao
        )
        
        # Teste básico de sessão
        test_chat_id = "test_123456"
        
        # Criar sessão
        sessao = iniciar_sessao(test_chat_id)
        print(f"  ✓ Sessão criada: {sessao['chat_id']}")
        
        # Obter sessão
        sessao_obtida = obter_sessao(test_chat_id)
        print(f"  ✓ Sessão obtida: {sessao_obtida is not None}")
        
        # Testar autenticação
        operador_fake = {
            'id': 1,
            'nome': 'Teste',
            'codigo': 'TEST001'
        }
        
        autenticar_operador(test_chat_id, operador_fake)
        autenticado = verificar_autenticacao(test_chat_id)
        print(f"  ✓ Autenticação: {autenticado}")
        
        print("✅ Sistema de sessões funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de sessões: {e}")
        return False

def test_bot_creation():
    """Testa criação do bot (sem conectar)"""
    print("🤖 Testando criação do bot...")
    
    try:
        from aiogram import Bot
        from core.config import TELEGRAM_TOKEN
        
        if not TELEGRAM_TOKEN:
            print("❌ Token do bot não configurado")
            return False
        
        # Criar bot (sem fazer conexão)
        bot = Bot(token=TELEGRAM_TOKEN)
        print("✅ Bot criado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar bot: {e}")
        return False

async def run_tests():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES DO BOT MANDACARU")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports()),
        ("Bot Creation", test_bot_creation()),
        ("Session System", test_session_system()),
        ("API Connection", await test_api_connection()),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            passed += 1
            print(f"✅ {test_name}: PASSOU")
        else:
            print(f"❌ {test_name}: FALHOU")
    
    print("=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n🚀 O bot está pronto para ser executado!")
        print("\n📝 Para executar o bot:")
        print("   python start.py")
        print("   ou")
        print("   python manage.py run_telegram_bot")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("\n🔧 Verifique:")
        print("   1. Arquivo .env configurado")
        print("   2. Token do bot válido")
        print("   3. API Django rodando")
        print("   4. Dependências instaladas")
    
    return passed == total

if __name__ == "__main__":
    # Configurar logging simples
    logging.basicConfig(level=logging.ERROR)
    
    try:
        result = asyncio.run(run_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)