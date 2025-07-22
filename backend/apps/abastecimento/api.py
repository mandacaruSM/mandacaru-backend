# ----------------------------------------------------------------
# 6. VIEWS E APIs MELHORADAS
# backend/apps/abastecimento/api.py
# ----------------------------------------------------------------

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import RegistroAbastecimento, TipoCombustivel
from .serializers import RegistroAbastecimentoSerializer, TipoCombustivelSerializer

class TipoCombustivelViewSet(viewsets.ModelViewSet):
    queryset = TipoCombustivel.objects.all()
    serializer_class = TipoCombustivelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'descricao']
    
    @action(detail=False, methods=['get'])
    def disponiveis_almoxarifado(self, request):
        """Lista combustíveis disponíveis no almoxarifado"""
        combustiveis_com_estoque = []
        
        for tipo in self.get_queryset().filter(ativo=True):
            estoque = tipo.get_estoque_almoxarifado()
            if estoque and estoque.quantidade_em_estoque > 0:
                combustiveis_com_estoque.append({
                    'id': tipo.id,
                    'nome': tipo.nome,
                    'quantidade_disponivel': float(estoque.quantidade_em_estoque),
                    'estoque_minimo': float(estoque.estoque_minimo),
                    'abaixo_do_minimo': estoque.abaixo_do_minimo,
                    'valor_compra': float(estoque.valor_compra)
                })
        
        return Response({
            'combustiveis_disponiveis': combustiveis_com_estoque,
            'total_tipos': len(combustiveis_com_estoque)
        })
    
    @action(detail=False, methods=['get'])
    def alertas_estoque_baixo(self, request):
        """Lista combustíveis com estoque baixo"""
        alertas = []
        
        for tipo in self.get_queryset().filter(ativo=True):
            if tipo.estoque_baixo:
                estoque = tipo.get_estoque_almoxarifado()
                alertas.append({
                    'id': tipo.id,
                    'nome': tipo.nome,
                    'quantidade_atual': float(estoque.quantidade_em_estoque),
                    'estoque_minimo': float(estoque.estoque_minimo),
                    'diferenca': float(estoque.estoque_minimo - estoque.quantidade_em_estoque),
                    'urgencia': 'CRITICA' if estoque.quantidade_em_estoque <= 0 else 'ALTA'
                })
        
        return Response({
            'alertas': alertas,
            'total_alertas': len(alertas)
        })

class RegistroAbastecimentoViewSet(viewsets.ModelViewSet):
    queryset = RegistroAbastecimento.objects.select_related(
        'equipamento', 'tipo_combustivel', 'criado_por', 'aprovado_por'
    ).all()
    serializer_class = RegistroAbastecimentoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'equipamento', 'origem_combustivel', 'tipo_combustivel', 
        'aprovado', 'registrado_via_bot'
    ]
    search_fields = ['numero', 'equipamento__nome', 'posto_combustivel']
    ordering_fields = ['data_abastecimento', 'valor_total', 'quantidade_litros']
    ordering = ['-data_abastecimento']
    
    @action(detail=False, methods=['get'])
    def estatisticas_almoxarifado(self, request):
        """Estatísticas de abastecimentos do almoxarifado"""
        from django.db.models import Sum, Count, Avg
        from datetime import date, timedelta
        
        # Filtro por período (últimos 30 dias por padrão)
        dias = int(request.query_params.get('dias', 30))
        data_inicio = date.today() - timedelta(days=dias)
        
        abastecimentos_almoxarifado = self.get_queryset().filter(
            origem_combustivel='ALMOXARIFADO',
            data_abastecimento__date__gte=data_inicio
        )
        
        stats = abastecimentos_almoxarifado.aggregate(
            total_abastecimentos=Count('id'),
            total_litros=Sum('quantidade_litros'),
            total_valor=Sum('valor_total'),
            preco_medio=Avg('preco_litro')
        )
        
        # Estatísticas por equipamento
        por_equipamento = abastecimentos_almoxarifado.values(
            'equipamento__nome'
        ).annotate(
            total_litros=Sum('quantidade_litros'),
            total_valor=Sum('valor_total'),
            total_abastecimentos=Count('id')
        ).order_by('-total_litros')
        
        # Estatísticas por combustível
        por_combustivel = abastecimentos_almoxarifado.values(
            'tipo_combustivel__nome'
        ).annotate(
            total_litros=Sum('quantidade_litros'),
            total_valor=Sum('valor_total'),
            total_abastecimentos=Count('id')
        ).order_by('-total_litros')
        
        return Response({
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': date.today(),
                'dias': dias
            },
            'resumo': {
                'total_abastecimentos': stats['total_abastecimentos'] or 0,
                'total_litros': float(stats['total_litros'] or 0),
                'total_valor': float(stats['total_valor'] or 0),
                'preco_medio_litro': float(stats['preco_medio'] or 0)
            },
            'por_equipamento': list(por_equipamento)[:10],
            'por_combustivel': list(por_combustivel)
        })
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """Aprova um abastecimento"""
        abastecimento = self.get_object()
        
        if abastecimento.aprovado:
            return Response(
                {'error': 'Abastecimento já foi aprovado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        abastecimento.aprovado = True
        abastecimento.aprovado_por = request.user
        abastecimento.data_aprovacao = timezone.now()
        abastecimento.save()
        
        return Response({
            'message': 'Abastecimento aprovado com sucesso',
            'aprovado_por': request.user.username,
            'data_aprovacao': abastecimento.data_aprovacao
        })
    
    def perform_create(self, serializer):
        """Override para definir usuário criador"""
        serializer.save(criado_por=self.request.user)