# backend/apps/dashboard/models.py
from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Count, Sum, Avg, Q
from decimal import Decimal

class KPISnapshot(models.Model):
    """Snapshot diário dos KPIs para histórico"""
    
    data_snapshot = models.DateField(default=date.today, unique=True)
    
    # Equipamentos
    total_equipamentos = models.IntegerField(default=0)
    equipamentos_operacionais = models.IntegerField(default=0)
    equipamentos_manutencao = models.IntegerField(default=0)
    equipamentos_parados = models.IntegerField(default=0)
    
    # Checklists NR12
    checklists_pendentes = models.IntegerField(default=0)
    checklists_concluidos = models.IntegerField(default=0)
    checklists_com_problemas = models.IntegerField(default=0)
    
    # Manutenção
    manutencoes_vencidas = models.IntegerField(default=0)
    manutencoes_proximas = models.IntegerField(default=0)
    alertas_criticos = models.IntegerField(default=0)
    
    # Financeiro
    contas_vencidas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contas_a_vencer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    faturamento_mes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Controle
    calculado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_snapshot']
        verbose_name = 'Snapshot de KPIs'
        verbose_name_plural = 'Snapshots de KPIs'
    
    def __str__(self):
        return f"KPIs - {self.data_snapshot}"
    
    @classmethod
    def calcular_kpis_hoje(cls):
        """Calcula e salva KPIs do dia atual"""
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import ChecklistNR12, AlertaManutencao
        from backend.apps.financeiro.models import ContaFinanceira
        
        hoje = date.today()
        
        # Equipamentos
        total_eq = Equipamento.objects.filter(ativo=True).count()
        eq_operacional = Equipamento.objects.filter(ativo=True, status='OPERACIONAL').count()
        eq_manutencao = Equipamento.objects.filter(ativo=True, status='MANUTENCAO').count()
        eq_parados = Equipamento.objects.filter(ativo=True, status='PARADO').count()
        
        # Checklists
        chk_pendentes = ChecklistNR12.objects.filter(data_checklist=hoje, status='PENDENTE').count()
        chk_concluidos = ChecklistNR12.objects.filter(data_checklist=hoje, status='CONCLUIDO').count()
        chk_problemas = ChecklistNR12.objects.filter(data_checklist=hoje, status='CONCLUIDO', necessita_manutencao=True).count()
        
        # Manutenção
        manut_vencidas = Equipamento.objects.filter(
            ativo=True,
            proxima_manutencao_preventiva__lt=hoje
        ).count()
        manut_proximas = Equipamento.objects.filter(
            ativo=True,
            proxima_manutencao_preventiva__range=[hoje, hoje + timedelta(days=7)]
        ).count()
        alertas_crit = AlertaManutencao.objects.filter(
            status__in=['ATIVO', 'NOTIFICADO'],
            criticidade='CRITICA'
        ).count()
        
        # Financeiro
        try:
            vencidas = ContaFinanceira.objects.filter(
                status='VENCIDO'
            ).aggregate(total=Sum('valor_restante'))['total'] or 0
            
            a_vencer = ContaFinanceira.objects.filter(
                status='PENDENTE',
                data_vencimento__range=[hoje, hoje + timedelta(days=30)]
            ).aggregate(total=Sum('valor_restante'))['total'] or 0
            
            faturamento = ContaFinanceira.objects.filter(
                tipo='RECEBER',
                status='PAGO',
                data_pagamento__month=hoje.month,
                data_pagamento__year=hoje.year
            ).aggregate(total=Sum('valor_pago'))['total'] or 0
        except:
            vencidas = a_vencer = faturamento = 0
        
        # Salvar snapshot
        snapshot, created = cls.objects.get_or_create(
            data_snapshot=hoje,
            defaults={
                'total_equipamentos': total_eq,
                'equipamentos_operacionais': eq_operacional,
                'equipamentos_manutencao': eq_manutencao,
                'equipamentos_parados': eq_parados,
                'checklists_pendentes': chk_pendentes,
                'checklists_concluidos': chk_concluidos,
                'checklists_com_problemas': chk_problemas,
                'manutencoes_vencidas': manut_vencidas,
                'manutencoes_proximas': manut_proximas,
                'alertas_criticos': alertas_crit,
                'contas_vencidas': vencidas,
                'contas_a_vencer': a_vencer,
                'faturamento_mes': faturamento,
            }
        )
        
        return snapshot


class AlertaDashboard(models.Model):
    """Alertas personalizados do dashboard"""
    
    TIPO_CHOICES = [
        ('EQUIPAMENTO', 'Equipamento'),
        ('CHECKLIST', 'Checklist'),
        ('MANUTENCAO', 'Manutenção'),
        ('FINANCEIRO', 'Financeiro'),
        ('SISTEMA', 'Sistema'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES)
    
    # Links
    link_acao = models.URLField(blank=True, help_text="Link para ação do alerta")
    icone = models.CharField(max_length=50, blank=True, help_text="Ícone do alerta")
    
    # Controle
    ativo = models.BooleanField(default=True)
    exibir_ate = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-prioridade', '-criado_em']
        verbose_name = 'Alerta do Dashboard'
        verbose_name_plural = 'Alertas do Dashboard'
    
    def __str__(self):
        return f"{self.get_prioridade_display()} - {self.titulo}"
    
    @property
    def cor_prioridade(self):
        cores = {
            'BAIXA': '#28a745',
            'MEDIA': '#ffc107',
            'ALTA': '#fd7e14',
            'CRITICA': '#dc3545'
        }
        return cores.get(self.prioridade, '#6c757d')