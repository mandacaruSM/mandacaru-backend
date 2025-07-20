# ================================================================
# MODELO EQUIPAMENTO COMPLETO E CORRIGIDO
# backend/apps/equipamentos/models.py
# ================================================================
from backend.apps.abastecimento.qr_mixins import EquipamentoQRMixin
from django.conf import settings
import os
from django.db import models
from datetime import date
from django.contrib.postgres.fields import ArrayField  # Adicione no topo se ainda não tiver

class CategoriaEquipamento(models.Model):
    """Categorias de equipamentos para organização"""
    
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    prefixo_codigo = models.CharField(max_length=5, verbose_name="Prefixo do Código")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        ordering = ['codigo']
        verbose_name = 'Categoria de Equipamento'
        verbose_name_plural = 'Categorias de Equipamentos'
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Equipamento(EquipamentoQRMixin, models.Model):
    """Modelo completo para equipamentos"""

    STATUS_CHOICES = [
        ('OPERACIONAL', 'Operacional'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('PARADO', 'Parado'),
        ('INATIVO', 'Inativo'),
    ]

    FREQUENCIA_CHOICES = [
        ('DIARIO', 'Diário'),
        ('SEMANAL', 'Semanal'),
        ('QUINZENAL', 'Quinzenal'),
        ('MENSAL', 'Mensal'),
    ]

    STATUS_OPERACIONAL_CHOICES = [
        ('OPERANDO', 'Em Operação'),
        ('PARADO', 'Parado'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('QUEBRADO', 'Quebrado'),
        ('DISPONIVEL', 'Disponível'),
    ]

    # Campos básicos
    nome = models.CharField(max_length=100, verbose_name="Nome")
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    # Categoria
    categoria = models.ForeignKey(
        CategoriaEquipamento,
        on_delete=models.PROTECT,
        related_name='equipamentos',
        verbose_name="Categoria"
    )

    # Especificações técnicas
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    n_serie = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Número de Série")

    # Horímetros
    horimetro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Horímetro")
    horimetro_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Horímetro Atual")

    # Status e controle operacional
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPERACIONAL', verbose_name="Status")
    status_operacional = models.CharField(max_length=15, choices=STATUS_OPERACIONAL_CHOICES, default='DISPONIVEL', verbose_name="Status Operacional")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    # Relacionamentos
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, verbose_name="Cliente")
    empreendimento = models.ForeignKey('empreendimentos.Empreendimento', on_delete=models.CASCADE, verbose_name="Empreendimento")

    # NR12
    ativo_nr12 = models.BooleanField(default=True, verbose_name="Ativo para NR12")

    frequencias_checklist = ArrayField(
        models.CharField(max_length=10, choices=[
            ('DIARIA', 'Diária'),
            ('SEMANAL', 'Semanal'),
            ('MENSAL', 'Mensal'),
        ]),
        default=list,
        blank=True,
        verbose_name='Frequência(s) do Checklist NR12'
    )

    tipo_nr12 = models.ForeignKey(
        'nr12_checklist.TipoEquipamentoNR12',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo NR12"
    )
    # Manutenção
    proxima_manutencao_preventiva = models.DateField(null=True, blank=True, verbose_name="Próxima Manutenção Preventiva")

    # Controle de uso
    operador_atual = models.ForeignKey(
        'operadores.Operador',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipamentos_em_uso',
        help_text='Operador que está usando este equipamento'
    )
    data_inicio_uso = models.DateTimeField(null=True, blank=True)
    localizacao_atual = models.CharField(max_length=200, blank=True)

    # Restrições de acesso
    requer_cnh = models.BooleanField(default=False)
    categoria_cnh_necessaria = models.CharField(max_length=5, blank=True)
    nivel_experiencia_minimo = models.IntegerField(
        default=0,
        help_text='Anos mínimos de experiência necessários'
    )

    # Controle de datas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['nome']
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'

    def __str__(self):
        return f"{self.nome} ({self.categoria.codigo})"

    @property
    def tipo(self):
        """Retorna o nome da categoria para compatibilidade"""
        return self.categoria.nome if self.categoria else ''

    def pode_ser_operado_por(self, operador):
        """Verifica se operador pode usar este equipamento"""
        return operador.pode_operar_equipamento(self)

    def iniciar_uso(self, operador):
        """Registrar início de uso por operador"""
        from django.utils import timezone
        if self.operador_atual and self.operador_atual != operador:
            raise ValueError(f"Equipamento já está sendo usado por {self.operador_atual.nome}")
        self.operador_atual = operador
        self.data_inicio_uso = timezone.now()
        self.status_operacional = 'OPERANDO'
        self.save()
        operador.ultimo_equipamento_usado = self
        operador.save()

    def finalizar_uso(self):
        """Finalizar uso do equipamento"""
        self.operador_atual = None
        self.data_inicio_uso = None
        self.status_operacional = 'DISPONIVEL'
        self.save()

    @property
    def bot_link(self):
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start=eq{self.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # só depois do primeiro save teremos um ID definido
            self.gerar_qr_png()
