from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProdutoViewSet, MovimentacaoEstoqueViewSet

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'movimentacoes', MovimentacaoEstoqueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
