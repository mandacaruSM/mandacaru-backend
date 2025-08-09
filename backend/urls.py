# ===============================================
# backend/urls.py - VERSÃO CORRIGIDA E FUNCIONAL
# ===============================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_root(request):
    """Endpoint raiz da API"""
    return JsonResponse({
        'message': 'Mandacaru ERP API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'admin': '/admin/',
            'nr12': '/api/nr12/',
            'equipamentos': '/api/equipamentos/',
            'operadores': '/api/operadores/',
        }
    })

def app_exists(app_path):
    """Verifica se um app Django existe"""
    try:
        module_path = f"{app_path}.urls"
        __import__(module_path)
        return True
    except ImportError:
        return False

# ===============================================
# URLs PRINCIPAIS
# ===============================================

urlpatterns = [
    # Admin (sempre funciona)
    path('admin/', admin.site.urls),
    
    # API raiz
    path('api/', api_root, name='api-root'),
]

# ===============================================
# ADICIONAR URLs DOS APPS (COM VERIFICAÇÃO)
# ===============================================

# Tentar adicionar URLs dos apps principais
apps_to_try = [
    ('api/nr12/', 'backend.apps.nr12_checklist.urls'),
    ('api/equipamentos/', 'backend.apps.equipamentos.urls'), 
    ('api/operadores/', 'backend.apps.operadores.api_urls'),
    ('operadores/', 'backend.apps.operadores.urls'),  # views HTML se existir
]

for url_prefix, app_urls in apps_to_try:
    try:
        urlpatterns.append(path(url_prefix, include(app_urls)))
        print(f"✅ URLs adicionadas: {url_prefix} -> {app_urls}")
    except ImportError as e:
        print(f"⚠️ App não encontrado: {app_urls} - {e}")
        continue
    except Exception as e:
        print(f"❌ Erro ao incluir {app_urls}: {e}")
        continue

# ===============================================
# TENTAR ADICIONAR URLs ESPECÍFICAS DO BOT
# ===============================================

# Imports seguros para views do bot
bot_views_imported = False
try:
    from backend.apps.operadores.views_bot import (
        operador_por_chat_id, operadores_busca, validar_operador_login, atualizar_operador
    )
    from backend.apps.nr12_checklist.views_bot import (
        checklists_bot, equipamentos_operador
    )
    from backend.apps.equipamentos.views_bot import (
        equipamentos_publicos, checklists_equipamento
    )
    bot_views_imported = True
    print("✅ Views do bot importadas com sucesso")
except ImportError as e:
    print(f"⚠️ Algumas views do bot não foram encontradas: {e}")
    bot_views_imported = False

# Se conseguiu importar as views do bot, adicionar as URLs
if bot_views_imported:
    urlpatterns += [
        # ENDPOINTS ESPECÍFICOS DO BOT TELEGRAM
        path('api/operadores/por-chat-id/', operador_por_chat_id, name='operador-por-chat-id-bot'),
        path('api/operadores/busca/', operadores_busca, name='operadores-busca-bot'), 
        path('api/operadores/validar-login/', validar_operador_login, name='validar-login-bot'),
        path('api/operadores/<int:operador_id>/', atualizar_operador, name='atualizar-operador-bot'),
        
        path('api/checklists/', checklists_bot, name='checklists-bot'),
        path('api/nr12/checklists/', checklists_bot, name='nr12-checklists-bot'),
        path('api/operadores/<int:operador_id>/equipamentos/', equipamentos_operador, name='operador-equipamentos-bot'),
        
        path('api/equipamentos/', equipamentos_publicos, name='equipamentos-publicos-bot'),
        path('api/equipamentos/<int:equipamento_id>/checklists/', checklists_equipamento, name='equipamento-checklists-bot'),
    ]
    print("🤖 URLs específicas do bot adicionadas")

# ===============================================
# ARQUIVOS ESTÁTICOS (DESENVOLVIMENTO)
# ===============================================

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

print(f"📊 Total de URLs registradas: {len(urlpatterns)}")