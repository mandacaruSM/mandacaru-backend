from rest_framework import viewsets
from .models import OrdemServico
from .serializers import OrdemServicoSerializer

class OrdemServicoViewSet(viewsets.ModelViewSet):
    queryset = OrdemServico.objects.all().order_by('-data_abertura')
    serializer_class = OrdemServicoSerializer
