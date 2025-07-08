# apps/ordens_servico/views.py

from rest_framework import viewsets
from backend.apps.ordens_servico.models import OrdemServico
from .serializers import OrdemServicoSerializer

class OrdemServicoViewSet(viewsets.ModelViewSet):
    serializer_class = OrdemServicoSerializer

    def get_queryset(self):
        queryset = OrdemServico.objects.all()
        finalizada = self.request.query_params.get('finalizada')

        if finalizada is not None:
            if finalizada.lower() == 'true':
                queryset = queryset.filter(finalizada=True)
            elif finalizada.lower() == 'false':
                queryset = queryset.filter(finalizada=False)

        return queryset
