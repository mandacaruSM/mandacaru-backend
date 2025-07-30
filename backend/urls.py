# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from backend.apps.nr12_checklist.views_bot import checklists_bot, equipamentos_operador
from backend.apps.equipamentos.views_bot import equipamentos_publicos, checklists_equipamento  
from backend.apps.operadores.views_bot import atualizar_operador
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
    # Admin
    path('admin/', admin.site.urls),

    # API REST
    path('api/operadores/', include('backend.apps.operadores.api_urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),

    # Endpoints específicos do bot
#    path('bot/', include('backend.apps.operadores.urls_bot')),
#    path('bot/', include('backend.apps.equipamentos.urls_bot')),
#    path('bot/', include('backend.apps.nr12_checklist.urls_bot')),

    # Views HTML
    path('operadores/', include('backend.apps.operadores.urls')),

    # API raiz
    path('api/', api_root, name='api-root'),

#    path('api/nr12/bot/', include('backend.apps.nr12_checklist.urls_bot_corrigido')),

    path('api/checklists/', checklists_bot, name='checklists-bot'),
    path('api/nr12/checklists/', checklists_bot, name='nr12-checklists-bot'),
    path('api/equipamentos/', equipamentos_publicos, name='equipamentos-publicos'),
    path('api/operadores/<int:operador_id>/equipamentos/', equipamentos_operador, name='operador-equipamentos'),
    path('api/equipamentos/<int:equipamento_id>/checklists/', checklists_equipamento, name='equipamento-checklists'),
    path('api/operadores/<int:operador_id>/', atualizar_operador, name='atualizar-operador'),
]


# Adicionar URLs dos apps que existem
apps_urls = [
    ('api/auth/', 'backend.apps.authentication'),
    ('api/dashboard/', 'backend.apps.dashboard'),
    ('api/nr12/', 'backend.apps.nr12_checklist'),
    ('api/equipamentos/', 'backend.apps.equipamentos'),
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

# Adicionar URLs dos apps que existem
for url_pattern, app_path in apps_urls:
    if app_exists(app_path):
        try:
            urlpatterns.append(path(url_pattern, include(f'{app_path}.urls')))
        except Exception as e:
            # Se der erro, tenta sem o .urls
            pass

# Servir arquivos de média em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)