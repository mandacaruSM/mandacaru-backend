# ================================================================
# SERIALIZER EQUIPAMENTO CORRIGIDO
# backend/apps/equipamentos/serializers.py
# ================================================================

from rest_framework import serializers
from .models import Equipamento, CategoriaEquipamento

class CategoriaEquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaEquipamento
        fields = ['id', 'codigo', 'nome', 'descricao', 'prefixo_codigo', 'ativo']

class EquipamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.razao_social', read_only=True)
    empreendimento_nome = serializers.CharField(source='empreendimento.nome', read_only=True)
    tipo = serializers.CharField(source='tipo', read_only=True)
    codigo = serializers.CharField(source='codigo', read_only=True)  # Código gerado automaticamente
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    # ✅ CORRIGIDO: Campo frequencias_checklist (plural, ArrayField)
    frequencias_checklist = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('DIARIA', 'Diária'),
            ('SEMANAL', 'Semanal'),
            ('MENSAL', 'Mensal'),
        ]),
        required=False,
        allow_empty=True
    )
    
    # Campos para bot
    qr_url_bot = serializers.CharField(source='qr_url_bot', read_only=True)
    bot_link = serializers.CharField(source='bot_link', read_only=True)
    precisa_checklist_hoje = serializers.BooleanField(source='precisa_checklist_hoje', read_only=True)
    
    class Meta:
        model = Equipamento
        fields = [
            'id', 'codigo', 'nome', 'descricao', 'tipo', 'categoria', 'categoria_nome',
            'marca', 'modelo', 'n_serie', 'horimetro', 'horimetro_atual',
            'status', 'status_operacional', 'ativo', 'ativo_nr12',
            'cliente', 'cliente_nome', 'empreendimento', 'empreendimento_nome',
            'frequencias_checklist', 'tipo_nr12',
            'operador_atual', 'localizacao_atual', 'data_inicio_uso',
            'qr_url_bot', 'bot_link', 'precisa_checklist_hoje',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'codigo', 'created_at', 'updated_at', 'cliente_nome', 
            'empreendimento_nome', 'tipo', 'categoria_nome', 'qr_url_bot', 
            'bot_link', 'precisa_checklist_hoje'
        ]

class EquipamentoBotSerializer(serializers.ModelSerializer):
    """Serializer específico para uso do bot - campos essenciais"""
    codigo = serializers.CharField(source='codigo', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    cliente_nome = serializers.CharField(source='cliente.razao_social', read_only=True)
    operador_atual_nome = serializers.CharField(source='operador_atual.nome', read_only=True)
    checklists_hoje = serializers.SerializerMethodField()
    acoes_disponiveis = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipamento
        fields = [
            'id', 'codigo', 'nome', 'categoria_nome', 'marca', 'modelo',
            'status_operacional', 'ativo_nr12', 'cliente_nome',
            'horimetro_atual', 'operador_atual_nome', 'localizacao_atual',
            'checklists_hoje', 'acoes_disponiveis'
        ]
    
    def get_checklists_hoje(self, obj):
        """Retorna checklists de hoje para o bot"""
        checklists = obj.get_checklists_hoje()
        return [{
            'id': c.id,
            'uuid': str(c.uuid),
            'turno': c.turno,
            'status': c.status,
            'frequencia': c.frequencia if hasattr(c, 'frequencia') else 'DIARIA'
        } for c in checklists]
    
    def get_acoes_disponiveis(self, obj):
        """Retorna ações disponíveis para o bot"""
        acoes = []
        
        if obj.ativo_nr12 and obj.status_operacional in ['DISPONIVEL', 'PARADO']:
            if obj.precisa_checklist_hoje():
                acoes.append('criar_checklist')
            
            checklists_hoje = obj.get_checklists_hoje()
            for checklist in checklists_hoje:
                if checklist.status == 'PENDENTE':
                    acoes.append('iniciar_checklist')
                elif checklist.status == 'EM_ANDAMENTO':
                    acoes.extend(['continuar_checklist', 'finalizar_checklist'])
        
        # Ações sempre disponíveis
        acoes.extend([
            'registrar_abastecimento',
            'reportar_anomalia', 
            'consultar_relatorio'
        ])
        
        return acoes