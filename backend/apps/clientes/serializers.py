from rest_framework import serializers
from .models import Cliente
from backend.apps.empreendimentos.serializers import EmpreendimentoSerializer

class ClienteSerializer(serializers.ModelSerializer):
    empreendimentos = EmpreendimentoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'