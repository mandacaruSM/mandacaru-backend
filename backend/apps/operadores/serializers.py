from rest_framework import serializers
from .models import Operador

class OperadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operador
        fields = ['id', 'nome', 'cpf', 'codigo', 'data_nascimento', 'chat_id_telegram', 'ativo_bot', 'status']
