# ================================================================
# CORRIGIR backend/apps/dashboard/models.py
# ================================================================

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
    equipamentos_nr12_ativos = models.IntegerField(default=0)
    
    # Checklists NR12
    checklists_pendentes = models.IntegerField(default=0)
    checklists_concluidos = models.IntegerField(default=0)
    checklists_com_problemas = models.IntegerField(default=0)
    
    # Manutenção
    manutencoes_vencidas = models.IntegerField(default=0)
    manutencoes_proximas = models.IntegerField(default=0)
    alertas_criticos = models.IntegerField(default=0)
    alertas_ativos = models.IntegerField(default=0)
    
    # Financeiro
    contas_vencidas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contas_a_vencer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    faturamento_mes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Estoque
    produtos_estoque_baixo = models.IntegerField(default=0)
    movimentacoes_estoque = models.IntegerField(default=0)
    
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
        hoje = date.today()
        
        # Inicializar contadores
        kpis = {
            'total_equipamentos': 0,
            'equipamentos_operacionais': 0,
            'equipamentos_manutencao': 0,
            'equipamentos_parados': 0,
            'equipamentos_nr12_ativos': 0,
            'checklists_pendentes': 0,
            'checklists_concluidos': 0,
            'checklists_com_problemas': 0,
            'manutencoes_vencidas': 0,
            'manutencoes_proximas': 0,
            'alertas_criticos': 0,
            'alertas_ativos': 0,
            'contas_vencidas': 0,
            'contas_a_vencer': 0,
            'faturamento_mes': 0,
            'produtos_estoque_baixo': 0,
            'movimentacoes_estoque': 0,
        }
        
        # Calcular KPIs de Equipamentos
        try:
            from backend.apps.equipamentos.models import Equipamento
            equipamentos = Equipamento.objects.filter(ativo=True)
            
            kpis['total_equipamentos'] = equipamentos.count()
            kpis['equipamentos_operacionais'] = equipamentos.filter(status='OPERACIONAL').count()
            kpis['equipamentos_manutencao'] = equipamentos.filter(status='MANUTENCAO').count()
            kpis['equipamentos_parados'] = equipamentos.filter(status='PARADO').count()
            kpis['equipamentos_nr12_ativos'] = equipamentos.filter(ativo_nr12=True).count()
            
            # Manutenções
            kpis['manutencoes_vencidas'] = equipamentos.filter(
                proxima_manutencao_preventiva__lt=hoje
            ).count()
            kpis['manutencoes_proximas'] = equipamentos.filter(
                proxima_manutencao_preventiva__range=[hoje, hoje + timedelta(days=7)]
            ).count()
            
        except Exception as e:
            print(f"Erro ao calcular KPIs de equipamentos: {e}")
        
        # Calcular KPIs de Checklists NR12
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12, AlertaManutencao
            
            kpis['checklists_pendentes'] = ChecklistNR12.objects.filter(
                data_checklist=hoje, status='PENDENTE'
            ).count()
            kpis['checklists_concluidos'] = ChecklistNR12.objects.filter(
                data_checklist=hoje, status='CONCLUIDO'
            ).count()
            kpis['checklists_com_problemas'] = ChecklistNR12.objects.filter(
                data_checklist=hoje, status='CONCLUIDO', necessita_manutencao=True
            ).count()
            
            # Alertas
            alertas_ativos = AlertaManutencao.objects.filter(status__in=['ATIVO', 'NOTIFICADO'])
            kpis['alertas_ativos'] = alertas_ativos.count()
            kpis['alertas_criticos'] = alertas_ativos.filter(criticidade='CRITICA').count()
            
        except Exception as e:
            print(f"Erro ao calcular KPIs de checklists: {e}")
        
        # Calcular KPIs Financeiros
        try:
            from backend.apps.financeiro.models import ContaFinanceira
            
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
            
            kpis['contas_vencidas'] = float(vencidas)
            kpis['contas_a_vencer'] = float(a_vencer)
            kpis['faturamento_mes'] = float(faturamento)
            
        except Exception as e:
            print(f"Erro ao calcular KPIs financeiros: {e}")
        
        # Calcular KPIs de Estoque
        try:
            from backend.apps.almoxarifado.models import Produto, MovimentacaoEstoque
            
            kpis['produtos_estoque_baixo'] = Produto.objects.filter(
                estoque_atual__lt=5
            ).count()
            
            kpis['movimentacoes_estoque'] = MovimentacaoEstoque.objects.filter(
                data__date=hoje
            ).count()
            
        except Exception as e:
            print(f"Erro ao calcular KPIs de estoque: {e}")
        
        # Salvar snapshot
        snapshot, created = cls.objects.update_or_create(
            data_snapshot=hoje,
            defaults=kpis
        )
        
        print(f"✅ KPIs calculados para {hoje}: {len([k for k, v in kpis.items() if v > 0])} métricas ativas")
        return snapshot


class AlertaDashboard(models.Model):
    """Alertas personalizados do dashboard"""
    
    TIPO_CHOICES = [
        ('EQUIPAMENTO', 'Equipamento'),
        ('CHECKLIST', 'Checklist'),
        ('MANUTENCAO', 'Manutenção'),
        ('FINANCEIRO', 'Financeiro'),
        ('ESTOQUE', 'Estoque'),
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
    
    # Links e ações
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
        """Cor baseada na prioridade"""
        cores = {
            'BAIXA': '#28a745',   # Verde
            'MEDIA': '#ffc107',   # Amarelo
            'ALTA': '#fd7e14',    # Laranja
            'CRITICA': '#dc3545'  # Vermelho
        }
        return cores.get(self.prioridade, '#6c757d')
    
    @classmethod
    def criar_alerta_automatico(cls, tipo, titulo, descricao, prioridade='MEDIA', link_acao=''):
        """Cria um alerta automático do sistema"""
        return cls.objects.create(
            tipo=tipo,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            link_acao=link_acao,
            icone='⚠️',
            exibir_ate=timezone.now() + timedelta(days=7)
        )


class MetricaPersonalizada(models.Model):
    """Métricas personalizadas para o dashboard"""
    
    TIPO_CALCULO_CHOICES = [
        ('COUNT', 'Contagem'),
        ('SUM', 'Soma'),
        ('AVG', 'Média'),
        ('PERCENTAGE', 'Percentual'),
    ]
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo_calculo = models.CharField(max_length=15, choices=TIPO_CALCULO_CHOICES)
    query_sql = models.TextField(help_text="Query SQL para calcular a métrica")
    
    # Configurações de exibição
    formato_numero = models.CharField(
        max_length=20, 
        default='decimal',
        help_text="Formato: decimal, integer, currency, percentage"
    )
    cor_fundo = models.CharField(max_length=7, default='#f8f9fa')
    icone = models.CharField(max_length=50, blank=True)
    
    # Controle
    ativo = models.BooleanField(default=True)
    ordem_exibicao = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ordem_exibicao', 'nome']
        verbose_name = 'Métrica Personalizada'
        verbose_name_plural = 'Métricas Personalizadas'
    
    def __str__(self):
        return self.nome
    
    def calcular_valor(self):
        """Calcula o valor da métrica usando a query SQL"""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute(self.query_sql)
                resultado = cursor.fetchone()
                
                if resultado:
                    return resultado[0]
                return 0
                
        except Exception as e:
            print(f"Erro ao calcular métrica {self.nome}: {e}")
            return 0


# ================================================================
# FUNÇÕES AUXILIARES PARA O DASHBOARD
# ================================================================

def obter_resumo_dashboard():
    """Retorna resumo completo para o dashboard principal"""
    hoje = date.today()
    
    # Tentar obter snapshot de hoje, senão calcular
    try:
        snapshot = KPISnapshot.objects.get(data_snapshot=hoje)
    except KPISnapshot.DoesNotExist:
        snapshot = KPISnapshot.calcular_kpis_hoje()
    
    # Alertas ativos
    alertas = AlertaDashboard.objects.filter(
        ativo=True,
        exibir_ate__isnull=True
    ).order_by('-prioridade')[:5]
    
    # Tendências (comparar com semana passada)
    semana_passada = hoje - timedelta(days=7)
    try:
        snapshot_anterior = KPISnapshot.objects.get(data_snapshot=semana_passada)
        tendencias = {
            'equipamentos': calcular_tendencia(
                snapshot.total_equipamentos, 
                snapshot_anterior.total_equipamentos
            ),
            'checklists': calcular_tendencia(
                snapshot.checklists_concluidos, 
                snapshot_anterior.checklists_concluidos
            ),
            'alertas': calcular_tendencia(
                snapshot.alertas_ativos, 
                snapshot_anterior.alertas_ativos
            ),
        }
    except KPISnapshot.DoesNotExist:
        tendencias = {'equipamentos': 0, 'checklists': 0, 'alertas': 0}
    
    return {
        'kpis': {
            'total_equipamentos': snapshot.total_equipamentos,
            'equipamentos_operacionais': snapshot.equipamentos_operacionais,
            'equipamentos_manutencao': snapshot.equipamentos_manutencao,
            'equipamentos_nr12_ativos': snapshot.equipamentos_nr12_ativos,
            'checklists_pendentes': snapshot.checklists_pendentes,
            'checklists_concluidos': snapshot.checklists_concluidos,
            'checklists_com_problemas': snapshot.checklists_com_problemas,
            'alertas_criticos': snapshot.alertas_criticos,
            'alertas_ativos': snapshot.alertas_ativos,
            'contas_vencidas': float(snapshot.contas_vencidas),
            'contas_a_vencer': float(snapshot.contas_a_vencer),
            'faturamento_mes': float(snapshot.faturamento_mes),
        },
        'tendencias': tendencias,
        'alertas': [
            {
                'tipo': alerta.tipo,
                'titulo': alerta.titulo,
                'descricao': alerta.descricao,
                'prioridade': alerta.prioridade,
                'cor': alerta.cor_prioridade,
                'icone': alerta.icone,
                'link': alerta.link_acao,
            }
            for alerta in alertas
        ],
        'data_atualizacao': snapshot.calculado_em.isoformat(),
    }


def calcular_tendencia(valor_atual, valor_anterior):
    """Calcula tendência percentual entre dois valores"""
    if valor_anterior == 0:
        return 100 if valor_atual > 0 else 0
    
    return round(((valor_atual - valor_anterior) / valor_anterior) * 100, 1)


def criar_alertas_automaticos():
    """Cria alertas automáticos baseado no estado atual do sistema"""
    hoje = date.today()
    
    # Limpar alertas automáticos antigos
    AlertaDashboard.objects.filter(
        tipo='SISTEMA',
        exibir_ate__lt=timezone.now()
    ).delete()
    
    try:
        # Alerta de checklists pendentes
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        pendentes = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).count()
        
        if pendentes > 10:
            AlertaDashboard.criar_alerta_automatico(
                tipo='CHECKLIST',
                titulo=f"{pendentes} checklists pendentes hoje",
                descricao=f"Existem {pendentes} checklists NR12 pendentes para hoje. Verifique se todos os equipamentos foram inspecionados.",
                prioridade='ALTA',
                link_acao='/admin/nr12_checklist/checklistnr12/?status=PENDENTE'
            )
        
        # Alerta de manutenções vencidas
        from backend.apps.equipamentos.models import Equipamento
        
        vencidas = Equipamento.objects.filter(
            ativo=True,
            proxima_manutencao_preventiva__lt=hoje
        ).count()
        
        if vencidas > 0:
            AlertaDashboard.criar_alerta_automatico(
                tipo='MANUTENCAO',
                titulo=f"{vencidas} equipamentos com manutenção vencida",
                descricao=f"{vencidas} equipamentos estão com manutenção preventiva vencida. Agende as manutenções urgentemente.",
                prioridade='CRITICA',
                link_acao='/admin/equipamentos/equipamento/'
            )
        
        # Alerta de estoque baixo
        from backend.apps.almoxarifado.models import Produto
        
        estoque_baixo = Produto.objects.filter(estoque_atual__lt=5).count()
        
        if estoque_baixo > 0:
            AlertaDashboard.criar_alerta_automatico(
                tipo='ESTOQUE',
                titulo=f"{estoque_baixo} produtos com estoque baixo",
                descricao=f"{estoque_baixo} produtos estão com estoque abaixo de 5 unidades. Considere fazer pedidos de reposição.",
                prioridade='MEDIA',
                link_acao='/admin/almoxarifado/produto/'
            )
        
        # Alerta de contas vencidas
        from backend.apps.financeiro.models import ContaFinanceira
        
        contas_vencidas = ContaFinanceira.objects.filter(
            status='VENCIDO'
        ).count()
        
        if contas_vencidas > 0:
            AlertaDashboard.criar_alerta_automatico(
                tipo='FINANCEIRO',
                titulo=f"{contas_vencidas} contas vencidas",
                descricao=f"Existem {contas_vencidas} contas financeiras vencidas que precisam de atenção.",
                prioridade='ALTA',
                link_acao='/admin/financeiro/contafinanceira/?status=VENCIDO'
            )
        
    except Exception as e:
        print(f"Erro ao criar alertas automáticos: {e}")
    
    print("✅ Alertas automáticos verificados e atualizados")