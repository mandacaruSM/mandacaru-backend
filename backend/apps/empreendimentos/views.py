# backend/apps/empreendimentos/views.py

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Empreendimento
from .serializers import EmpreendimentoSerializer

class EmpreendimentoViewSet(viewsets.ModelViewSet):
    serializer_class = EmpreendimentoSerializer
    queryset = Empreendimento.objects.all()

    def get_queryset(self):
        """
        Se vier ?cliente=<id>, filtra por esse cliente,
        senão retorna todos (ou talvez nenhum, se preferir).
        """
        qs = super().get_queryset()
        cliente_id = self.request.query_params.get('cliente')
        if cliente_id is not None:
            qs = qs.filter(cliente_id=cliente_id)
        return qs
