# apps/manutencao/serializers.py

from rest_framework import serializers
from .models import HistoricoManutencao
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date

class HistoricoManutencaoSerializer(serializers.ModelSerializer):
    equipamento_nome = serializers.ReadOnlyField(source="equipamento.nome")

    class Meta:
        model = HistoricoManutencao
        fields = '__all__'

    def validate(self, data):
        equipamento = data.get("equipamento")
        horimetro = data.get("horimetro")
        tipo = data.get("tipo")
        proxima_manutencao = data.get("proxima_manutencao")

        # Verifica se é preventiva e exige "proxima_manutencao"
        if tipo == "preventiva" and not proxima_manutencao:
            raise serializers.ValidationError({
                "proxima_manutencao": _("Este campo é obrigatório para manutenções preventivas.")
            })

        # Garante que horímetro é maior que o último
        if self.instance:
            # edição: ignora o próprio registro
            anteriores = HistoricoManutencao.objects.filter(equipamento=equipamento).exclude(id=self.instance.id)
        else:
            anteriores = HistoricoManutencao.objects.filter(equipamento=equipamento)

        ultimo = anteriores.order_by("-data", "-horimetro").first()

        if ultimo and horimetro <= ultimo.horimetro:
            raise serializers.ValidationError({
                "horimetro": _(f"O horímetro ({horimetro}) deve ser maior que o da última manutenção registrada ({ultimo.horimetro}).")
            })

        return data
