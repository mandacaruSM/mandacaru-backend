from django.db import models
from apps.equipamentos.models import Equipamento

class HistoricoManutencao(models.Model):
    TIPO_CHOICES = (
        ('preventiva', 'Preventiva'),
        ('corretiva', 'Corretiva'),
    )

    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='historicos')
    data = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    custo_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.equipamento} - {self.tipo} - {self.data}"
