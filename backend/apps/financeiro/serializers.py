from rest_framework import serializers
from .models import ContaFinanceira

class ContaFinanceiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaFinanceira
        fields = '__all__'
