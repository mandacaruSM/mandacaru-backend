# apps/orcamentos/serializers.py
from rest_framework import serializers
from backend.apps.orcamentos.models import Orcamento

class OrcamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orcamento
        fields = '__all__'