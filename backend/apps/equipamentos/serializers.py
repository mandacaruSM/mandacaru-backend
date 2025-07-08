# SERIALIZER
from rest_framework import serializers
from .models import Equipamento

class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        fields = '__all__'


# VIEWSET
from rest_framework import viewsets
from .models import Equipamento
from .serializers import EquipamentoSerializer

class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer
