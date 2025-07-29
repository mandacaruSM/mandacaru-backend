# scripts/executar_bot.py

import os
import sys
import subprocess

print("🤖 EXECUTANDO BOT TELEGRAM")
print("="*50)

# Caminho do projeto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bot_path = os.path.join(project_root, 'mandacaru_bot')

print(f"📁 Diretório do projeto: {project_root}")
print(f"📁 Diretório do bot: {bot_path}")

# Verificar se existe
if not os.path.exists(bot_path):
    print(f"\n❌ Pasta do bot não encontrada em: {bot_path}")
    print("\nProcurando em outros locais...")
    
    # Procurar a pasta mandacaru_bot
    for root, dirs, files in os.walk(project_root):
        if 'mandacaru_bot' in dirs:
            bot_path = os.path.join(root, 'mandacaru_bot')
            print(f"✅ Encontrada em: {bot_path}")
            break
    else:
        print("❌ Pasta mandacaru_bot não encontrada em lugar nenhum!")
        sys.exit(1)

# Verificar arquivo start.py
start_file = os.path.join(bot_path, 'start.py')
if not os.path.exists(start_file):
    print(f"\n❌ Arquivo start.py não encontrado em: {start_file}")
    
    # Listar arquivos na pasta
    print("\n📄 Arquivos encontrados:")
    for file in os.listdir(bot_path):
        print(f"  - {file}")
    sys.exit(1)

# Mudar para o diretório do bot
os.chdir(bot_path)
print(f"\n📂 Mudando para: {os.getcwd()}")

# Configurar variáveis de ambiente
os.environ['BOT_DEBUG'] = 'True'
print("\n🔧 Modo debug ativado")

# Executar o bot
print("\n🚀 Iniciando bot...")
print("-"*50)

try:
    # Usar o Python do ambiente virtual
    python_exe = sys.executable
    subprocess.run([python_exe, 'start.py'])
except KeyboardInterrupt:
    print("\n\n⏹️ Bot interrompido pelo usuário")
except Exception as e:
    print(f"\n❌ Erro ao executar bot: {e}")