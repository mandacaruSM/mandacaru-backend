# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

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

# Função auxiliar para verificar se um app existe
def app_exists(app_path):
    """Verifica se um app Django existe"""
    try:
        # Tenta importar o módulo urls do app
        module_path = f"{app_path}.urls"
        __import__(module_path)
        return True
    except ImportError:
        return False

urlpatterns = [
    # Administração
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
]

# Adicionar URLs dos apps que existem
apps_urls = [
    ('api/auth/', 'backend.apps.authentication'),
    ('api/dashboard/', 'backend.apps.dashboard'),
    ('api/nr12/', 'backend.apps.nr12_checklist'),
    ('api/equipamentos/', 'backend.apps.equipamentos'),
    ('api/clientes/', 'backend.apps.clientes'),
    ('api/empreendimentos/', 'backend.apps.empreendimentos'),
    ('api/operadores/', 'backend.apps.operadores'),
    ('api/almoxarifado/', 'backend.apps.almoxarifado'),
    ('api/financeiro/', 'backend.apps.financeiro'),
    ('api/manutencao/', 'backend.apps.manutencao'),
    ('api/ordens-servico/', 'backend.apps.ordens_servico'),
    ('api/orcamentos/', 'backend.apps.orcamentos'),
    ('api/fornecedor/', 'backend.apps.fornecedor'),
    ('api/relatorios/', 'backend.apps.relatorios'),
    ('api/portal/', 'backend.apps.cliente_portal'),
]

# Adicionar apenas os apps que existem
for url_path, app_module in apps_urls:
    if app_exists(app_module):
        urlpatterns.append(path(url_path, include(f'{app_module}.urls')))
    else:
        # Criar um endpoint vazio para apps não implementados
        urlpatterns.append(
            path(url_path, lambda request, app=app_module: JsonResponse({
                'error': f'App {app} não implementado ainda',
                'status': 'em_desenvolvimento'
            }), name=f'{app_module}-placeholder')
        )

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)