# ----------------------------------------------------------------
# 5. SIGNALS PARA BAIXA AUTOMÁTICA
# backend/apps/abastecimento/signals.py
# ----------------------------------------------------------------

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import RegistroAbastecimento
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=RegistroAbastecimento)
def capturar_estoque_antes_abastecimento(sender, instance, **kwargs):
    """Captura o estoque antes do abastecimento para auditoria"""
    if instance.origem_combustivel == 'ALMOXARIFADO':
        try:
            from backend.apps.almoxarifado.models import EstoqueCombustivel
            
            estoque = EstoqueCombustivel.objects.get(
                tipo_combustivel=instance.tipo_combustivel,
                ativo=True
            )
            instance.estoque_antes_abastecimento = estoque.quantidade_em_estoque
            
        except:
            logger.warning(f"Estoque não encontrado para {instance.tipo_combustivel.nome}")

@receiver(post_save, sender=RegistroAbastecimento)
def processar_baixa_estoque_almoxarifado(sender, instance, created, **kwargs):
    """
    Processa a baixa automática no estoque do almoxarifado
    quando a origem for ALMOXARIFADO
    """
    if not created:
        return
    
    if instance.origem_combustivel != 'ALMOXARIFADO':
        return

    try:
        from backend.apps.almoxarifado.models import EstoqueCombustivel, MovimentacaoEstoque, Produto
        from django.db.models import F
        
        with transaction.atomic():
            # 1. Buscar estoque do combustível
            estoque_combustivel = EstoqueCombustivel.objects.select_for_update().get(
                tipo_combustivel=instance.tipo_combustivel,
                ativo=True
            )
            
            # 2. Verificar estoque suficiente (dupla verificação)
            if estoque_combustivel.quantidade_em_estoque < instance.quantidade_litros:
                logger.error(f"Estoque insuficiente para abastecimento {instance.numero}")
                return
            
            # 3. Realizar baixa no estoque
            estoque_anterior = estoque_combustivel.quantidade_em_estoque
            estoque_combustivel.quantidade_em_estoque -= instance.quantidade_litros
            estoque_combustivel.save()
            
            # 4. Registrar estoque após baixa para auditoria
            instance.estoque_depois_abastecimento = estoque_combustivel.quantidade_em_estoque
            RegistroAbastecimento.objects.filter(id=instance.id).update(
                estoque_depois_abastecimento=estoque_combustivel.quantidade_em_estoque
            )
            
            # 5. Criar movimentação no produto (se existir)
            try:
                produto = Produto.objects.get(codigo=f"COMB_{instance.tipo_combustivel.id}")
                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo='SAIDA',
                    quantidade=instance.quantidade_litros,
                    origem=f"Abastecimento {instance.numero} - {instance.equipamento.nome}"
                )
            except Produto.DoesNotExist:
                # Criar produto automaticamente se não existir
                produto = Produto.objects.create(
                    codigo=f"COMB_{instance.tipo_combustivel.id}",
                    descricao=f"Combustível - {instance.tipo_combustivel.nome}",
                    unidade_medida="L",
                    estoque_atual=estoque_combustivel.quantidade_em_estoque
                )
                
                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo='SAIDA',
                    quantidade=instance.quantidade_litros,
                    origem=f"Abastecimento {instance.numero} - {instance.equipamento.nome}"
                )
            
            logger.info(
                f"✅ Baixa automática realizada: {instance.numero} - "
                f"{instance.quantidade_litros}L de {instance.tipo_combustivel.nome} - "
                f"Estoque: {estoque_anterior}L → {estoque_combustivel.quantidade_em_estoque}L"
            )
            
    except Exception as e:
        logger.error(f"❌ Erro na baixa automática: {str(e)}")