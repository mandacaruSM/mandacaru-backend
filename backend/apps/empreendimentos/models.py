from django.db import models
from backend.apps.clientes.models import Cliente

class Empreendimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="empreendimentos")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    endereco = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome_fantasia})"
