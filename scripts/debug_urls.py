# scripts/debug_urls.py

import os
import sys

# Configurar caminho
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Procurar arquivo urls.py principal
print("🔍 Procurando arquivo principal de URLs...")

urls_files = []
for root, dirs, files in os.walk(os.path.join(project_root, 'backend')):
    # Ignorar diretórios de apps
    if 'apps' in root:
        continue
    for file in files:
        if file == 'urls.py':
            full_path = os.path.join(root, file)
            urls_files.append(full_path)
            print(f"\n📄 Encontrado: {full_path}")
            
            # Ler conteúdo e procurar por 'bot/'
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Procurar linha com bot/
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'bot/' in line and 'path' in line:
                    print(f"\n   Linha {i+1}: {line.strip()}")
                    # Mostrar contexto
                    if i > 0:
                        print(f"   Linha {i}: {lines[i-1].strip()}")
                    if i < len(lines) - 1:
                        print(f"   Linha {i+2}: {lines[i+1].strip()}")

print("\n💡 A linha correta deve ser algo como:")
print("   path('bot/', include('backend.apps.nr12_checklist.urls_bot')),")
print("\n⚠️  Se houver namespace, use:")
print("   path('bot/', include(('backend.apps.nr12_checklist.urls_bot', 'bot'))),")