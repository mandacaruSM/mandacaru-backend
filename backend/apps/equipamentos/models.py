from django.db import models
from apps.clientes.models import Cliente
from apps.empreendimentos.models import Empreendimento

class Equipamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome
