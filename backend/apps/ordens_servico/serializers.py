# backend/apps/ordens_servico/serializers.py
from rest_framework import serializers
from .models import OrdemServico

class OrdemServicoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome_fantasia', read_only=True)
    equipamento_nome = serializers.CharField(source='equipamento.nome', read_only=True)

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'orcamento',
            'cliente', 'cliente_nome',
            'equipamento', 'equipamento_nome',
            'data_abertura', 'data_fechamento',
            'descricao', 'finalizada'
        ]
        read_only_fields = ['id', 'data_abertura']