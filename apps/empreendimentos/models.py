from django.db import models
from apps.clientes.models import Cliente

class Empreendimento(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="empreendimentos"  # ESSENCIAL PARA O SERIALIZER FUNCIONAR
    )
    nome = models.CharField(max_length=255)
    localizacao = models.CharField(max_length=255)
    descricao = models.TextField()
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.nome
