 # 2. ATUALIZAR backend/apps/auth_cliente/serializers.py
# ================================================================

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UsuarioCliente

class LoginSerializer(serializers.Serializer):
    """Serializer para login de usuários"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('Conta desativada.')
            else:
                raise serializers.ValidationError('Credenciais inválidas.')
        else:
            raise serializers.ValidationError('Username e password são obrigatórios.')

class UsuarioClienteSerializer(serializers.ModelSerializer):
    """Serializer para usuários clientes"""
    cliente_nome = serializers.CharField(source='cliente.razao_social', read_only=True)
    cliente_cnpj = serializers.CharField(source='cliente.cnpj', read_only=True)
    
    class Meta:
        model = UsuarioCliente
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'telefone', 'cargo', 'cliente', 'cliente_nome', 'cliente_cnpj',
            'telegram_chat_id', 'ativo', 'is_cliente', 'is_admin_mandacaru',
            'last_login', 'date_joined'
        ]
        read_only_fields = [
            'id', 'cliente_nome', 'cliente_cnpj', 'is_cliente', 
            'is_admin_mandacaru', 'last_login', 'date_joined'
        ]

class PerfilClienteSerializer(serializers.ModelSerializer):
    """Serializer para o cliente atualizar seu próprio perfil"""
    class Meta:
        model = UsuarioCliente
        fields = ['first_name', 'last_name', 'email', 'telefone']

