# backend/apps/operadores/serializers.py
from rest_framework import serializers
from .models import Operador

class OperadorSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Operador
    Usado nas APIs do sistema e do bot Telegram
    """
    
    class Meta:
        model = Operador
        fields = [
            'id',
            'codigo',
            'nome',
            'funcao', 
            'setor',
            'telefone',
            'email',
            'data_nascimento',
            'status',
            'ativo_bot',
            'chat_id_telegram',
            'data_criacao',
            'data_atualizacao'
        ]
        read_only_fields = ['id', 'codigo', 'data_criacao', 'data_atualizacao']
    
    def validate_chat_id_telegram(self, value):
        """Valida se o chat_id não está em uso por outro operador"""
        if value:
            # Se estamos atualizando, excluir o próprio operador da verificação
            queryset = Operador.objects.filter(chat_id_telegram=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Este chat ID já está vinculado a outro operador"
                )
        return value
    
    def to_representation(self, instance):
        """Personaliza a representação do operador"""
        data = super().to_representation(instance)
        
        # Mascarar dados sensíveis se necessário
        if hasattr(self.context.get('request'), 'user'):
            # Se não for admin, omitir dados sensíveis
            pass
        
        # Adicionar campos calculados
        data['nome_completo'] = instance.nome
        data['telefone_formatado'] = instance.telefone if instance.telefone else None
        data['status_display'] = instance.get_status_display() if hasattr(instance, 'get_status_display') else instance.status
        
        return data


class OperadorResumoSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listagens e referências
    """
    
    class Meta:
        model = Operador
        fields = ['id', 'codigo', 'nome', 'funcao', 'status']


class OperadorBotSerializer(serializers.ModelSerializer):
    """
    Serializer específico para o bot Telegram
    Inclui apenas campos necessários para o bot
    """
    
    class Meta:
        model = Operador
        fields = [
            'id',
            'codigo', 
            'nome',
            'funcao',
            'setor',
            'data_nascimento',
            'status',
            'ativo_bot',
            'chat_id_telegram'
        ]
        read_only_fields = ['id', 'codigo']
    
    def to_representation(self, instance):
        """Personaliza dados para o bot"""
        data = super().to_representation(instance)
        
        # Formatar data de nascimento para o bot (DD/MM/AAAA)
        if instance.data_nascimento:
            data['data_nascimento_formatada'] = instance.data_nascimento.strftime('%d/%m/%Y')
        
        # Status mais amigável
        data['ativo'] = instance.status == 'ATIVO' if hasattr(instance, 'status') else True
        
        return data