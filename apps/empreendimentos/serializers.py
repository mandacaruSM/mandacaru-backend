from rest_framework import serializers
from .models import Empreendimento

class EmpreendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empreendimento
        fields = '__all__'
