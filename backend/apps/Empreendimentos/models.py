# apps/empreendimentos/models.py
from django.db import models
from clientes.models import Cliente

class Empreendimento(models.Model):
    nome = models.CharField(max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='empreendimentos')
    localizacao = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2, help_text="Distância em KM para cálculo de deslocamento")

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome_fantasia})"
