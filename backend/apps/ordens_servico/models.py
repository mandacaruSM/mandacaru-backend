from django.db import models
from apps.clientes.models import Cliente
from apps.empreendimentos.models import Empreendimento
from apps.equipamentos.models import Equipamento

class OrdemServico(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.CASCADE)
    equipamentos = models.ManyToManyField(Equipamento)
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    responsavel = models.CharField(max_length=100)
    descricao_servico = models.TextField()
    deslocamento_km = models.DecimalField(max_digits=6, decimal_places=2)
    valor_km = models.DecimalField(max_digits=6, decimal_places=2, default=3.00)
    custo_total_deslocamento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('aberta', 'Aberta'), ('concluida', 'Concluída')], default='aberta')

    def calcular_custo_deslocamento(self):
        return self.deslocamento_km * self.valor_km

    def save(self, *args, **kwargs):
        self.custo_total_deslocamento = self.calcular_custo_deslocamento()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OS #{self.id} - {self.cliente.razao_social} - {self.status}"
