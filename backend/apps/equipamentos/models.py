# ================================================================
# MODELO EQUIPAMENTO CORRIGIDO - SEM DUPLICAÇÕES
# backend/apps/equipamentos/models.py
# ================================================================
from backend.apps.abastecimento.qr_mixins import EquipamentoQRMixin
from django.conf import settings
import os
from django.db import models
from datetime import date
from django.contrib.postgres.fields import ArrayField  
from uuid import uuid4
from django.db import models


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
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    """Modelo completo para equipamentos"""

    STATUS_CHOICES = [
        ('OPERACIONAL', 'Operacional'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('PARADO', 'Parado'),
        ('INATIVO', 'Inativo'),
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

    # NR12 - CORREÇÃO: APENAS UM CAMPO DE FREQUÊNCIA
    ativo_nr12 = models.BooleanField(default=True, verbose_name="Ativo para NR12")
    
    # ✅ CORRIGIDO: Apenas um campo para frequências (ArrayField)
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

    @property
    def codigo(self):
        """Gera código único baseado na categoria e ID"""
        if self.categoria:
            return f"{self.categoria.prefixo_codigo}{self.id:04d}"
        return f"EQ{self.id:04d}"

    # ✅ NOVOS MÉTODOS PARA BOT
    def pode_ser_acessado_por_operador(self, operador_codigo):
        """Verifica se operador pode acessar este equipamento via bot"""
        try:
            from backend.apps.operadores.models import Operador
            operador = Operador.objects.get(
                codigo=operador_codigo, 
                status='ATIVO', 
                ativo_bot=True
            )
            return operador.pode_operar_equipamento(self)
        except Operador.DoesNotExist:
            return False

    @property 
    def qr_url_bot(self):
        """URL padronizada para bot acessar equipamento"""
        return f"/bot/equipamento/{self.id}/"

    def get_checklists_hoje(self):
        """Retorna checklists de hoje para este equipamento"""
        from backend.apps.nr12_checklist.models import ChecklistNR12
        hoje = date.today()
        return ChecklistNR12.objects.filter(
            equipamento=self,
            data_checklist=hoje
        )

    def precisa_checklist_hoje(self):
        """Verifica se precisa de checklist hoje baseado na frequência"""
        hoje = date.today()
        
        # Verificar se tem checklist hoje
        checklist_hoje = self.get_checklists_hoje().first()
        if checklist_hoje:
            return False  # Já tem checklist hoje
        
        # Verificar frequências configuradas
        if 'DIARIA' in self.frequencias_checklist:
            return True
        
        if 'SEMANAL' in self.frequencias_checklist:
            # Verificar se é segunda-feira ou se não teve checklist na semana
            if hoje.weekday() == 0:  # Segunda-feira
                return True
        
        if 'MENSAL' in self.frequencias_checklist:
            # Verificar se é dia 1 ou primeiro dia útil do mês
            if hoje.day == 1:
                return True
        
        return False

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
        """Link direto para bot telegram"""
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start=eq{self.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # só depois do primeiro save teremos um ID definido
            self.gerar_qr_png()

    def get_tipo_nr12(self):
        """
        Retorna o tipo de equipamento NR12 associado
        Busca primeiro por associação direta, depois por categoria
        """
        from backend.apps.nr12_checklist.models import TipoEquipamentoNR12
        
        # Verificar se há associação direta
        if hasattr(self, 'tipo_nr12_direto'):
            return self.tipo_nr12_direto
        
        # Buscar por categoria
        if self.categoria:
            tipo_nr12 = TipoEquipamentoNR12.objects.filter(
                categoria_equipamento=self.categoria,
                ativo=True
            ).first()
            if tipo_nr12:
                return tipo_nr12
        
        # Buscar por nome/modelo similar
        if self.modelo:
            # Buscar tipo NR12 que contenha o modelo do equipamento
            tipo_nr12 = TipoEquipamentoNR12.objects.filter(
                nome__icontains=self.modelo.split()[0],  # Primeira palavra do modelo
                ativo=True
            ).first()
            if tipo_nr12:
                return tipo_nr12
        
        # Retornar tipo genérico se existir
        return TipoEquipamentoNR12.objects.filter(
            codigo='GENERICO',
            ativo=True
        ).first()
    
    def get_info_para_bot(self):
        """Retorna informações do equipamento formatadas para o bot"""
        return {
            'id': self.id,
            'numero_serie': self.numero_serie,
            'modelo': self.modelo,
            'fabricante': self.fabricante,
            'categoria': self.categoria.nome if self.categoria else None,
            'status': self.status_operacional,
            'horimetro': float(self.horimetro_atual or 0),
            'cliente': {
                'id': self.cliente.id if self.cliente else None,
                'nome': self.cliente.razao_social if self.cliente else None,
            },
            'empreendimento': {
                'id': self.empreendimento.id if self.empreendimento else None,
                'nome': self.empreendimento.nome if self.empreendimento else None,
            },
            'ativo_nr12': self.ativo_nr12,
            'requer_checklist': self.ativo_nr12,
            'tipo_nr12': {
                'id': self.get_tipo_nr12().id if self.get_tipo_nr12() else None,
                'nome': self.get_tipo_nr12().nome if self.get_tipo_nr12() else None,
            }
        }