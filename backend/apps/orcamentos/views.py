# backend/apps/orcamentos/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Orcamento
from .serializers import OrcamentoSerializer

class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.prefetch_related('itens__produto').all().order_by('-data_criacao')
    serializer_class = OrcamentoSerializer
    permission_classes = [IsAuthenticated]