from rest_framework import serializers
from .models import Orcamento, OrcamentoItem

class OrcamentoItemSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = OrcamentoItem
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario', 'subtotal']

class OrcamentoSerializer(serializers.ModelSerializer):
    itens = OrcamentoItemSerializer(many=True)
    distancia_km = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    custo_deslocamento = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Orcamento
        fields = [
            'id', 'cliente', 'empreendimento', 'data_criacao', 'data_vencimento',
            'distancia_km', 'custo_deslocamento', 'itens', 'valor_total', 'status'
        ]

    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        orc = super().create(validated_data)
        for item in itens_data:
            OrcamentoItem.objects.create(
                orcamento=orc,
                **item
            )
        return orc

    def update(self, instance, validated_data):
        itens_data = validated_data.pop('itens', None)
        instance = super().update(instance, validated_data)
        if itens_data is not None:
            # deletar e recriar para simplificar
            instance.itens.all().delete()
            for item in itens_data:
                OrcamentoItem.objects.create(orcamento=instance, **item)
        return instance