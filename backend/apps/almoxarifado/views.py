# backend/apps/almoxarifado/views.py

from rest_framework import viewsets
from .models import Produto, MovimentacaoEstoque, EstoqueCombustivel
from .serializers import (
    ProdutoSerializer,
    MovimentacaoEstoqueSerializer,
    EstoqueCombustivelSerializer
)


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class MovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoEstoque.objects.all()
    serializer_class = MovimentacaoEstoqueSerializer


class EstoqueCombustivelViewSet(viewsets.ModelViewSet):
    queryset = EstoqueCombustivel.objects.select_related('tipo_combustivel').all()
    serializer_class = EstoqueCombustivelSerializer
    filterset_fields = ('tipo_combustivel', 'ativo')
    search_fields = ('tipo_combustivel__nome',)
