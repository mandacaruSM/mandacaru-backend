from django.urls import path
from . import views

urlpatterns = [
    path('os_por_cliente/', views.RelatorioOSPorCliente.as_view()),
    path('estoque_baixo/', views.RelatorioEstoqueBaixo.as_view()),
]
