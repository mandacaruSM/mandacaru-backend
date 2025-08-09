#!/usr/bin/env python3
# ===============================================
# SCRIPT DE CORREÇÃO DAS CONFIGURAÇÕES
# Executa automaticamente as correções necessárias
# ===============================================

import os
import sys
from pathlib import Path
import shutil

def corrigir_configuracoes():
    """Executa todas as correções de configuração necessárias"""
    print("🔧 INICIANDO CORREÇÃO DAS CONFIGURAÇÕES")
    print("=" * 50)
    
    # 1. Verificar e criar .env se necessário
    print("\n📝 1. VERIFICANDO ARQUIVO .env")
    sucesso_env = verificar_criar_env()
    
    # 2. Verificar core/config.py
    print("\n⚙️ 2. VERIFICANDO core/config.py")
    sucesso_config = verificar_config_py()
    
    # 3. Verificar diretórios necessários
    print("\n📁 3. VERIFICANDO DIRETÓRIOS")
    sucesso_dirs = criar_diretorios_necessarios()
    
    # 4. Verificar dependências
    print("\n📦 4. VERIFICANDO DEPENDÊNCIAS")
    sucesso_deps = verificar_dependencias()
    
    # 5. Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DAS CORREÇÕES")
    print("=" * 50)
    
    resultados = {
        "Arquivo .env": sucesso_env,
        "core/config.py": sucesso_config,
        "Diretórios": sucesso_dirs,
        "Dependências": sucesso_deps
    }
    
    sucessos = sum(resultados.values())
    total = len(resultados)
    
    for item, sucesso in resultados.items():
        status = "✅" if sucesso else "❌"
        print(f"   {status} {item}")
    
    print(f"\n📈 Taxa de Sucesso: {sucessos}/{total} ({sucessos/total*100:.1f}%)")
    
    if sucessos == total:
        print("\n🎉 TODAS AS CONFIGURAÇÕES CORRIGIDAS!")
        print("✅ Agora execute: python test_phase1.py")
        return True
    else:
        print("\n⚠️ ALGUMAS CORREÇÕES PRECISAM DE ATENÇÃO MANUAL")
        return False

def verificar_criar_env():
    """Verifica e cria arquivo .env se necessário"""
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if env_path.exists():
        print("   ✅ Arquivo .env já existe")
        
        # Verificar se tem as variáveis essenciais
        with open(env_path, 'r') as f:
            content = f.read()
        
        vars_essenciais = [
            "TELEGRAM_BOT_TOKEN",
            "API_BASE_URL"
        ]
        
        faltando = []
        for var in vars_essenciais:
            if var not in content:
                faltando.append(var)
        
        if faltando:
            print(f"   ⚠️ Variáveis faltando: {', '.join(faltando)}")
            print("   📝 Adicione essas variáveis ao .env")
            return False
        else:
            print("   ✅ Variáveis essenciais presentes")
            return True
    
    elif example_path.exists():
        print("   📝 Copiando .env.example para .env")
        shutil.copy(example_path, env_path)
        print("   ✅ Arquivo .env criado")
        print("   ⚠️ CONFIGURE as variáveis TELEGRAM_BOT_TOKEN e API_BASE_URL")
        return True
    
    else:
        print("   ❌ Nem .env nem .env.example encontrados")
        print("   📝 Criando .env básico...")
        
        conteudo_basico = """# ===============================================
# CONFIGURAÇÕES BÁSICAS DO BOT TELEGRAM
# ===============================================

# Token do Bot Telegram (OBRIGATÓRIO)
# Obtenha em: @BotFather no Telegram
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI

# URL da API Django (OBRIGATÓRIO)
API_BASE_URL=http://127.0.0.1:8000/api

# Configurações opcionais
SESSION_TIMEOUT_HOURS=24
DEBUG=true
LOG_LEVEL=INFO
ADMIN_IDS=123456789,987654321
API_TIMEOUT=30
ITEMS_PER_PAGE=10
"""
        
        with open(env_path, 'w') as f:
            f.write(conteudo_basico)
        
        print("   ✅ Arquivo .env básico criado")
        print("   🚨 CONFIGURE TELEGRAM_BOT_TOKEN antes de continuar!")
        return False

def verificar_config_py():
    """Verifica se core/config.py está correto"""
    config_path = Path("core/config.py")
    
    if not config_path.exists():
        print("   ❌ core/config.py não encontrado")
        return False
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Verificar imports essenciais
    imports_necessarios = [
        "from dotenv import load_dotenv",
        "TELEGRAM_TOKEN",
        "API_BASE_URL"
    ]
    
    problemas = []
    for imp in imports_necessarios:
        if imp not in content:
            problemas.append(imp)
    
    if problemas:
        print(f"   ⚠️ Elementos faltando em config.py: {problemas}")
        return False
    else:
        print("   ✅ core/config.py parece estar correto")
        return True

def criar_diretorios_necessarios():
    """Cria diretórios necessários"""
    diretorios = [
        "logs",
        "temp", 
        "data",
        "reports"
    ]
    
    criados = 0
    for diretorio in diretorios:
        dir_path = Path(diretorio)
        if not dir_path.exists():
            try:
                dir_path.mkdir(exist_ok=True)
                (dir_path / ".gitkeep").touch()
                print(f"   ✅ Criado: {diretorio}/")
                criados += 1
            except Exception as e:
                print(f"   ❌ Erro ao criar {diretorio}: {e}")
                return False
        else:
            print(f"   ✅ Existe: {diretorio}/")
    
    if criados > 0:
        print(f"   📁 {criados} diretórios criados")
    
    return True

def verificar_dependencias():
    """Verifica se dependências estão instaladas"""
    deps_essenciais = [
        ("aiogram", "Framework do bot Telegram"),
        ("httpx", "Cliente HTTP assíncrono"),
        ("python-dotenv", "Carregamento de variáveis .env")
    ]
    
    deps_opcionais = [
        ("psutil", "Monitoramento do sistema"),
        ("python-dateutil", "Utilitários de data")
    ]
    
    essenciais_ok = 0
    opcionais_ok = 0
    
    print("   📦 Dependências essenciais:")
    for dep, desc in deps_essenciais:
        try:
            __import__(dep.replace("-", "_"))
            print(f"      ✅ {dep}: {desc}")
            essenciais_ok += 1
        except ImportError:
            print(f"      ❌ {dep}: {desc}")
            print(f"         Execute: pip install {dep}")
    
    print("   📦 Dependências opcionais:")
    for dep, desc in deps_opcionais:
        try:
            __import__(dep.replace("-", "_"))
            print(f"      ✅ {dep}: {desc}")
            opcionais_ok += 1
        except ImportError:
            print(f"      ⚠️ {dep}: {desc} (opcional)")
    
    # Consideramos sucesso se todas as essenciais estão OK
    return essenciais_ok == len(deps_essenciais)

def verificar_token_telegram():
    """Ajuda o usuário a configurar o token do Telegram"""
    print("\n🤖 COMO OBTER O TOKEN DO TELEGRAM:")
    print("1. Abra o Telegram")
    print("2. Procure por @BotFather")
    print("3. Digite /newbot")
    print("4. Siga as instruções")
    print("5. Copie o token gerado")
    print("6. Cole no arquivo .env na linha TELEGRAM_BOT_TOKEN=")
    print("\nExemplo: TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")

def main():
    """Função principal"""
    try:
        sucesso = corrigir_configuracoes()
        
        if not sucesso:
            print("\n📝 PRÓXIMOS PASSOS MANUAIS:")
            print("1. Configure TELEGRAM_BOT_TOKEN no arquivo .env")
            print("2. Instale dependências faltantes: pip install -r requirements.txt")
            print("3. Execute novamente: python fix_config.py")
            verificar_token_telegram()
        else:
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. python test_phase1.py  # Executar testes")
            print("2. python start.py        # Iniciar o bot")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante correção: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()