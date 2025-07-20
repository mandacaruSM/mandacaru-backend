# backend/apps/abastecimento/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import RegistroAbastecimentoViewSet, TipoCombustivelViewSet
from . import views
from .views import gerar_relatorio_consumo_view

router = DefaultRouter()
router.register(r'api/abastecimentos', RegistroAbastecimentoViewSet)
router.register(r'api/tipos-combustivel', TipoCombustivelViewSet)

urlpatterns += [
    path('relatorio/consumo/', gerar_relatorio_consumo_view, name='relatorio_consumo'),
]