from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # APIs da Mandacaru
    path('api/auth/', include('backend.apps.auth_cliente.urls')),
    path('api/nr12/', include('backend.apps.nr12_checklist.urls')),  # ✅ ADICIONAR
    path('api/clientes/', include('backend.apps.clientes.urls')),
    path('api/ordens-servico/', include('backend.apps.ordens_servico.urls')),
    path('api/manutencoes/', include('backend.apps.manutencao.urls')),
    path('api/relatorios/', include('backend.apps.relatorios.urls')),
    path('api/empreendimentos/', include('backend.apps.empreendimentos.urls')),
    path('api/almoxarifado/', include('backend.apps.almoxarifado.urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/financeiro/', include('backend.apps.financeiro.urls')),
    path('api/fornecedor/', include('backend.apps.fornecedor.urls')),
    path('api/orcamentos/', include('backend.apps.orcamentos.urls')),
    path('api/portal/', include('backend.apps.cliente_portal.urls')),
    path('', include('backend.apps.bot_telegram.urls')),  # Endpoints do bot
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)