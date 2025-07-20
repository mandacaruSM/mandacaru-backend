# backend/apps/almoxarifado/serializers.py

from rest_framework import serializers
from .models import Produto, MovimentacaoEstoque, EstoqueCombustivel


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'


class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoEstoque
        fields = '__all__'


class EstoqueCombustivelSerializer(serializers.ModelSerializer):
    tipo_combustivel_nome = serializers.CharField(source='tipo_combustivel.nome', read_only=True)

    class Meta:
        model = EstoqueCombustivel
        fields = [
            'id',
            'tipo_combustivel',
            'tipo_combustivel_nome',
            'quantidade_em_estoque',
            'estoque_minimo',
            'valor_compra',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ('criado_em', 'atualizado_em')
