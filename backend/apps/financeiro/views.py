from rest_framework import viewsets
from .models import ContaFinanceira
from .serializers import ContaFinanceiraSerializer

class ContaFinanceiraViewSet(viewsets.ModelViewSet):
    queryset = ContaFinanceira.objects.all()
    serializer_class = ContaFinanceiraSerializer
