from rest_framework import viewsets
from ..models.fornecedor import Fornecedor
from ..serializers.fornecedor_serializer import FornecedorSerializer

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
