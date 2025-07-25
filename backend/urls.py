# ================================================================
# ATUALIZAR backend/urls.py - INTEGRAÇÃO FINAL COM BOT
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
            'operadores': '/api/operadores/',
            'almoxarifado': '/api/almoxarifado/',
            'financeiro': '/api/financeiro/',
            'manutencao': '/api/manutencao/',
            'orcamentos': '/api/orcamentos/',
            'ordens_servico': '/api/ordens-servico/',
            'relatorios': '/api/relatorios/',
            'portal': '/api/portal/',
            'bot_telegram': '/api/nr12/bot/',  # ✅ CORRIGIDO: Endpoint correto do bot
        },
        # ✅ ADICIONADO: Informações específicas do bot
        'bot_endpoints': {
            'operador_login': '/api/nr12/bot/operador/login/',
            'equipamento_acesso': '/api/nr12/bot/equipamento/{id}/',
            'atualizar_item': '/api/nr12/bot/item-checklist/atualizar/',
        }
    })

urlpatterns = [
    # Administração
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api_root'),
    
    # ================================================================
    # MÓDULOS PRINCIPAIS
    # ================================================================
    
    # Autenticação e Dashboard
    path('api/auth/', include('backend.apps.auth_cliente.urls')),
    path('api/dashboard/', include('backend.apps.dashboard.urls')),
    
    # ================================================================
    # EQUIPAMENTOS E NR12 (Ordem correta para bot funcionar)
    # ================================================================
    
    # Equipamentos
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    
    # NR12 - APIs REST principais
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),
    
    # ✅ CRÍTICO: URLs do bot DENTRO do nr12 (já definidas no urls.py do nr12)
    # As URLs do bot são: /api/nr12/bot/... (definidas em nr12_checklist/urls.py)
    
    # ================================================================
    # OPERADORES E OUTROS MÓDULOS
    # ================================================================
    
    # Operadores
    path('operadores/', include('backend.apps.operadores.urls')),  # Web views
    path('api/operadores/', include('backend.apps.operadores.api_urls')),  # API
    
    # Clientes e Empreendimentos
    path('api/clientes/', include('backend.apps.clientes.urls')),
    path('api/empreendimentos/', include('backend.apps.empreendimentos.urls')),
    
    # ================================================================
    # OUTROS MÓDULOS DO SISTEMA
    # ================================================================
    
    # Almoxarifado e Financeiro
    path('api/almoxarifado/', include('backend.apps.almoxarifado.urls')),
    path('api/financeiro/', include('backend.apps.financeiro.urls')),
    
    # Manutenção e Ordens de Serviço
    path('api/manutencao/', include('backend.apps.manutencao.urls')),
    path('api/ordens-servico/', include('backend.apps.ordens_servico.urls')),
    
    # Orçamentos e Fornecedores
    path('api/orcamentos/', include('backend.apps.orcamentos.urls')),
    path('api/fornecedor/', include('backend.apps.fornecedor.urls')),
    
    # Relatórios
    path('api/relatorios/', include('backend.apps.relatorios.urls')),
    
    # Portal do cliente
    path('api/portal/', include('backend.apps.cliente_portal.urls')),
    
    # ================================================================
    # BOT TELEGRAM (URLs públicas adicionais, se necessário)
    # ================================================================
    
    # Bot Telegram principal (se tiver URLs específicas fora do NR12)
    #path('', include('backend.apps.bot_telegram.urls')),
    
    # ✅ Abastecimento (descomentado se necessário)
    # path('abastecimento/', include('backend.apps.abastecimento.urls')),
]

# ================================================================
# ARQUIVOS ESTÁTICOS E MÍDIA
# ================================================================

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ================================================================
# RESUMO DOS ENDPOINTS DO BOT DISPONÍVEIS:
# ================================================================

"""
🤖 ENDPOINTS DO BOT TELEGRAM (Funcionais após as correções):

1. 👤 LOGIN DE OPERADOR:
   POST /api/nr12/bot/operador/login/
   Body: {
       "qr_code": "OP0001" ou "dados_json_do_qr",
       "chat_id": "123456789"
   }

2. 🔧 ACESSO A EQUIPAMENTO:
   GET  /api/nr12/bot/equipamento/{id}/?operador=OP0001
   POST /api/nr12/bot/equipamento/{id}/
   Body: {
       "acao": "criar_checklist|iniciar_checklist|continuar_checklist|finalizar_checklist",
       "operador_codigo": "OP0001",
       "turno": "MANHA", (opcional)
       "frequencia": "DIARIA" (opcional)
   }

3. ✅ ATUALIZAR ITEM DE CHECKLIST:
   POST /api/nr12/bot/item-checklist/atualizar/
   Body: {
       "item_id": 123,
       "status": "OK|NOK|NA",
       "observacao": "texto opcional",
       "operador_codigo": "OP0001"
   }

4. 📋 VISUALIZAR CHECKLIST (Web):
   GET /api/nr12/checklist/{uuid}/

5. 📄 PDF DO CHECKLIST:
   GET /api/nr12/checklist/{id}/pdf/

6. 🔗 QR CODE PDF EQUIPAMENTO:
   GET /api/equipamentos/{id}/qr-pdf/

📝 FLUXO TÍPICO DO BOT:

1. Operador escaneia QR do próprio cartão → Login
2. Operador escaneia QR do equipamento → Acessa funções
3. Bot oferece opções: Checklist, Abastecimento, Anomalia, Relatório
4. Para checklist: Criar → Iniciar → Preencher itens → Finalizar
5. Cada item é atualizado via endpoint específico

🔧 TESTE RÁPIDO:

# Login
curl -X POST http://localhost:8000/api/nr12/bot/operador/login/ \
  -H "Content-Type: application/json" \
  -d '{"qr_code": "OP0001", "chat_id": "123456"}'

# Acesso equipamento
curl http://localhost:8000/api/nr12/bot/equipamento/1/?operador=OP0001

# Criar checklist
curl -X POST http://localhost:8000/api/nr12/bot/equipamento/1/ \
  -H "Content-Type: application/json" \
  -d '{"acao": "criar_checklist", "operador_codigo": "OP0001", "turno": "MANHA"}'
"""