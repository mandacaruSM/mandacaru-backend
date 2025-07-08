# apps/ordens_servico/serializers.py

from rest_framework import serializers
from backend.apps.ordens_servico.models import OrdemServico

class OrdemServicoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome_fantasia", read_only=True)
    equipamento_nome = serializers.CharField(source="equipamento.nome", read_only=True)

    class Meta:
        model = OrdemServico
        fields = '__all__'  # Vai incluir todos os campos do modelo
        # E também cliente_nome e equipamento_nome porque foram definidos acima
