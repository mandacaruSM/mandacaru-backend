from rest_framework.views import APIView
from rest_framework.response import Response
from backend.apps.ordens_servico.models import OrdemServico
from backend.apps.almoxarifado.models import Produto
from django.db.models import Count, F

class RelatorioOSPorCliente(APIView):
    def get(self, request):
        dados = OrdemServico.objects.values('cliente__razao_social').annotate(total=Count('id'))
        return Response(dados)

class RelatorioEstoqueBaixo(APIView):
    def get(self, request):
        produtos = Produto.objects.filter(estoque_atual__lt=5).values('codigo', 'descricao', 'estoque_atual')
        return Response(produtos)
