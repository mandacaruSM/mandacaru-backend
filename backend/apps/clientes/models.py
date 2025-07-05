
from django.db import models

class Cliente(models.Model):
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255)

class Empreendimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='empreendimentos')
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)
    localizacao = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.cliente.nome_fantasia})"
