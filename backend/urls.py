from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from backend.apps.financeiro.views import ContaFinanceiraViewSet

# Rotas do DRF
router = DefaultRouter()
router.register(r'financeiro/contas', ContaFinanceiraViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas da API da Mandacaru
    path('api/clientes/', include('backend.apps.clientes.urls')),
    path('api/ordens/', include('backend.apps.ordens_servico.urls')),
    path('api/manutencoes/', include('backend.apps.manutencao.urls')),
    path('api/relatorios/', include('backend.apps.relatorios.urls')),
    path('api/empreendimentos/', include('backend.apps.empreendimentos.urls')),
    path('api/almoxarifado/', include('backend.apps.almoxarifado.urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
    path('api/financeiro/', include('backend.apps.financeiro.urls')),
    path('api/fornecedor/', include('backend.apps.fornecedor.urls')),


]

# Suporte a imagens (comprovantes)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
