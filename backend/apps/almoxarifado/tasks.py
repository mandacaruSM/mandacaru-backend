# ----------------------------------------------------------------
# 11. TASKS CELERY PARA AUTOMAÇÃO
# backend/apps/almoxarifado/tasks.py
# ----------------------------------------------------------------

from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta
from .models import EstoqueCombustivel
from .notifications import NotificacaoEstoque
import logging

logger = logging.getLogger(__name__)

@shared_task
def verificar_estoques_baixos():
    """Task para verificar estoques baixos e enviar alertas"""
    try:
        estoques_baixos = EstoqueCombustivel.objects.filter(
            ativo=True
        ).select_related('tipo_combustivel')
        
        alertas_enviados = 0
        
        for estoque in estoques_baixos:
            if estoque.abaixo_do_minimo:
                NotificacaoEstoque.enviar_alerta_estoque_baixo(estoque)
                alertas_enviados += 1
        
        logger.info(f"✅ Verificação de estoque concluída: {alertas_enviados} alertas enviados")
        return f"Alertas enviados: {alertas_enviados}"
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação de estoque: {e}")
        raise

@shared_task
def enviar_relatorio_consumo_diario():
    """Task para enviar relatório diário de consumo"""
    try:
        NotificacaoEstoque.enviar_relatorio_consumo_diario()
        return "Relatório diário enviado com sucesso"
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar relatório diário: {e}")
        raise

@shared_task
def consolidar_movimentacoes_diarias():
    """Task para consolidar movimentações diárias"""
    try:
        from .models import MovimentacaoEstoque, Produto
        from django.db.models import Sum
        
        ontem = date.today() - timedelta(days=1)
        
        # Atualizar estoques dos produtos baseado nas movimentações
        produtos_combustivel = Produto.objects.filter(
            codigo__startswith='COMB_'
        )
        
        atualizados = 0
        
        for produto in produtos_combustivel:
            # Calcular saldo das movimentações de ontem
            movimentacoes_ontem = MovimentacaoEstoque.objects.filter(
                produto=produto,
                data__date=ontem
            )
            
            entradas = movimentacoes_ontem.filter(tipo='ENTRADA').aggregate(
                total=Sum('quantidade')
            )['total'] or 0
            
            saidas = movimentacoes_ontem.filter(tipo='SAIDA').aggregate(
                total=Sum('quantidade')
            )['total'] or 0
            
            if entradas > 0 or saidas > 0:
                # Atualizar estoque do produto
                produto.estoque_atual = max(0, produto.estoque_atual + entradas - saidas)
                produto.save()
                atualizados += 1
                
                logger.info(
                    f"📦 {produto.descricao}: "
                    f"Entradas: {entradas}L, Saídas: {saidas}L, "
                    f"Estoque: {produto.estoque_atual}L"
                )
        
        return f"Produtos atualizados: {atualizados}"
        
    except Exception as e:
        logger.error(f"❌ Erro na consolidação: {e}")
        raise
