# backend/apps/orcamentos/serializers.py
from rest_framework import serializers

from .models import Orcamento
from backend.apps.ordens_servico.models import OrdemServico

class ItemOrcamentoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=[('peca','Peça'),('deslocamento','Deslocamento'),('mao_de_obra','Mão de Obra')])
    almoxarifado_item = serializers.IntegerField(required=False, allow_null=True)
    descricao = serializers.CharField()
    quantidade = serializers.IntegerField()
    valor_unitario = serializers.DecimalField(max_digits=12, decimal_places=2)

class OrcamentoSerializer(serializers.ModelSerializer):
    items = ItemOrcamentoSerializer(many=True, write_only=True)

    class Meta:
        model = Orcamento
        fields = ['id', 'cliente', 'empreendimento', 'equipamento', 'data_criacao', 'valor_total', 'status', 'items']
        read_only_fields = ['id', 'data_criacao', 'valor_total']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        # calcula valor_total
        total = sum([it['quantidade'] * it['valor_unitario'] for it in items_data])
        validated_data['valor_total'] = total
        orc = super().create(validated_data)
        # aqui você pode criar registro de itens associados, se tiver modelo
        return orc

    def update(self, instance, validated_data):
        old_status = instance.status
        items_data = validated_data.pop('items', None)

        # se houver itens, atualize valor_total
        if items_data is not None:
            total = sum([it['quantidade'] * it['valor_unitario'] for it in items_data])
            validated_data['valor_total'] = total
        
        instance = super().update(instance, validated_data)

        # dispara criação de OS quando status muda para aprovado
        if old_status != 'A' and instance.status == 'A' and not instance.os_criada:
            OrdemServico.objects.create(
                orcamento=instance,
                cliente=instance.cliente,
                equipamento=instance.equipamento,
                data_abertura=timezone.now(),
                descricao=f"OS gerada a partir do orçamento #{instance.id}",
                finalizada=False,
            )
            instance.os_criada = True
            instance.save(update_fields=['os_criada'])

        return instance