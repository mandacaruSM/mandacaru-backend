from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.clientes.urls')),
    path('api/ordens/', include('apps.ordens_servico.urls')),
    path('api/manutencao/', include('apps.manutencao.urls')),
    path('api/relatorios/', include('apps.relatorios.urls')),

]