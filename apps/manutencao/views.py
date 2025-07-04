from rest_framework import viewsets
from .models import HistoricoManutencao
from .serializers import HistoricoManutencaoSerializer

class HistoricoManutencaoViewSet(viewsets.ModelViewSet):
    queryset = HistoricoManutencao.objects.all()
    serializer_class = HistoricoManutencaoSerializer
