# apps/empreendimentos/serializers.py
from rest_framework import serializers
from .models import Empreendimento

class EmpreendimentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.ReadOnlyField(source='cliente.nome_fantasia')

    class Meta:
        model = Empreendimento
        fields = '__all__'
