from django.db import models
from apps.clientes.models import Cliente, Empreendimento

class Equipamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='equipamentos')
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipamentos')
    nome = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True, unique=True)
    ano = models.PositiveIntegerField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.numero_serie})"
