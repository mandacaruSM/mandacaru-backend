from django.db import models
from backend.apps.clientes.models import Cliente
from backend.apps.empreendimentos.models import Empreendimento

class Equipamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    n_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    horimetro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nome