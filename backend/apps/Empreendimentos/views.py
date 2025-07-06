# apps/empreendimentos/views.py
from rest_framework import viewsets
from .models import Empreendimento
from .serializers import EmpreendimentoSerializer

class EmpreendimentoViewSet(viewsets.ModelViewSet):
    queryset = Empreendimento.objects.all()
    serializer_class = EmpreendimentoSerializer
