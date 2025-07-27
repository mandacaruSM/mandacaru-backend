# backend/apps/operadores/serializers.py

from rest_framework import serializers
from .models import Operador

class OperadorSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Operador"""
    
    class Meta:
        model = Operador
        fields = [
            'id', 'codigo', 'nome', 'cpf', 'rg', 'data_nascimento',
            'telefone', 'email', 'endereco', 'cidade', 'estado', 'cep',
            'funcao', 'setor', 'data_admissao', 'data_demissao', 'salario',
            'status', 'chat_id_telegram', 'ativo_bot', 'ultimo_acesso_bot',
            'pode_fazer_checklist', 'pode_registrar_abastecimento'
        ]
        read_only_fields = ['codigo', 'ativo_bot', 'ultimo_acesso_bot']

class OperadorListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de operadores"""
    
    class Meta:
        model = Operador
        fields = [
            'id', 'codigo', 'nome', 'cpf', 'telefone', 'email',
            'funcao', 'setor', 'status', 'data_nascimento'
        ]