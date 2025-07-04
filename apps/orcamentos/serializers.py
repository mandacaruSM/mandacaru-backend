from rest_framework import serializers
from .models import Orcamento
from apps.ordens_servico.models import OrdemServico

class OrcamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orcamento
        fields = '__all__'

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", instance.status)

        instance = super().update(instance, validated_data)

        if old_status != "aprovado" and new_status == "aprovado":
            os = OrdemServico.objects.create(
                cliente=instance.cliente,
                empreendimento=instance.empreendimento,
                descricao_servico=instance.descricao,
                deslocamento_km=0,
                valor_km=3.00,
                responsavel="A definir",
            )
            os.equipamentos.set(instance.equipamentos.all())

        return instance
