from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from apps.financeiro.views import ContaFinanceiraViewSet

# Rotas do DRF
router = DefaultRouter()
router.register(r'financeiro/contas', ContaFinanceiraViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas da API da Mandacaru
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/ordens/', include('apps.ordens_servico.urls')),
    path('api/manutencoes/', include('apps.manutencao.urls')),
    path('api/relatorios/', include('apps.relatorios.urls')),
    path('api/empreendimentos/', include('apps.empreendimentos.urls')),
    path('api/almoxarifado/', include('apps.almoxarifado.urls')),
    path('api/equipamentos/', include('apps.equipamentos.urls')),
    path('api/financeiro/', include('apps.financeiro.urls')),

    # Rotas do DRF (como financeiro)
    path('api/', include(router.urls)),
]

# Suporte a imagens (comprovantes)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
