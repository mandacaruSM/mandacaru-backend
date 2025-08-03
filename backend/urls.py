# ================================================================
# CORREÇÃO CRÍTICA: backend/urls.py
# Remove conflitos e duplicações, mantém funcionalidade
# ================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

def health_check(request):
    """Endpoint de health check simples - função corrigida"""
    return JsonResponse({'status': 'ok', 'message': 'API funcionando'})

@csrf_exempt
def api_root(request):
    """Endpoint raiz da API com informações do sistema e bot"""
    return JsonResponse({
        'message': 'Mandacaru ERP API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'nr12': '/api/nr12/',
            'equipamentos': '/api/equipamentos/',
            'clientes': '/api/clientes/',
            'empreendimentos': '/api/empreendimentos/',
            'operadores': '/api/operadores/',
            'almoxarifado': '/api/almoxarifado/',
            'financeiro': '/api/financeiro/',
            'manutencao': '/api/manutencao/',
            'orcamentos': '/api/orcamentos/',
            'ordens_servico': '/api/ordens-servico/',
            'relatorios': '/api/relatorios/',
        },
        'bot_telegram': {
            'info': 'Endpoints do Bot Telegram para integração',
            'endpoints': {
                'operador_login': '/api/nr12/bot/operador/login/',
                'equipamento_acesso': '/api/nr12/bot/equipamento/{id}/',
                'atualizar_item': '/api/nr12/bot/item-checklist/atualizar/',
            },
            'documentacao': 'Use POST com JSON para todos os endpoints do bot'
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

# ================================================================
# URL PATTERNS LIMPO - SEM DUPLICAÇÕES
# ================================================================

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ================================================================
    # APIs REST PRINCIPAIS (ordem importa!)
    # ================================================================
    path('api/operadores/', include('backend.apps.operadores.api_urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),
    
    # ================================================================
    # ENDPOINTS ESPECIAIS
    # ================================================================
    path('api/health/', health_check, name='health_check'),
    path('api/', api_root, name='api-root'),
    
    # ================================================================
    # VIEWS HTML (não APIs)
    # ================================================================
    path('operadores/', include('backend.apps.operadores.urls')),
]

# ================================================================
# ADICIONAR APPS DINAMICAMENTE (sem conflitos)
# ================================================================
apps_urls = [
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

# Adicionar URLs de apps que existem (sem duplicar os já incluídos)
for url_pattern, app_path in apps_urls:
    if app_exists(app_path):
        try:
            urlpatterns.append(path(url_pattern, include(f'{app_path}.urls')))
        except Exception as e:
            # Log error but continue
            print(f"Warning: Could not include {app_path}.urls - {e}")

# ================================================================
# ARQUIVOS ESTÁTICOS (sempre por último)
# ================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)