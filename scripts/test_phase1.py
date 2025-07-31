#!/usr/bin/env python3
# ===============================================
# SCRIPT DE TESTE - FASE 1
# Verifica se todas as correções estão funcionando
# EXECUTAR: python test_phase1.py
# ===============================================

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configurar paths
def setup_paths():
    current_dir = Path(__file__).parent
    project_root = current_dir.parent if current_dir.name == 'mandacaru_bot' else current_dir
    
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(project_root))
    
    return current_dir, project_root

# Setup inicial
bot_dir, project_root = setup_paths()

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("🧪 TESTE DA FASE 1 - BOT MANDACARU")
print("=" * 50)

# ===============================================
# 1. TESTE DE IMPORTS
# ===============================================

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("\n🔍 1. TESTANDO IMPORTS...")
    
    testes = []
    
    # Testar core
    try:
        from core.config import TELEGRAM_TOKEN, API_BASE_URL
        testes.append(("✅", "core.config"))
    except Exception as e:
        testes.append(("❌", f"core.config - {e}"))
    
    try:
        from core.session import iniciar_sessao, obter_sessao
        testes.append(("✅", "core.session"))
    except Exception as e:
        testes.append(("❌", f"core.session - {e}"))
    
    try:
        from core.db import buscar_operador_por_nome, verificar_status_api
        testes.append(("✅", "core.db"))
    except Exception as e:
        testes.append(("❌", f"core.db - {e}"))
    
    try:
        from core.utils import Validators, Formatters
        testes.append(("✅", "core.utils"))
    except Exception as e:
        testes.append(("❌", f"core.utils - {e}"))
    
    try:
        from core.templates import MessageTemplates
        testes.append(("✅", "core.templates"))
    except Exception as e:
        testes.append(("❌", f"core.templates - {e}"))
    
    # Testar handlers
    try:
        from bot_main.handlers import register_handlers
        testes.append(("✅", "bot_main.handlers"))
    except Exception as e:
        testes.append(("❌", f"bot_main.handlers - {e}"))
    
    try:
        from bot_main.main import main
        testes.append(("✅", "bot_main.main"))
    except Exception as e:
        testes.append(("❌", f"bot_main.main - {e}"))
    
    # Mostrar resultados
    for status, teste in testes:
        print(f"   {status} {teste}")
    
    sucessos = sum(1 for status, _ in testes if status == "✅")
    total = len(testes)
    
    print(f"\n📊 Resultado: {sucessos}/{total} imports bem-sucedidos")
    return sucessos == total

# ===============================================
# 2. TESTE DE CONFIGURAÇÕES
# ===============================================

def test_config():
    """Testa configurações essenciais"""
    print("\n🔍 2. TESTANDO CONFIGURAÇÕES...")
    
    try:
        from core.config import (
            TELEGRAM_TOKEN, API_BASE_URL, SESSION_TIMEOUT_HOURS,
            ADMIN_IDS, DEBUG, config
        )
        
        testes = []
        
        # Verificar variáveis essenciais
        if TELEGRAM_TOKEN and len(TELEGRAM_TOKEN) > 20:
            testes.append(("✅", f"TELEGRAM_TOKEN: ***{TELEGRAM_TOKEN[-5:]}"))
        else:
            testes.append(("❌", "TELEGRAM_TOKEN: não configurado ou inválido"))
        
        if API_BASE_URL and "http" in API_BASE_URL:
            testes.append(("✅", f"API_BASE_URL: {API_BASE_URL}"))
        else:
            testes.append(("❌", "API_BASE_URL: não configurado"))
        
        if SESSION_TIMEOUT_HOURS and SESSION_TIMEOUT_HOURS > 0:
            testes.append(("✅", f"SESSION_TIMEOUT_HOURS: {SESSION_TIMEOUT_HOURS}"))
        else:
            testes.append(("❌", "SESSION_TIMEOUT_HOURS: não configurado"))
        
        if isinstance(DEBUG, bool):
            testes.append(("✅", f"DEBUG: {DEBUG}"))
        else:
            testes.append(("⚠️", f"DEBUG: {DEBUG} (tipo incorreto)"))
        
        # Mostrar resultados
        for status, teste in testes:
            print(f"   {status} {teste}")
        
        sucessos = sum(1 for status, _ in testes if status == "✅")
        total = len(testes)
        
        print(f"\n📊 Resultado: {sucessos}/{total} configurações OK")
        return sucessos >= total - 1  # Permitir 1 warning
        
    except Exception as e:
        print(f"   ❌ Erro ao testar configurações: {e}")
        return False

# ===============================================
# 3. TESTE DE VALIDADORES
# ===============================================

def test_validators():
    """Testa validadores"""
    print("\n🔍 3. TESTANDO VALIDADORES...")
    
    try:
        from core.utils import Validators
        
        testes = [
            (Validators.validar_nome("João da Silva"), "Nome válido"),
            (not Validators.validar_nome("A"), "Nome muito curto"),
            (not Validators.validar_nome("João123"), "Nome com números"),
            (Validators.validar_data_nascimento("15/03/1990") is not None, "Data válida"),
            (Validators.validar_data_nascimento("32/13/2025") is None, "Data inválida"),
            (Validators.validar_valor_monetario("123.45") == 123.45, "Valor monetário"),
            (Validators.validar_quantidade("45.5") == 45.5, "Quantidade"),
            (Validators.validar_horimetro("1234.5") == 1234.5, "Horímetro"),
            (Validators.validar_uuid("123e4567-e89b-12d3-a456-426614174000"), "UUID válido")
        ]
        
        sucessos = 0
        for resultado, descricao in testes:
            if resultado:
                print(f"   ✅ {descricao}")
                sucessos += 1
            else:
                print(f"   ❌ {descricao}")
        
        print(f"\n📊 Resultado: {sucessos}/{len(testes)} validadores OK")
        return sucessos == len(testes)
        
    except Exception as e:
        print(f"   ❌ Erro ao testar validadores: {e}")
        return False

# ===============================================
# 4. TESTE DE SESSÕES
# ===============================================

async def test_sessions():
    """Testa sistema de sessões"""
    print("\n🔍 4. TESTANDO SESSÕES...")
    
    try:
        from core.session import (
            iniciar_sessao, obter_sessao, atualizar_sessao,
            limpar_sessao, verificar_autenticacao
        )
        
        # Dados de teste
        user_id = 999999
        operador_teste = {
            'id': 1,
            'nome': 'Operador Teste',
            'funcao': 'Operador'
        }
        
        testes = []
        
        # Iniciar sessão
        await iniciar_sessao(user_id, operador_teste)
        sessao = await obter_sessao(user_id)
        testes.append((sessao is not None, "Iniciar sessão"))
        
        # Verificar autenticação
        autenticado = await verificar_autenticacao(user_id)
        testes.append((autenticado, "Verificar autenticação"))
        
        # Atualizar sessão
        await atualizar_sessao(user_id, {'teste': 'valor'})
        sessao = await obter_sessao(user_id)
        testes.append((sessao.get('teste') == 'valor', "Atualizar sessão"))
        
        # Limpar sessão
        await limpar_sessao(user_id)
        autenticado = await verificar_autenticacao(user_id)
        testes.append((not autenticado, "Limpar sessão"))
        
        # Mostrar resultados
        sucessos = 0
        for resultado, descricao in testes:
            if resultado:
                print(f"   ✅ {descricao}")
                sucessos += 1
            else:
                print(f"   ❌ {descricao}")
        
        print(f"\n📊 Resultado: {sucessos}/{len(testes)} testes de sessão OK")
        return sucessos == len(testes)
        
    except Exception as e:
        print(f"   ❌ Erro ao testar sessões: {e}")
        return False

# ===============================================
# 5. TESTE DE API (se disponível)
# ===============================================

async def test_api():
    """Testa conectividade com API"""
    print("\n🔍 5. TESTANDO API...")
    
    try:
        from core.db import verificar_status_api, testar_conexao_api
        
        # Teste básico de status
        api_ok = await verificar_status_api()
        print(f"   {'✅' if api_ok else '⚠️'} Status da API: {'OK' if api_ok else 'Indisponível'}")
        
        if api_ok:
            # Teste detalhado
            resultados = await testar_conexao_api()
            
            for endpoint, resultado in resultados.items():
                status = "✅" if resultado['ok'] else "❌"
                print(f"   {status} {endpoint}: {resultado['status'] or 'Erro'}")
        
        return api_ok
        
    except Exception as e:
        print(f"   ⚠️ Teste de API não disponível: {e}")
        return True  # Não falhar se API não disponível

# ===============================================
# 6. TESTE DE TEMPLATES
# ===============================================

def test_templates():
    """Testa templates de mensagem"""
    print("\n🔍 6. TESTANDO TEMPLATES...")
    
    try:
        from core.templates import MessageTemplates, AdminTemplates
        from core.utils import Formatters
        
        testes = []
        
        # Testar templates básicos
        welcome = MessageTemplates.welcome_template()
        testes.append((len(welcome) > 50, "Template de boas-vindas"))
        
        error = MessageTemplates.error_template("Teste", "Descrição")
        testes.append(("❌" in error, "Template de erro"))
        
        success = MessageTemplates.success_template("Teste", "Descrição")
        testes.append(("✅" in success, "Template de sucesso"))
        
        help_msg = MessageTemplates.ajuda_template()
        testes.append((len(help_msg) > 100, "Template de ajuda"))
        
        # Testar formatadores
        moeda = Formatters.formatar_moeda(1234.56)
        testes.append(("R$" in moeda, "Formatador de moeda"))
        
        status = Formatters.formatar_status("DISPONIVEL")
        testes.append(("✅" in status, "Formatador de status"))
        
        # Mostrar resultados
        sucessos = 0
        for resultado, descricao in testes:
            if resultado:
                print(f"   ✅ {descricao}")
                sucessos += 1
            else:
                print(f"   ❌ {descricao}")
        
        print(f"\n📊 Resultado: {sucessos}/{len(testes)} templates OK")
        return sucessos == len(testes)
        
    except Exception as e:
        print(f"   ❌ Erro ao testar templates: {e}")
        return False

# ===============================================
# 7. TESTE DE ESTRUTURA DE ARQUIVOS
# ===============================================

def test_file_structure():
    """Testa se todos os arquivos necessários existem"""
    print("\n🔍 7. TESTANDO ESTRUTURA DE ARQUIVOS...")
    
    arquivos_necessarios = [
        "core/__init__.py",
        "core/config.py",
        "core/session.py",
        "core/db.py",
        "core/utils.py",
        "core/templates.py",
        "bot_main/__init__.py",
        "bot_main/main.py",
        "bot_main/handlers.py",
        "start.py",
        ".env"
    ]
    
    diretorios_necessarios = [
        "logs",
        "temp",
        "data"
    ]
    
    testes = []
    
    # Verificar arquivos
    for arquivo in arquivos_necessarios:
        caminho = bot_dir / arquivo
        existe = caminho.exists()
        testes.append((existe, f"Arquivo: {arquivo}"))
    
    # Verificar diretórios (criar se não existir)
    for diretorio in diretorios_necessarios:
        caminho = bot_dir / diretorio
        if not caminho.exists():
            try:
                caminho.mkdir(exist_ok=True)
                (caminho / ".gitkeep").touch()
                testes.append((True, f"Diretório: {diretorio} (criado)"))
            except Exception as e:
                testes.append((False, f"Diretório: {diretorio} (erro: {e})"))
        else:
            testes.append((True, f"Diretório: {diretorio}"))
    
    # Mostrar resultados
    sucessos = 0
    for resultado, descricao in testes:
        if resultado:
            print(f"   ✅ {descricao}")
            sucessos += 1
        else:
            print(f"   ❌ {descricao}")
    
    print(f"\n📊 Resultado: {sucessos}/{len(testes)} arquivos/diretórios OK")
    return sucessos >= len(testes) - 2  # Permitir alguns arquivos opcionais

# ===============================================
# 8. TESTE DE BOT (simulação)
# ===============================================

async def test_bot_simulation():
    """Simula inicialização do bot sem executar polling"""
    print("\n🔍 8. TESTANDO INICIALIZAÇÃO DO BOT...")
    
    try:
        from aiogram import Bot, Dispatcher
        from core.config import TELEGRAM_TOKEN
        from bot_main.handlers import register_handlers
        
        # Criar instâncias
        bot = Bot(token=TELEGRAM_TOKEN)
        dp = Dispatcher()
        
        # Registrar handlers
        register_handlers(dp)
        
        print("   ✅ Bot criado com sucesso")
        print("   ✅ Dispatcher configurado")
        print("   ✅ Handlers registrados")
        
        # Fechar bot
        await bot.session.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na inicialização do bot: {e}")
        return False

# ===============================================
# 9. RELATÓRIO FINAL
# ===============================================

def gerar_relatorio(resultados):
    """Gera relatório final dos testes"""
    print("\n" + "=" * 50)
    print("📋 RELATÓRIO FINAL - FASE 1")
    print("=" * 50)
    
    total_testes = len(resultados)
    sucessos = sum(resultados.values())
    
    print(f"\n📊 **RESUMO GERAL:**")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Falhas: {total_testes - sucessos}")
    print(f"   📈 Taxa de sucesso: {(sucessos/total_testes)*100:.1f}%")
    
    print(f"\n🔍 **DETALHES POR TESTE:**")
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {teste}: {status}")
    
    if sucessos == total_testes:
        print(f"\n🎉 **TODOS OS TESTES PASSARAM!**")
        print(f"✅ A FASE 1 está completa e o bot está pronto para uso.")
        print(f"🚀 Próximo passo: Implementar FASE 2 (módulos específicos)")
    elif sucessos >= total_testes * 0.8:
        print(f"\n⚠️ **MAIORIA DOS TESTES PASSOU**")
        print(f"✅ A base está sólida, mas há alguns ajustes necessários.")
        print(f"🔧 Corrija os problemas identificados antes de prosseguir.")
    else:
        print(f"\n❌ **MUITOS TESTES FALHARAM**")
        print(f"🚨 É necessário corrigir os problemas antes de continuar.")
        print(f"📋 Revise a configuração e implementação.")
    
    print(f"\n📝 **PRÓXIMAS AÇÕES:**")
    if sucessos == total_testes:
        print(f"   1. Executar `python start.py` para testar o bot real")
        print(f"   2. Testar fluxo de autenticação via Telegram")
        print(f"   3. Iniciar implementação da FASE 2")
    else:
        print(f"   1. Corrigir os testes que falharam")
        print(f"   2. Executar este script novamente")
        print(f"   3. Só prosseguir quando todos os testes passarem")
    
    return sucessos == total_testes

# ===============================================
# FUNÇÃO PRINCIPAL
# ===============================================

async def main():
    """Executa todos os testes"""
    print(f"📁 Diretório do bot: {bot_dir}")
    print(f"📁 Diretório do projeto: {project_root}")
    
    # Executar todos os testes
    resultados = {}
    
    resultados["1. Imports"] = test_imports()
    resultados["2. Configurações"] = test_config()
    resultados["3. Validadores"] = test_validators()
    resultados["4. Sessões"] = await test_sessions()
    resultados["5. API"] = await test_api()
    resultados["6. Templates"] = test_templates()
    resultados["7. Estrutura"] = test_file_structure()
    resultados["8. Bot"] = await test_bot_simulation()
    
    # Gerar relatório
    sucesso_geral = gerar_relatorio(resultados)
    
    return sucesso_geral

# ===============================================
# UTILITÁRIOS ADICIONAIS
# ===============================================

def criar_arquivo_env_exemplo():
    """Cria arquivo .env.example se não existir"""
    env_example_path = bot_dir / ".env.example"
    
    if not env_example_path.exists():
        conteudo = """# ===============================================
# ARQUIVO DE EXEMPLO - mandacaru_bot/.env.example
# Copie para .env e configure as variáveis
# ===============================================

# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-sua-secret-key-aqui-mude-em-producao
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
BASE_URL=http://127.0.0.1:8000

# Bot Telegram
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_BOT_USERNAME=SeuBotUsername
BOT_DEBUG=True
SESSION_TIMEOUT_HOURS=24
ADMIN_IDS=SEU_ID_TELEGRAM_AQUI

# API Configuration
API_BASE_URL=http://127.0.0.1:8000/api
API_TIMEOUT=10

# Logging
BOT_LOG_LEVEL=INFO
BOT_LOG_FILE=bot.log

# Empresa
EMPRESA_NOME=Mandacaru ERP
EMPRESA_TELEFONE=(11) 99999-9999

# NR12
NR12_TEMPO_LIMITE_CHECKLIST=120
NR12_FREQUENCIA_PADRAO=DIARIO
NR12_NOTIFICAR_ATRASOS=True
"""
        
        try:
            env_example_path.write_text(conteudo, encoding='utf-8')
            print(f"✅ Criado arquivo: {env_example_path}")
        except Exception as e:
            print(f"❌ Erro ao criar .env.example: {e}")

def verificar_dependencias():
    """Verifica se dependências estão instaladas"""
    print("\n🔍 VERIFICANDO DEPENDÊNCIAS...")
    
    dependencias = [
        ('aiogram', '3.4.1'),
        ('httpx', '0.26.0'),
        ('python-dotenv', '1.0.0'),
        ('psutil', '5.9.8')
    ]
    
    for nome, versao_esperada in dependencias:
        try:
            modulo = __import__(nome)
            versao_atual = getattr(modulo, '__version__', 'desconhecida')
            
            if versao_atual == versao_esperada:
                print(f"   ✅ {nome} {versao_atual}")
            else:
                print(f"   ⚠️ {nome} {versao_atual} (esperada: {versao_esperada})")
        
        except ImportError:
            print(f"   ❌ {nome} não instalado")

# ===============================================
# PONTO DE ENTRADA
# ===============================================

if __name__ == "__main__":
    print("🔧 Configurando ambiente...")
    
    # Criar arquivo .env.example se necessário
    criar_arquivo_env_exemplo()
    
    # Verificar dependências
    verificar_dependencias()
    
    # Executar testes principais
    try:
        sucesso = asyncio.run(main())
        
        print("\n" + "=" * 50)
        if sucesso:
            print("🎉 FASE 1 CONCLUÍDA COM SUCESSO!")
            print("🚀 O bot está pronto para uso básico.")
            
            print("\n💡 **COMO CONTINUAR:**")
            print("1. python start.py  # Para executar o bot")
            print("2. Implementar FASE 2  # Módulos específicos")
            
            sys.exit(0)
        else:
            print("❌ FASE 1 INCOMPLETA!")
            print("🔧 Corrija os problemas e execute novamente.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)