from django.db import models

class Fornecedor(models.Model):
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=100, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.TextField(blank=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome_fantasia
