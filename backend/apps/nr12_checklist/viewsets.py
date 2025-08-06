from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import now
from datetime import date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

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
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


class ItemChecklistPadraoViewSet(viewsets.ModelViewSet):
    queryset = ItemChecklistPadrao.objects.all()
    serializer_class = ItemChecklistPadraoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_equipamento', 'criticidade', 'ativo']
    search_fields = ['item', 'descricao']
    ordering = ['tipo_equipamento', 'ordem']


class ChecklistNR12ViewSet(viewsets.ModelViewSet):
    serializer_class = ChecklistNR12Serializer
    permission_classes = [AllowAny]
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

        responsavel = None

        # 1. Tenta resolver via operador_id (preferido se você estiver passando o operador)
        operador_id = request.data.get("operador_id")
        if operador_id:
            from backend.apps.operadores.models import Operador  # import local para evitar ciclo
            try:
                operador = Operador.objects.get(pk=operador_id)
            except Operador.DoesNotExist:
                return Response({"error": "operador_id inválido."}, status=status.HTTP_400_BAD_REQUEST)

            # Assumindo que Operador tem um campo apontando para User; ajuste se o nome for diferente
            user = getattr(operador, "user", None) or getattr(operador, "usuario", None)
            if not user:
                return Response({"error": "Operador não está vinculado a um User válido."}, status=status.HTTP_400_BAD_REQUEST)
            responsavel = user

        # 2. Se não veio operador_id, tenta pelo responsavel_id direto (User)
        if responsavel is None:
            responsavel_id = request.data.get("responsavel_id")
            responsavel_username = request.data.get("responsavel_username")

            if responsavel_id:
                try:
                    responsavel = User.objects.get(pk=responsavel_id)
                except User.DoesNotExist:
                    return Response({"error": "responsavel_id inválido."}, status=status.HTTP_400_BAD_REQUEST)
            elif responsavel_username:
                try:
                    responsavel = User.objects.get(username=responsavel_username)
                except User.DoesNotExist:
                    return Response({"error": "responsavel_username inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Fallback para request.user, se autenticado
        if responsavel is None:
            if request.user and not request.user.is_anonymous:
                responsavel = request.user
            else:
                return Response(
                    {
                        "error": "Responsável não fornecido e request.user é anônimo. "
                                "Envie 'operador_id' ou 'responsavel_id' válido."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 4. Inicia checklist
        try:
            checklist.iniciar_checklist(responsavel)
            return Response({"message": "Checklist iniciado com sucesso"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.checklist.status not in ['PENDENTE', 'EM_ANDAMENTO']:
            return Response({'error': 'Checklist já foi finalizado'}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Aplica os campos (da primeira versão)
        instance.status = serializer.validated_data['status']
        instance.observacao = serializer.validated_data.get('observacao', '')
        instance.verificado_por = request.user
        instance.verificado_em = timezone.now()
        instance.save()
        return Response(self.get_serializer(instance).data)


class AlertaManutencaoViewSet(viewsets.ModelViewSet):
    serializer_class = AlertaManutencaoSerializer
    permission_classes = [AllowAny]
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
    def iniciar(self, request, pk=None):
        checklist = self.get_object()

        # Tenta pegar responsavel_id do body
        responsavel = None
        responsavel_id = request.data.get("responsavel_id")
        if responsavel_id:
            try:
                responsavel = UsuarioCliente.objects.get(pk=responsavel_id)
            except UsuarioCliente.DoesNotExist:
                return Response(
                    {"error": "responsavel_id inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Se não veio via payload, tenta inferir de request.user
        if responsavel is None:
            # Tente atributos comuns: 'usuario_cliente' ou 'cliente' dependendo de como está modelado
            if hasattr(request.user, "usuario_cliente") and request.user.usuario_cliente:
                responsavel = request.user.usuario_cliente
            elif hasattr(request.user, "cliente") and request.user.cliente:
                # Só caia aqui se 'cliente' de fato for do tipo esperado para responsavel; caso contrário, remova esse ramo.
                responsavel = request.user.cliente
            else:
                return Response(
                    {
                        "error": "Responsável não fornecido e usuário não está vinculado a um UsuarioCliente válido."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            checklist.iniciar_checklist(responsavel)
            return Response({"message": "Checklist iniciado com sucesso"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def marcar_resolvido(self, request, pk=None):
        alerta = self.get_object()
        alerta.marcar_como_resolvido()
        return Response({'message': 'Alerta marcado como resolvido'})
    
class ItemChecklistAtualizarView(APIView):
    permission_classes = [AllowAny]  # Permitir para bot Telegram

    def post(self, request):
        try:
            item = ItemChecklistRealizado.objects.get(id=request.data['id'])
            if item.checklist.status not in ['PENDENTE', 'EM_ANDAMENTO']:
                return Response({'error': 'Checklist já foi finalizado'}, status=400)
            serializer = ItemChecklistRealizadoSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": True, "detail": "Item atualizado com sucesso"})
            return Response({"success": False, "error": serializer.errors}, status=400)
        except ItemChecklistRealizado.DoesNotExist:
            return Response({"success": False, "error": "Item não encontrado"}, status=404)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)