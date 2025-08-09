# -*- coding: utf-8 -*-
from pathlib import Path

def adicionar_variaveis_faltantes():
    print("🔧 ADICIONANDO VARIÁVEIS FALTANTES")
    print("=" * 40)
    
    config_path = Path("core/config.py")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ Arquivo core/config.py lido")
    except Exception as e:
        print(f"❌ Erro ao ler config.py: {e}")
        return False
    
    # Adicionar variáveis que faltam
    if "MAX_MESSAGE_LENGTH" not in content:
        variaveis_extras = '''
# Configurações de mensagem
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
MESSAGE_CHUNK_SIZE = int(os.getenv("MESSAGE_CHUNK_SIZE", "3500"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "temp/uploads")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "yes")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")
DB_FILE = os.getenv("DB_FILE", "data/bot.db")
'''
        
        # Inserir antes do __all__
        if "__all__" in content:
            content = content.replace("__all__", variaveis_extras + "\n__all__")
        else:
            content += variaveis_extras
        
        # Atualizar __all__
        if '"validar_configuracoes"' in content:
            content = content.replace(
                '"validar_configuracoes"',
                '"validar_configuracoes",\n    "MAX_MESSAGE_LENGTH", "MESSAGE_CHUNK_SIZE", "LOG_FILE"'
            )
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Variáveis adicionadas")
            
            # Testar
            import sys
            if 'core.config' in sys.modules:
                del sys.modules['core.config']
            from core.config import MAX_MESSAGE_LENGTH
            print(f"✅ MAX_MESSAGE_LENGTH: {MAX_MESSAGE_LENGTH}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return False
    else:
        print("✅ Variáveis já existem")
        return True

if __name__ == "__main__":
    if adicionar_variaveis_faltantes():
        print("🎉 SUCESSO!")
        print("🚀 Execute: python test_phase1.py")
