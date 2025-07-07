from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clientes/', include('backend.apps.clientes.urls')),
    path('api/ordens/', include('backend.apps.ordens_servico.urls')),
    path('api/manutencoes/', include('backend.apps.manutencao.urls')),
    path('api/relatorios/', include('backend.apps.relatorios.urls')),
    path('api/empreendimentos/', include('backend.apps.empreendimentos.urls')),
    path('api/almoxarifado/', include('backend.apps.almoxarifado.urls')),
    path('api/equipamentos/', include('backend.apps.equipamentos.urls')),
]
