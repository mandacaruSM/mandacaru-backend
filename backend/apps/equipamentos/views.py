# ================================================================
# SUBSTITUIR COMPLETAMENTE backend/apps/equipamentos/views.py
# ================================================================

from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipamento
from .serializers import EquipamentoSerializer

class EquipamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar equipamentos"""
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer
    
    # Filtros e busca
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['cliente', 'empreendimento', 'tipo', 'marca']
    search_fields = ['nome', 'marca', 'modelo', 'n_serie']
    ordering_fields = ['nome', 'marca', 'horimetro', 'created_at']
    ordering = ['nome']

    def get_queryset(self):
        """Filtra equipamentos baseado no usuário"""
        queryset = super().get_queryset()
        
        # Se o usuário é um cliente, só mostra equipamentos do seu cliente
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            queryset = queryset.filter(cliente=self.request.user.cliente)
        
        return queryset