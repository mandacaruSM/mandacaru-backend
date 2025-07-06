from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.equipamentos.models import Equipamento

class HistoricoManutencao(models.Model):
    TIPO_MANUTENCAO_CHOICES = [
        ("preventiva", "Preventiva"),
        ("corretiva", "Corretiva"),
    ]

    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name="manutencoes")
    tipo = models.CharField(max_length=20, choices=TIPO_MANUTENCAO_CHOICES)
    data = models.DateField()
    horimetro = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tecnico_responsavel = models.CharField(max_length=100)
    descricao = models.TextField()
    observacoes = models.TextField(blank=True, null=True)
    proxima_manutencao = models.DateField(blank=True, null=True)  # Apenas para preventiva

    def clean(self):
        historico_anterior = HistoricoManutencao.objects.filter(
            equipamento=self.equipamento
        ).exclude(id=self.id).order_by("-data").first()

        if historico_anterior and self.horimetro <= historico_anterior.horimetro:
            raise ValidationError("O horímetro deve ser maior do que o da manutenção anterior.")

    def __str__(self):
        return f"{self.equipamento.nome} - {self.data} - {self.tipo}"
