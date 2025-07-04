from rest_framework import serializers
from .models import HistoricoManutencao

class HistoricoManutencaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoManutencao
        fields = '__all__'
