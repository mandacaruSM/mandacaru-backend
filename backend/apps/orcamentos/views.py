# apps/orcamentos/views.py
from rest_framework import viewsets
from backend.apps.orcamentos.models import Orcamento
from .serializers import OrcamentoSerializer

class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.all()
    serializer_class = OrcamentoSerializer