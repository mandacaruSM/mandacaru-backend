from django.db import models
from backend.apps.clientes.models import Cliente
from backend.apps.equipamentos.models import Equipamento
from backend.apps.empreendimentos.models import Empreendimento

class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empreendimento = models.ForeignKey(Empreendimento, null=False, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Orçamento #{self.id} - {self.cliente.nome_fantasia}"
