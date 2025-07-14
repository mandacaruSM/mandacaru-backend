# ================================================================
# SUBSTITUIR COMPLETAMENTE backend/apps/equipamentos/serializers.py
# ================================================================

from rest_framework import serializers
from .models import Equipamento

class EquipamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.razao_social', read_only=True)
    empreendimento_nome = serializers.CharField(source='empreendimento.nome', read_only=True)
    tipo = serializers.CharField(source='tipo', read_only=True)  # <-- novo
    
    class Meta:
        model = Equipamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'empreendimento', 'empreendimento_nome',
            'nome', 'descricao', 'tipo', 'categoria', 'marca', 'modelo', 'n_serie', 'horimetro',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'cliente_nome', 'empreendimento_nome', 'tipo']
