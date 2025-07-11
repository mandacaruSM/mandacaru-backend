# ================================================================
# SUBSTITUIR COMPLETAMENTE backend/apps/equipamentos/models.py
# ================================================================

from django.db import models
from backend.apps.clientes.models import Cliente
from backend.apps.empreendimentos.models import Empreendimento

class Equipamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.CASCADE, verbose_name="Empreendimento")
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    tipo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo")
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    n_serie = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Número de Série")
    horimetro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Horímetro")
    
    # Novos campos para NR12
    tipo_nr12 = models.ForeignKey(
        'nr12_checklist.TipoEquipamentoNR12', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Tipo NR12"
    )
    frequencia_checklist = models.CharField(
        max_length=10, 
        choices=[
            ('DIARIO', 'Diário'),
            ('SEMANAL', 'Semanal'),
            ('QUINZENAL', 'Quinzenal'),
            ('MENSAL', 'Mensal')
        ],
        default='DIARIO',
        verbose_name="Frequência do Checklist"
    )
    ativo_nr12 = models.BooleanField(default=True, verbose_name="Ativo para NR12")
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['nome']
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"

    def __str__(self):
        return self.nome

    @property
    def cliente_nome(self):
        return self.cliente.razao_social if self.cliente else ""

    @property
    def empreendimento_nome(self):
        return self.empreendimento.nome if self.empreendimento else ""

    @property
    def tem_checklist_pendente_hoje(self):
        """Verifica se há checklist pendente para hoje"""
        from datetime import date
        # Esta propriedade será implementada quando o sistema NR12 estiver completo
        return False