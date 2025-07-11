# 2. ATUALIZAR backend/apps/nr12_checklist/views.py
# ================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    TipoEquipamentoNR12, ItemChecklistPadrao, 
    ChecklistNR12, ItemChecklistRealizado, AlertaManutencao
)
from .serializers import (
    TipoEquipamentoNR12Serializer, ItemChecklistPadraoSerializer,
    ChecklistNR12Serializer, ItemChecklistRealizadoSerializer, 
    AlertaManutencaoSerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])  # Acesso via QR Code sem autenticação
def checklist_por_uuid(request, checklist_uuid):
    """Acessa checklist via QR Code usando UUID"""
    try:
        checklist = ChecklistNR12.objects.get(uuid=checklist_uuid)
        
        # Dados básicos do checklist
        data = {
            'id': checklist.id,
            'uuid': str(checklist.uuid),
            'equipamento': {
                'id': checklist.equipamento.id,
                'nome': checklist.equipamento.nome,
                'marca': checklist.equipamento.marca,
                'modelo': checklist.equipamento.modelo,
                'cliente': checklist.equipamento.cliente.razao_social
            },
            'data_checklist': checklist.data_checklist,
            'turno': checklist.turno,
            'status': checklist.status,
            'responsavel': checklist.responsavel.username if checklist.responsavel else None,
            'pode_editar': checklist.status in ['PENDENTE', 'EM_ANDAMENTO'],
            'link_bot': f"https://t.me/seu_bot?start=checklist_{checklist.uuid}",
            'percentual_conclusao': checklist.percentual_conclusao
        }
        
        return Response(data)
        
    except ChecklistNR12.DoesNotExist:
        return Response({'error': 'Checklist não encontrado'}, status=404)

class TipoEquipamentoNR12ViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de equipamentos NR12"""
    queryset = TipoEquipamentoNR12.objects.all()
    serializer_class = TipoEquipamentoNR12Serializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering = ['nome']

class ItemChecklistPadraoViewSet(viewsets.ModelViewSet):
    """ViewSet para itens padrão de checklist"""
    queryset = ItemChecklistPadrao.objects.all()
    serializer_class = ItemChecklistPadraoSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_equipamento', 'criticidade', 'ativo']
    search_fields = ['item', 'descricao']
    ordering = ['tipo_equipamento', 'ordem']

class ChecklistNR12ViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar checklists NR12"""
    serializer_class = ChecklistNR12Serializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'turno', 'equipamento', 'equipamento__cliente']
    search_fields = ['equipamento__nome', 'responsavel__username']
    ordering = ['-data_checklist', '-created_at']

    def get_queryset(self):
        queryset = ChecklistNR12.objects.select_related(
            'equipamento', 'equipamento__cliente', 'responsavel'
        ).prefetch_related('itens')
        
        # Filtro por cliente (se for usuário cliente)
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(equipamento__cliente=self.request.user.cliente)
        
        return queryset

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Inicia um checklist"""
        checklist = self.get_object()
        
        try:
            checklist.iniciar_checklist(request.user)
            return Response({'message': 'Checklist iniciado com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """Finaliza um checklist"""
        checklist = self.get_object()
        
        try:
            checklist.finalizar_checklist()
            return Response({'message': 'Checklist finalizado com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['get'])
    def itens(self, request, pk=None):
        """Lista itens do checklist"""
        checklist = self.get_object()
        itens = checklist.itens.select_related('item_padrao', 'verificado_por').order_by('item_padrao__ordem')
        
        serializer = ItemChecklistRealizadoSerializer(itens, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def gerar_diarios(self, request):
        """Gera checklists diários para equipamentos ativos"""
        from backend.apps.equipamentos.models import Equipamento
        
        hoje = date.today()
        equipamentos_ativos = Equipamento.objects.filter(
            ativo_nr12=True, 
            tipo_nr12__isnull=False
        )
        
        
        checklists_criados = 0
        
        for equipamento in equipamentos_ativos:
            # Verificar se já existe checklist para hoje
            if not ChecklistNR12.objects.filter(
                equipamento=equipamento, 
                data_checklist=hoje
            ).exists():
                # Criar checklist baseado na frequência
                if equipamento.frequencia_checklist == 'DIARIO':
                    ChecklistNR12.objects.create(
                        equipamento=equipamento,
                        data_checklist=hoje,
                        turno='MANHA'
                    )
                    checklists_criados += 1
        
        return Response({
            'message': f'{checklists_criados} checklists criados para hoje',
            'data': hoje
        })
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Gera QR Code para o checklist"""
        checklist = self.get_object()
        
        from .qr_generator import gerar_qr_code_base64
        qr_data = gerar_qr_code_base64(checklist)
        
        return Response({
            'checklist': {
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'equipamento': checklist.equipamento.nome,
                'data_checklist': checklist.data_checklist,
                'turno': checklist.turno,
                'status': checklist.status
            },
            'qr_code': qr_data
        })

    @action(detail=False, methods=['get'])
    def qr_codes_pendentes(self, request):
        """Lista QR Codes de checklists pendentes de hoje"""
        from .qr_generator import gerar_qr_code_base64
        
        hoje = date.today()
        checklists_pendentes = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).select_related('equipamento')
        
        qr_codes = []
        for checklist in checklists_pendentes:
            qr_data = gerar_qr_code_base64(checklist)
            qr_codes.append({
                'checklist_id': checklist.id,
                'equipamento': checklist.equipamento.nome,
                'turno': checklist.turno,
                'qr_code_base64': qr_data['qr_code_base64'],
                'url': qr_data['url']
            })
        
        return Response({
            'data': hoje,
            'total': len(qr_codes),
            'qr_codes': qr_codes
        })

class ItemChecklistRealizadoViewSet(viewsets.ModelViewSet):
    """ViewSet para itens individuais do checklist"""
    serializer_class = ItemChecklistRealizadoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ItemChecklistRealizado.objects.select_related(
            'checklist', 'item_padrao', 'verificado_por'
        )
        
        # Filtro por cliente
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(checklist__equipamento__cliente=self.request.user.cliente)
        
        return queryset

    def update(self, request, *args, **kwargs):
        """Atualizar item do checklist"""
        item = self.get_object()
        
        # Verificar se o checklist ainda pode ser editado
        if item.checklist.status not in ['PENDENTE', 'EM_ANDAMENTO']:
            return Response(
                {'error': 'Checklist já foi finalizado'}, 
                status=400
            )
        
        return super().update(request, *args, **kwargs)

class AlertaManutencaoViewSet(viewsets.ModelViewSet):
    """ViewSet para alertas de manutenção"""
    serializer_class = AlertaManutencaoSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'tipo', 'criticidade', 'equipamento']
    search_fields = ['titulo', 'descricao', 'equipamento__nome']
    ordering = ['-data_prevista', '-criticidade']

    def get_queryset(self):
        queryset = AlertaManutencao.objects.select_related('equipamento', 'equipamento__cliente')
        
        # Filtrar por cliente
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(equipamento__cliente=self.request.user.cliente)
        
        return queryset

    @action(detail=True, methods=['post'])
    def marcar_notificado(self, request, pk=None):
        """Marca alerta como notificado"""
        alerta = self.get_object()
        alerta.marcar_como_notificado()
        return Response({'message': 'Alerta marcado como notificado'})

    @action(detail=True, methods=['post'])
    def marcar_resolvido(self, request, pk=None):
        """Marca alerta como resolvido"""
        alerta = self.get_object()
        alerta.marcar_como_resolvido()
        return Response({'message': 'Alerta marcado como resolvido'})