# ===============================================
# backend/urls.py - VERSÃO DE EMERGÊNCIA QUE FUNCIONA
# ===============================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Imports para views específicas do bot
try:
    from backend.apps.operadores.views_bot import (
        operador_por_chat_id, operadores_busca, validar_operador_login
    )
    BOT_VIEWS_AVAILABLE = True
except ImportError:
    BOT_VIEWS_AVAILABLE = False

@csrf_exempt
def api_root(request):
    """Endpoint raiz da API"""
    return JsonResponse({
        'message': 'Mandacaru ERP API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'nr12': '/api/nr12/',
            'equipamentos': '/api/equipamentos/',
            'operadores': '/api/operadores/',
            'admin': '/admin/',
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

urlpatterns = [
    # Admin (sempre funciona)
    path('admin/', admin.site.urls),
    
    # API raiz
    path('api/', api_root, name='api-root'),
]

# Adicionar URLs específicas do bot se disponíveis
if BOT_VIEWS_AVAILABLE:
    urlpatterns += [
        path('api/operadores/por-chat-id/', operador_por_chat_id, name='operador-por-chat-id-bot'),
        path('api/operadores/busca/', operadores_busca, name='operadores-busca-bot'),
        path('api/operadores/validar-login/', validar_operador_login, name='validar-login-bot'),
    ]

# ================================================================
# ADICIONAR URLs DOS APPS QUE EXISTEM (COM VERIFICAÇÃO)
# ================================================================

# Tentar adicionar URLs dos apps principais
apps_to_try = [
    ('api/operadores/', 'backend.apps.operadores.api_urls'),
    ('api/equipamentos/', 'backend.apps.equipamentos.urls'),
    ('api/nr12/', 'backend.apps.nr12_checklist.urls'),
    ('operadores/', 'backend.apps.operadores.urls'),  # views HTML
]

# Depois tentar adicionar URLs específicas do bot (sem conflito)
bot_apps_to_try = [
    ('api/operadores/', 'backend.apps.operadores.urls_bot'),  # bot operadores
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

# Adicionar URLs específicas do bot (sem conflito de namespace)
for url_prefix, app_urls in bot_apps_to_try:
    try:
        urlpatterns.append(path(url_prefix, include(app_urls)))
        print(f"🤖 URLs do bot adicionadas: {url_prefix} -> {app_urls}")
    except ImportError as e:
        print(f"⚠️ Bot URLs não encontradas: {app_urls} - {e}")
        continue
    except Exception as e:
        print(f"❌ Erro ao incluir bot URLs {app_urls}: {e}")
        continue

# ================================================================
# APPS ADICIONAIS (OPCIONAIS)
# ================================================================
optional_apps = [
    ('api/auth/', 'backend.apps.authentication'),
    ('api/dashboard/', 'backend.apps.dashboard'), 
    ('api/clientes/', 'backend.apps.clientes'),
    ('api/empreendimentos/', 'backend.apps.empreendimentos'),
    ('api/almoxarifado/', 'backend.apps.almoxarifado'),
    ('api/financeiro/', 'backend.apps.financeiro'),
    ('api/manutencao/', 'backend.apps.manutencao'),
    ('api/orcamentos/', 'backend.apps.orcamentos'),
    ('api/ordens-servico/', 'backend.apps.ordens_servico'),
    ('api/relatorios/', 'backend.apps.relatorios'),
    ('api/abastecimento/', 'backend.apps.abastecimento'),
    ('api/fornecedor/', 'backend.apps.fornecedor'),
]

for url_prefix, app_urls in optional_apps:
    if app_exists(app_urls.replace('.urls', '')):
        try:
            urlpatterns.append(path(url_prefix, include(f'{app_urls}.urls')))
        except Exception:
            pass

# ================================================================
# ARQUIVOS ESTÁTICOS (DESENVOLVIMENTO)
# ================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ================================================================
# RESUMO DOS ENDPOINTS ESPERADOS:
# ================================================================
# /admin/                    - Django Admin
# /api/                      - API Root (informações do sistema)
# /api/operadores/           - APIs de operadores  
# /api/equipamentos/         - APIs de equipamentos
# /api/nr12/                 - APIs de checklist NR12
# /operadores/               - Views HTML de operadores
# + outros apps opcionais conforme disponibilidade