from rest_framework import viewsets
from .models import Produto, MovimentacaoEstoque
from .serializers import ProdutoSerializer, MovimentacaoEstoqueSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class MovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoEstoque.objects.all()
    serializer_class = MovimentacaoEstoqueSerializer
