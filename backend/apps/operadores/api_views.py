from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from .models import Operador
from .serializers import OperadorSerializer

class OperadorViewSet(viewsets.ModelViewSet):
    queryset = Operador.objects.all()
    serializer_class = OperadorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'cpf', 'codigo']
    permission_classes = [AllowAny]