# backend/apps/almoxarifado/models.py

# backend/apps/almoxarifado/models.py

from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from backend.apps.abastecimento.models import TipoCombustivel, RegistroAbastecimento


class Produto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=100)
    unidade_medida = models.CharField(max_length=10)
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    origem = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if is_new:
            if self.tipo == 'ENTRADA':
                self.produto.estoque_atual += self.quantidade
            elif self.tipo == 'SAIDA':
                self.produto.estoque_atual -= self.quantidade

            self.produto.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.produto} - {self.quantidade}"


class EstoqueCombustivel(models.Model):
    """
    Estoque específico para combustíveis, usado no módulo de abastecimento.
    """
    tipo_combustivel = models.OneToOneField(
        TipoCombustivel,
        on_delete=models.CASCADE,
        related_name='estoque_almoxarifado',
        verbose_name='Tipo de Combustível'
    )
    quantidade_em_estoque = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name='Quantidade em Estoque (litros)'
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name='Estoque Mínimo (litros)',
        help_text='Quando o estoque chegar a este nível, dispara alerta de reposição.'
    )
    valor_compra = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name='Preço de Compra (R$/litro)'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Registro Ativo',
        help_text='Desative para ocultar sem perder histórico.'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Estoque de Combustível'
        verbose_name_plural = 'Estoques de Combustíveis'
        ordering = ['tipo_combustivel']

    def __str__(self):
        return f"{self.tipo_combustivel.nome}: {self.quantidade_em_estoque} {self.tipo_combustivel.unidade_medida}"

    def clean(self):
        super().clean()
        erros = {}
        if self.quantidade_em_estoque < 0:
            erros['quantidade_em_estoque'] = 'Quantidade em estoque não pode ser negativa.'
        if self.estoque_minimo < 0:
            erros['estoque_minimo'] = 'Estoque mínimo não pode ser negativo.'
        if self.valor_compra < 0:
            erros['valor_compra'] = 'Preço de compra não pode ser negativo.'
        if erros:
            raise ValidationError(erros)

    @property
    def abaixo_do_minimo(self) -> bool:
        """
        True se a quantidade atual estiver igual ou abaixo do estoque mínimo,
        indicando que é preciso repor.
        """
        return self.quantidade_em_estoque <= self.estoque_minimo


@receiver(post_save, sender=RegistroAbastecimento)
def baixa_estoque_combustivel(sender, instance, created, **kwargs):
    """
    Quando um novo RegistroAbastecimento é criado,
    subtrai a quantidade de litros do EstoqueCombustivel correspondente.
    """
    if not created:
        return

    EstoqueCombustivel.objects.filter(
        tipo_combustivel=instance.tipo_combustivel
    ).update(
        quantidade_em_estoque=F('quantidade_em_estoque') - instance.quantidade_litros
    )
