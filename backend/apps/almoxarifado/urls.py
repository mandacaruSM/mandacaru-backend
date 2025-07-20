# backend/apps/almoxarifado/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProdutoViewSet,
    MovimentacaoEstoqueViewSet,
    EstoqueCombustivelViewSet,  # importe o novo viewset
)

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'movimentacoes', MovimentacaoEstoqueViewSet)
router.register(r'estoques-combustivel', EstoqueCombustivelViewSet)  # nova rota

urlpatterns = [
    path('', include(router.urls)),
]
