from django.db import models

class Cliente(models.Model):
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return self.razao_social


class Empreendimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='empreendimentos')
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    map_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.cliente.razao_social}"
