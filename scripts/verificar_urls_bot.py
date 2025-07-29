# scripts/verificar_urls_bot.py

import os
import sys
import django

# Configurar Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse, resolve
from django.urls.exceptions import NoReverseMatch

print("🔍 VERIFICANDO URLs DO BOT")
print("="*50)

# URLs do bot que devem existir
bot_urls = [
    ('bot-operador-login', '/bot/operador/login/', {}),
    ('bot-equipamento-acesso', '/bot/equipamento/1/', {'equipamento_id': 1}),
    ('bot-atualizar-item', '/bot/item-checklist/atualizar/', {}),
]

print("\n📋 URLs ESPERADAS:")
for name, expected_path, kwargs in bot_urls:
    try:
        url = reverse(name, kwargs=kwargs)
        print(f"✅ {name}: {url}")
        
        # Verificar se a URL resolve corretamente
        try:
            match = resolve(url)
            print(f"   - View: {match.func.__name__ if hasattr(match.func, '__name__') else match.func}")
            print(f"   - Nome: {match.url_name}")
        except Exception as e:
            print(f"   ❌ Erro ao resolver: {e}")
            
    except NoReverseMatch as e:
        print(f"❌ {name}: NÃO ENCONTRADO - {e}")

print("\n📍 TODAS AS URLs QUE COMEÇAM COM /bot/:")
from django.urls import get_resolver
resolver = get_resolver()

def listar_urls(urlpatterns, prefix=''):
    """Lista todas as URLs recursivamente"""
    urls = []
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # É um include
            new_prefix = prefix + str(pattern.pattern)
            urls.extend(listar_urls(pattern.url_patterns, new_prefix))
        else:
            # É uma URL normal
            full_pattern = prefix + str(pattern.pattern)
            if full_pattern.startswith('bot/'):
                urls.append((full_pattern, pattern.name))
    return urls

all_urls = listar_urls(resolver.url_patterns)
for pattern, name in sorted(all_urls):
    print(f"  - {pattern} [{name}]")

print("\n💡 TESTE MANUAL DE URLs:")
print("Para testar manualmente, use curl:")
print("")
print("# Login de operador:")
print('curl -X POST http://127.0.0.1:8000/bot/operador/login/ \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"qr_code": "OP001", "chat_id": "123456789"}\'')
print("")
print("# Acesso a equipamento:")
print('curl -X POST http://127.0.0.1:8000/bot/equipamento/1/ \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"operador_id": 1, "acao": "visualizar"}\'')

print("\n" + "="*50)