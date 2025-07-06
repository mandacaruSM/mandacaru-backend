from django.db import models
from decimal import Decimal

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
