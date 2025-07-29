# scripts/descobrir_estrutura.py

import os
import sys

# Diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

print("🔍 ANALISANDO ESTRUTURA DO PROJETO")
print("="*50)
print(f"Diretório raiz: {project_root}")
print(f"Diretório atual: {current_dir}")
print("="*50)

# Listar conteúdo da raiz
print("\n📁 CONTEÚDO DA RAIZ:")
for item in sorted(os.listdir(project_root)):
    item_path = os.path.join(project_root, item)
    if os.path.isdir(item_path):
        print(f"  📁 {item}/")
    else:
        print(f"  📄 {item}")

# Procurar por settings.py
print("\n⚙️ PROCURANDO SETTINGS.PY:")
settings_found = []
for root, dirs, files in os.walk(project_root):
    # Ignorar pastas do virtual env
    dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', 'env', '__pycache__']]
    
    for file in files:
        if file == 'settings.py':
            rel_path = os.path.relpath(os.path.join(root, file), project_root)
            settings_found.append(rel_path)
            print(f"  ✅ Encontrado: {rel_path}")

# Procurar por manage.py
print("\n🔧 PROCURANDO MANAGE.PY:")
for root, dirs, files in os.walk(project_root):
    dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', 'env', '__pycache__']]
    
    for file in files:
        if file == 'manage.py':
            rel_path = os.path.relpath(os.path.join(root, file), project_root)
            print(f"  ✅ Encontrado: {rel_path}")
            
            # Ler conteúdo do manage.py para descobrir settings
            manage_path = os.path.join(root, file)
            with open(manage_path, 'r') as f:
                content = f.read()
                if 'DJANGO_SETTINGS_MODULE' in content:
                    for line in content.split('\n'):
                        if 'DJANGO_SETTINGS_MODULE' in line:
                            print(f"     Settings module: {line.strip()}")

# Verificar estrutura de apps
print("\n📱 PROCURANDO APPS:")
apps_dirs = ['apps', 'backend/apps', 'src/apps']
for apps_dir in apps_dirs:
    full_path = os.path.join(project_root, apps_dir)
    if os.path.exists(full_path):
        print(f"\n  ✅ Encontrado diretório de apps: {apps_dir}")
        for app in os.listdir(full_path):
            app_path = os.path.join(full_path, app)
            if os.path.isdir(app_path) and not app.startswith('__'):
                print(f"     - {app}")

# Verificar .env
print("\n🔑 ARQUIVO .ENV:")
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    print("  ✅ .env existe")
    # Mostrar apenas as chaves, não os valores
    with open(env_path, 'r') as f:
        lines = f.readlines()
        keys = []
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                if key:
                    keys.append(key)
        if keys:
            print("  Variáveis encontradas:")
            for key in sorted(set(keys)):
                print(f"    - {key}")
else:
    print("  ❌ .env NÃO existe")

# Sugerir comando Django correto
print("\n💡 SUGESTÃO DE COMANDO:")
if settings_found:
    # Pegar o primeiro settings encontrado
    settings_path = settings_found[0].replace('\\', '.').replace('/', '.').replace('.py', '')
    print(f"  export DJANGO_SETTINGS_MODULE='{settings_path}'")
    print(f"  # ou no Windows:")
    print(f"  set DJANGO_SETTINGS_MODULE={settings_path}")

print("\n" + "="*50)