from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.timezone import now
from datetime import date
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


class TipoEquipamentoNR12ViewSet(viewsets.ModelViewSet):
    queryset = TipoEquipamentoNR12.objects.all()
    serializer_class = TipoEquipamentoNR12Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


class ItemChecklistPadraoViewSet(viewsets.ModelViewSet):
    queryset = ItemChecklistPadrao.objects.all()
    serializer_class = ItemChecklistPadraoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_equipamento', 'criticidade', 'ativo']
    search_fields = ['item', 'descricao']
    ordering = ['tipo_equipamento', 'ordem']


class ChecklistNR12ViewSet(viewsets.ModelViewSet):
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
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(equipamento__cliente=self.request.user.cliente)
        return queryset

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        checklist = self.get_object()
        try:
            checklist.iniciar_checklist(request.user)
            return Response({'message': 'Checklist iniciado com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        checklist = self.get_object()
        try:
            checklist.finalizar_checklist()
            return Response({'message': 'Checklist finalizado com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['get'])
    def itens(self, request, pk=None):
        checklist = self.get_object()
        itens = checklist.itens.select_related('item_padrao', 'verificado_por').order_by('item_padrao__ordem')
        serializer = ItemChecklistRealizadoSerializer(itens, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def gerar_diarios(self, request):
        from backend.apps.equipamentos.models import Equipamento
        hoje = date.today()
        equipamentos_ativos = Equipamento.objects.filter(ativo_nr12=True, tipo_nr12__isnull=False)
        checklists_criados = 0
        for equipamento in equipamentos_ativos:
            if not ChecklistNR12.objects.filter(equipamento=equipamento, data_checklist=hoje).exists():
                if equipamento.frequencia_checklist == 'DIARIO':
                    ChecklistNR12.objects.create(
                        equipamento=equipamento,
                        data_checklist=hoje,
                        turno='MANHA'
                    )
                    checklists_criados += 1
        return Response({'message': f'{checklists_criados} checklists criados para hoje', 'data': hoje})

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        from .qr_generator import gerar_qr_code_base64
        checklist = self.get_object()
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
        from .qr_generator import gerar_qr_code_base64
        hoje = date.today()
        checklists_pendentes = ChecklistNR12.objects.filter(data_checklist=hoje, status='PENDENTE').select_related('equipamento')
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
        return Response({'data': hoje, 'total': len(qr_codes), 'qr_codes': qr_codes})


class ItemChecklistRealizadoViewSet(viewsets.ModelViewSet):
    serializer_class = ItemChecklistRealizadoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ItemChecklistRealizado.objects.select_related('checklist', 'item_padrao', 'verificado_por')
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(checklist__equipamento__cliente=self.request.user.cliente)
        return queryset

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        if item.checklist.status not in ['PENDENTE', 'EM_ANDAMENTO']:
            return Response({'error': 'Checklist já foi finalizado'}, status=400)
        return super().update(request, *args, **kwargs)


class AlertaManutencaoViewSet(viewsets.ModelViewSet):
    serializer_class = AlertaManutencaoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'tipo', 'criticidade', 'equipamento']
    search_fields = ['titulo', 'descricao', 'equipamento__nome']
    ordering = ['-data_prevista', '-criticidade']

    def get_queryset(self):
        queryset = AlertaManutencao.objects.select_related('equipamento', 'equipamento__cliente')
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(equipamento__cliente=self.request.user.cliente)
        return queryset

    @action(detail=True, methods=['post'])
    def marcar_notificado(self, request, pk=None):
        alerta = self.get_object()
        alerta.marcar_como_notificado()
        return Response({'message': 'Alerta marcado como notificado'})

    @action(detail=True, methods=['post'])
    def marcar_resolvido(self, request, pk=None):
        alerta = self.get_object()
        alerta.marcar_como_resolvido()
        return Response({'message': 'Alerta marcado como resolvido'})
