# backend/apps/operadores/api_views.py

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Operador
from .serializers import OperadorSerializer, OperadorListSerializer

class OperadorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD dos operadores via API
    """
    queryset = Operador.objects.all()
    serializer_class = OperadorSerializer
    permission_classes = [AllowAny]  # ✅ Permite acesso sem autenticação
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'cpf', 'codigo', 'telefone', 'email']
    filterset_fields = ['status', 'setor', 'funcao', 'ativo_bot']
    ordering_fields = ['nome', 'codigo', 'data_admissao']
    ordering = ['nome']

    def get_serializer_class(self):
        """Usar serializer simplificado para listagem"""
        if self.action == 'list':
            return OperadorListSerializer
        return OperadorSerializer

    def get_queryset(self):
        """Filtros personalizados para busca"""
        queryset = super().get_queryset()
        
        # Filtro de busca customizado
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(cpf__icontains=search) |
                Q(codigo__icontains=search) |
                Q(telefone__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filtro por chat_id
        chat_id = self.request.query_params.get('chat_id_telegram', None)
        if chat_id:
            queryset = queryset.filter(chat_id_telegram=chat_id)
        
        return queryset

    @action(detail=True, methods=['patch'])
    def registrar_chat_id(self, request, pk=None):
        """Registra o chat_id do Telegram no operador"""
        operador = self.get_object()
        chat_id = request.data.get('chat_id_telegram')
        
        if not chat_id:
            return Response(
                {'error': 'chat_id_telegram é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        operador.chat_id_telegram = chat_id
        operador.ativo_bot = True
        operador.save()
        
        serializer = self.get_serializer(operador)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def buscar_por_chat_id(self, request):
        """Busca operador pelo chat_id do Telegram"""
        chat_id = request.query_params.get('chat_id')
        
        if not chat_id:
            return Response(
                {'error': 'chat_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            operador = Operador.objects.get(chat_id_telegram=chat_id)
            serializer = self.get_serializer(operador)
            return Response(serializer.data)
        except Operador.DoesNotExist:
            return Response(
                {'error': 'Operador não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def atualizar_acesso_bot(self, request, pk=None):
        """Atualiza último acesso do bot"""
        operador = self.get_object()
        operador.atualizar_ultimo_acesso_bot()
        
        return Response({'message': 'Último acesso atualizado com sucesso'})