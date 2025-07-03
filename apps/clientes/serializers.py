from rest_framework import serializers
from .models import Cliente, Empreendimento

class EmpreendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empreendimento
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    empreendimentos = EmpreendimentoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'
