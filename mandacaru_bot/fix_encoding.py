#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================
# SCRIPT DE CORREÇÃO DE CODIFICAÇÃO
# Corrige problemas de encoding nos arquivos
# ===============================================

import os
import sys
from pathlib import Path
import chardet

def detectar_e_corrigir_encoding():
    """Detecta e corrige problemas de encoding"""
    print("🔧 CORREÇÃO DE CODIFICAÇÃO DE ARQUIVOS")
    print("=" * 50)
    
    # Arquivos para verificar
    arquivos_verificar = [
        "core/config.py",
        "core/session.py", 
        "core/db.py",
        "core/utils.py",
        "core/templates.py",
        "bot_main/handlers.py",
        "bot_main/main.py",
        "bot_checklist/handlers.py"
    ]
    
    arquivos_corrigidos = 0
    
    for arquivo in arquivos_verificar:
        arquivo_path = Path(arquivo)
        if arquivo_path.exists():
            print(f"\n📄 Verificando: {arquivo}")
            if corrigir_encoding_arquivo(arquivo_path):
                arquivos_corrigidos += 1
        else:
            print(f"\n⚠️ Arquivo não encontrado: {arquivo}")
    
    print(f"\n📊 RESULTADO:")
    print(f"✅ {arquivos_corrigidos} arquivos corrigidos/verificados")
    
    if arquivos_corrigidos > 0:
        print("\n🎉 Problemas de codificação corrigidos!")
        print("🚀 Execute novamente: python test_phase1.py")
    else:
        print("\n✅ Nenhuma correção necessária")
    
    return True

def corrigir_encoding_arquivo(arquivo_path):
    """Corrige encoding de um arquivo específico"""
    try:
        # Primeiro, tentar detectar o encoding atual
        with open(arquivo_path, 'rb') as f:
            raw_data = f.read()
        
        # Detectar encoding
        detected = chardet.detect(raw_data)
        encoding_original = detected['encoding']
        confianca = detected['confidence']
        
        print(f"   📍 Encoding detectado: {encoding_original} (confiança: {confianca:.2f})")
        
        # Se confiança é baixa ou encoding problemático
        if confianca < 0.8 or encoding_original in ['ISO-8859-1', 'Windows-1252']:
            print(f"   🔧 Convertendo para UTF-8...")
            
            # Tentar ler com várias codificações
            for enc in [encoding_original, 'iso-8859-1', 'windows-1252', 'cp1252', 'latin1']:
                try:
                    with open(arquivo_path, 'r', encoding=enc) as f:
                        content = f.read()
                    
                    # Salvar como UTF-8 com BOM se necessário
                    with open(arquivo_path, 'w', encoding='utf-8') as f:
                        # Adicionar header UTF-8 se for arquivo Python
                        if arquivo_path.suffix == '.py' and not content.startswith('# -*- coding:'):
                            f.write('# -*- coding: utf-8 -*-\n')
                        f.write(content)
                    
                    print(f"   ✅ Convertido de {enc} para UTF-8")
                    return True
                    
                except UnicodeDecodeError:
                    continue
            
            print(f"   ❌ Não foi possível converter automaticamente")
            return False
        else:
            print(f"   ✅ Encoding OK")
            return True
            
    except Exception as e:
        print(f"   ❌ Erro ao processar arquivo: {e}")
        return False

def criar_config_py_limpo():
    """Cria uma versão limpa do core/config.py"""
    print("\n🛠️ CRIANDO VERSÃO LIMPA DO core/config.py")
    
    config_content = '''# -*- coding: utf-8 -*-
# ===============================================
# ARQUIVO: core/config.py
# Configurações do Bot Telegram Mandacaru
# ===============================================

import os
from dotenv import load_dotenv
from pathlib import Path

# ===============================================
# CARREGAMENTO DO .env
# ===============================================

# Encontrar arquivo .env
current_dir = Path(__file__).parent
project_root = current_dir.parent
env_path = project_root / ".env"

# Tentar locais alternativos se não encontrar
if not env_path.exists():
    alternative_paths = [
        current_dir.parent.parent / ".env",
        Path(".env"),
        Path("../.env")
    ]
    
    for alt_path in alternative_paths:
        if alt_path.exists():
            env_path = alt_path
            break
    else:
        print(f"⚠️ Arquivo .env não encontrado em:")
        print(f"   • {project_root / '.env'}")
        for path in alternative_paths:
            print(f"   • {path}")

# Carregar variáveis do .env
load_dotenv(dotenv_path=env_path)

# ===============================================
# CONFIGURAÇÕES PRINCIPAIS
# ===============================================

# Token do Bot Telegram (obrigatório)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN não encontrado no .env")

# URL da API Django
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_BASE_URL = os.getenv("API_BASE_URL", f"{BASE_URL}/api")

# Timeout para requisições HTTP
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# ===============================================
# CONFIGURAÇÕES DE SESSÃO
# ===============================================

# Timeout de sessão em horas
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))

# Intervalo de limpeza de sessões em minutos
CLEANUP_INTERVAL_MINUTES = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "60"))

# ===============================================
# CONFIGURAÇÕES DE PAGINAÇÃO
# ===============================================

# Itens por página
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))
MAX_ITEMS_PER_PAGE = int(os.getenv("MAX_ITEMS_PER_PAGE", "50"))

# ===============================================
# CONFIGURAÇÕES DE SEGURANÇA
# ===============================================

# Tentativas máximas de login
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))
LOGIN_TIMEOUT_MINUTES = int(os.getenv("LOGIN_TIMEOUT_MINUTES", "15"))

# IDs de administradores
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip().isdigit()]

# ===============================================
# CONFIGURAÇÕES DE DEBUG
# ===============================================

# Modo debug
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ===============================================
# CONFIGURAÇÕES ESPECÍFICAS
# ===============================================

# Empresa
EMPRESA_NOME = os.getenv("EMPRESA_NOME", "Mandacaru ERP")
EMPRESA_TELEFONE = os.getenv("EMPRESA_TELEFONE", "(11) 99999-9999")

# NR12
NR12_TEMPO_LIMITE_CHECKLIST = int(os.getenv("NR12_TEMPO_LIMITE_CHECKLIST", "120"))
NR12_FREQUENCIA_PADRAO = os.getenv("NR12_FREQUENCIA_PADRAO", "DIARIO")
NR12_NOTIFICAR_ATRASOS = os.getenv("NR12_NOTIFICAR_ATRASOS", "True").lower() in ("true", "1", "yes")

# ===============================================
# VALIDAÇÃO DE CONFIGURAÇÕES
# ===============================================

def validar_configuracoes():
    """Valida se todas as configurações essenciais estão presentes"""
    erros = []
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "SEU_TOKEN_AQUI":
        erros.append("TELEGRAM_BOT_TOKEN deve ser configurado")
    
    if not API_BASE_URL:
        erros.append("API_BASE_URL é obrigatório")
    
    if API_TIMEOUT <= 0:
        erros.append("API_TIMEOUT deve ser maior que 0")
    
    if SESSION_TIMEOUT_HOURS <= 0:
        erros.append("SESSION_TIMEOUT_HOURS deve ser maior que 0")
    
    if erros:
        raise ValueError(f"Erros de configuração:\\n" + "\\n".join(f"- {erro}" for erro in erros))

# Executar validação
try:
    validar_configuracoes()
except ValueError as e:
    print(f"❌ {e}")
    print("📝 Configure o arquivo .env corretamente")

# ===============================================
# EXPORTS
# ===============================================

__all__ = [
    "TELEGRAM_TOKEN", "API_BASE_URL", "API_TIMEOUT",
    "SESSION_TIMEOUT_HOURS", "CLEANUP_INTERVAL_MINUTES",
    "ITEMS_PER_PAGE", "MAX_ITEMS_PER_PAGE",
    "MAX_LOGIN_ATTEMPTS", "LOGIN_TIMEOUT_MINUTES",
    "ADMIN_IDS", "DEBUG", "LOG_LEVEL",
    "EMPRESA_NOME", "EMPRESA_TELEFONE",
    "NR12_TEMPO_LIMITE_CHECKLIST", "NR12_FREQUENCIA_PADRAO", "NR12_NOTIFICAR_ATRASOS"
]
'''
    
    try:
        config_path = Path("core/config.py")
        
        # Fazer backup do arquivo original
        if config_path.exists():
            backup_path = config_path.with_suffix('.py.backup')
            config_path.replace(backup_path)
            print(f"   💾 Backup criado: {backup_path}")
        
        # Criar nova versão
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"   ✅ Novo core/config.py criado com encoding UTF-8")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar config.py: {e}")
        return False

def main():
    """Função principal"""
    try:
        print("🎯 DETECTADO: Problema de codificação")
        print("🔧 SOLUÇÃO: Corrigir encoding dos arquivos")
        
        # Opção 1: Tentar corrigir automaticamente
        print("\n1️⃣ Tentando correção automática...")
        if detectar_e_corrigir_encoding():
            print("✅ Correção automática concluída")
        else:
            print("⚠️ Correção automática não funcionou")
        
        # Opção 2: Criar versão limpa do config.py
        print("\n2️⃣ Criando versão limpa do core/config.py...")
        if criar_config_py_limpo():
            print("✅ core/config.py recreado com sucesso")
        
        print("\n🚀 PRÓXIMO PASSO:")
        print("Execute: python test_phase1.py")
        
    except Exception as e:
        print(f"❌ Erro durante correção: {e}")
        return False

if __name__ == "__main__":
    main()