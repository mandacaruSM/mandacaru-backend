# ================================================================
# ATUALIZAR backend/urls.py
# ================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_root(request):
    """Endpoint raiz da API com informações do sistema"""
    return JsonResponse({
        'message': 'Mandacaru ERP API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'auth': '/api/auth/',
            'dashboard': '/api/dashboard/',
            'nr12': '/api/nr12/',
            'equipamentos': '/api/equipamentos/',
            'clientes': '/api/clientes/',
            'empreendimentos': '/api/empreendimentos/',
            'almoxarifado': '/api/almoxarifado/',
            'financeiro': '/api/financeiro/',
            'manutencao': '/api/manutencao/',
            'orcamentos': '/api/orcamentos/',
            'ordens_servico': '/api/ordens-servico/',
            'relatorios': '/api/relatorios/',
            'portal': '/api/portal/',
            'bot_telegram': '/qr/',
        }
    })

urlpatterns = [
    # Administração
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api_root'),
    
    # APIs principais do sistema
    path('api/auth/', include('backend.apps.auth_cliente.urls')),
    path('api/dashboard/', include('backend.apps.dashboard.urls')),
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/clientes/', include('backend.apps.clientes.urls')),
    path('api/empreendimentos/', include('backend.apps.empreendimentos.urls')),
    path('api/almoxarifado/', include('backend.apps.almoxarifado.urls')),
    path('api/financeiro/', include('backend.apps.financeiro.urls')),
    path('api/manutencao/', include('backend.apps.manutencao.urls')),
    path('api/orcamentos/', include('backend.apps.orcamentos.urls')),
    path('api/ordens-servico/', include('backend.apps.ordens_servico.urls')),
    path('api/relatorios/', include('backend.apps.relatorios.urls')),
    path('api/fornecedor/', include('backend.apps.fornecedor.urls')),
    
    # Portal do cliente
    path('api/portal/', include('backend.apps.cliente_portal.urls')),
    
    # Bot Telegram (endpoints públicos)
    path('', include('backend.apps.bot_telegram.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)