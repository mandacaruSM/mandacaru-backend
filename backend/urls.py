# backend/urls.py
# ================================================================
# CORREÇÃO CRÍTICA: backend/urls.py
# Corrige imports para evitar ModuleNotFoundError e mantém funcionalidade
# ================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from backend.apps.nr12_checklist.views import ItemChecklistAtualizarView
# Import ViewSets para registro no router
from backend.apps.nr12_checklist.views import (
    ChecklistNR12ViewSet,
    ItemChecklistRealizadoViewSet
)

# Instancia router DRF
router = DefaultRouter()
# Registra principais endpoints NR12
router.register(r'nr12/checklists', ChecklistNR12ViewSet, basename='nr12-checklists')
router.register(r'nr12/itemchecklistrealizado', ItemChecklistRealizadoViewSet, basename='itemchecklistrealizado')

def health_check(request):
    """Endpoint de health check simples"""
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

# URLs principais
urlpatterns = [
    path('admin/', admin.site.urls),
    # Endpoints REST via router
    path('api/', include(router.urls)),
    # APIs REST de apps específicos
    path('api/operadores/', include('backend.apps.operadores.api_urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),
    # Health and root
    path('api/health/', health_check, name='health_check'),
    path('api/', api_root, name='api-root'),
    # VIEWS HTML (não APIs)
    path('operadores/', include('backend.apps.operadores.urls')),
    # Endpoint específico para atualização de item-checklist
    path('api/nr12/bot/item-checklist/atualizar/', ItemChecklistAtualizarView.as_view(), name='item-checklist-atualizar'),
]

# Integração dinâmica de apps adicionais (sem duplicar)
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

for url_pattern, app_path in apps_urls:
    try:
        urlpatterns.append(path(url_pattern, include(f'{app_path}.urls')))
    except ImportError:
        # App não existe ou não tem urls
        pass

# Servir arquivos estáticos em DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)