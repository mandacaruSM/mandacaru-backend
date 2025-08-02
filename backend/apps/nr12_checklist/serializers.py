 # 1. ATUALIZAR backend/apps/nr12_checklist/serializers.py
# ================================================================

from rest_framework import serializers
from django.utils import timezone
from datetime import date
from .models import (
    TipoEquipamentoNR12, ItemChecklistPadrao, 
    ChecklistNR12, ItemChecklistRealizado, AlertaManutencao
)

class TipoEquipamentoNR12Serializer(serializers.ModelSerializer):
    """Serializer para tipos de equipamentos NR12"""
    total_itens = serializers.SerializerMethodField()
    
    class Meta:
        model = TipoEquipamentoNR12
        fields = ['id', 'nome', 'descricao', 'total_itens', 'created_at']
    
    def get_total_itens(self, obj):
        return obj.itens_checklist.filter(ativo=True).count()

class ItemChecklistPadraoSerializer(serializers.ModelSerializer):
    """Serializer para itens padrão de checklist"""
    tipo_equipamento_nome = serializers.CharField(source='tipo_equipamento.nome', read_only=True)
    
    class Meta:
        model = ItemChecklistPadrao
        fields = '__all__'

class ItemChecklistRealizadoSerializer(serializers.ModelSerializer):
    """Serializer para itens realizados de checklist"""
    item_padrao_nome = serializers.CharField(source='item_padrao.item', read_only=True)
    item_padrao_criticidade = serializers.CharField(source='item_padrao.criticidade', read_only=True)
    verificado_por_nome = serializers.CharField(source='verificado_por.first_name', read_only=True)
    
    class Meta:
        model = ItemChecklistRealizado
        fields = '__all__'
        read_only_fields = ['verificado_em', 'verificado_por']

    def update(self, instance, validated_data):
        """Atualizar item com dados do usuário"""
        request = self.context.get('request')
        if request and request.user:
            instance.verificado_em = timezone.now()
            instance.verificado_por = request.user
        
        return super().update(instance, validated_data)

class ChecklistNR12Serializer(serializers.ModelSerializer):
    """Serializer para checklists NR12"""
    equipamento_nome = serializers.CharField(source='equipamento.nome', read_only=True)
    cliente_nome = serializers.CharField(source='equipamento.cliente.razao_social', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.first_name', read_only=True)
    
    # Estatísticas
    total_itens = serializers.SerializerMethodField()
    itens_ok = serializers.SerializerMethodField()
    itens_nok = serializers.SerializerMethodField()
    itens_pendentes = serializers.SerializerMethodField()
    percentual_conclusao = serializers.SerializerMethodField()
    
    # URL para QR Code
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ChecklistNR12
        fields = '__all__'
        read_only_fields = ['uuid', 'data_inicio', 'data_conclusao', 'created_at', 'updated_at']
    
    def get_total_itens(self, obj):
        return obj.itens.count()
    
    def get_itens_ok(self, obj):
        return obj.itens.filter(status='OK').count()
    
    def get_itens_nok(self, obj):
        return obj.itens.filter(status='NOK').count()
    
    def get_itens_pendentes(self, obj):
        return obj.itens.filter(status='PENDENTE').count()
    
    def get_percentual_conclusao(self, obj):
        return obj.percentual_conclusao
    
    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if request:
            base_url = request.build_absolute_uri('/')
            return f"{base_url}checklist/{obj.uuid}/"
        return f"/checklist/{obj.uuid}/"

class AlertaManutencaoSerializer(serializers.ModelSerializer):
    """Serializer para alertas de manutenção"""
    equipamento_nome = serializers.CharField(source='equipamento.nome', read_only=True)
    cliente_nome = serializers.CharField(source='equipamento.cliente.razao_social', read_only=True)
    dias_restantes = serializers.SerializerMethodField()
    urgente = serializers.SerializerMethodField()
    
    class Meta:
        model = AlertaManutencao
        fields = '__all__'
        read_only_fields = ['data_identificacao', 'created_at', 'updated_at']
    
    def get_dias_restantes(self, obj):
        return obj.dias_restantes
    
    def get_urgente(self, obj):
        return obj.is_urgente