
from rest_framework import serializers
from .models import Cliente, Empreendimento

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class EmpreendimentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome_fantasia', read_only=True)

    class Meta:
        model = Empreendimento
        fields = '__all__'
