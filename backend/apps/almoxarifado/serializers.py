from rest_framework import serializers
from .models import Produto, MovimentacaoEstoque

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoEstoque
        fields = '__all__'
