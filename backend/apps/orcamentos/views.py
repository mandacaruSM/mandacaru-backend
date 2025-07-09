# backend/apps/orcamentos/views.py
from rest_framework import viewsets

from .models import Orcamento
from .serializers import OrcamentoSerializer

class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.all().order_by('-data_criacao')
    serializer_class = OrcamentoSerializer