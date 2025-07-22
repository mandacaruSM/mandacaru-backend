# ----------------------------------------------------------------
# 3. SERIALIZERS ATUALIZADOS
# backend/apps/abastecimento/serializers.py
# ----------------------------------------------------------------

from rest_framework import serializers
from .models import RegistroAbastecimento, TipoCombustivel

class TipoCombustivelSerializer(serializers.ModelSerializer):
    quantidade_disponivel_almoxarifado = serializers.ReadOnlyField()
    estoque_baixo = serializers.ReadOnlyField()
    
    class Meta:
        model = TipoCombustivel
        fields = [
            'id', 'nome', 'descricao', 'unidade_medida', 'preco_medio', 'ativo',
            'quantidade_disponivel_almoxarifado', 'estoque_baixo'
        ]

class RegistroAbastecimentoSerializer(serializers.ModelSerializer):
    equipamento_nome = serializers.CharField(source='equipamento.nome', read_only=True)
    tipo_combustivel_nome = serializers.CharField(source='tipo_combustivel.nome', read_only=True)
    consumo_periodo = serializers.ReadOnlyField()
    
    # Campos específicos para controle de almoxarifado
    estoque_disponivel_almoxarifado = serializers.SerializerMethodField()
    alerta_estoque_baixo = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroAbastecimento
        fields = '__all__'
        read_only_fields = [
            'numero', 'valor_total', 'data_registro', 'criado_em', 'atualizado_em',
            'estoque_antes_abastecimento', 'estoque_depois_abastecimento'
        ]
    
    def get_estoque_disponivel_almoxarifado(self, obj):
        """Retorna estoque disponível no almoxarifado"""
        if obj.origem_combustivel == 'ALMOXARIFADO':
            return float(obj.tipo_combustivel.quantidade_disponivel_almoxarifado)
        return None
    
    def get_alerta_estoque_baixo(self, obj):
        """Indica se o estoque ficará baixo após este abastecimento"""
        if obj.origem_combustivel == 'ALMOXARIFADO':
            estoque = obj.tipo_combustivel.get_estoque_almoxarifado()
            if estoque:
                estoque_pos = estoque.quantidade_em_estoque - obj.quantidade_litros
                return estoque_pos <= estoque.estoque_minimo
        return False
    
    def validate(self, data):
        """Validações customizadas"""
        if data.get('origem_combustivel') == 'ALMOXARIFADO':
            tipo_combustivel = data.get('tipo_combustivel')
            quantidade = data.get('quantidade_litros')
            
            if tipo_combustivel and quantidade:
                estoque_disponivel = tipo_combustivel.quantidade_disponivel_almoxarifado
                if quantidade > estoque_disponivel:
                    raise serializers.ValidationError({
                        'quantidade_litros': f'Quantidade solicitada ({quantidade}L) maior que '
                                           f'estoque disponível ({estoque_disponivel}L)'
                    })
        
        return data
