# backend/apps/ordens_servico/models.py
from django.db import models
from backend.apps.orcamentos.models import Orcamento
from backend.apps.financeiro.models import ContaReceber

class OrdemServico(models.Model):
    orcamento = models.OneToOneField(Orcamento, on_delete=models.CASCADE)
    descricao_servico = models.TextField()
    data_execucao = models.DateField(auto_now_add=True)
    finalizada = models.BooleanField(default=False)
    criado_via_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"OS #{self.id} para Orçamento #{self.orcamento.id}"

    def finalizar_os(self):
        self.finalizada = True
        self.save()

        # Gera conta a receber no financeiro
        ContaReceber.objects.create(
            cliente=self.orcamento.cliente,
            descricao=f"Ordem de Serviço #{self.id} finalizada",
            valor=self.orcamento.valor,
            vencimento=self.data_execucao
        )