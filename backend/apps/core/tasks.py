# ================================================================
# ARQUIVO: backend/apps/core/tasks.py
# Sistema de Automação Principal do Mandacaru ERP
# ================================================================

from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.db.models import Count, Sum, Q
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ================================================================
# TASKS DE CHECKLISTS NR12
# ================================================================

@shared_task
def gerar_checklists_diarios():
    """Gera checklists NR12 diários para todos os equipamentos ativos"""
    try:
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import ChecklistNR12
        import uuid
        
        hoje = date.today()
        equipamentos_ativos = Equipamento.objects.filter(
            ativo_nr12=True,
            tipo_nr12__isnull=False
        )
        
        checklists_criados = 0
        turnos = ['MANHA', 'TARDE', 'NOITE']
        
        for equipamento in equipamentos_ativos:
            # Verificar frequência
            if equipamento.frequencia_checklist == 'DIARIO':
                for turno in turnos:
                    # Verificar se já existe
                    if not ChecklistNR12.objects.filter(
                        equipamento=equipamento,
                        data_checklist=hoje,
                        turno=turno
                    ).exists():
                        ChecklistNR12.objects.create(
                            equipamento=equipamento,
                            data_checklist=hoje,
                            turno=turno,
                            status='PENDENTE',
                            uuid=uuid.uuid4()
                        )
                        checklists_criados += 1
        
        logger.info(f"✅ {checklists_criados} checklists criados para {hoje}")
        return f"Checklists criados: {checklists_criados}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar checklists: {e}")
        raise

@shared_task
def verificar_checklists_pendentes():
    """Verifica checklists pendentes e envia notificações"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        hoje = date.today()
        agora = timezone.now()
        
        # Checklists pendentes há mais de 2 horas
        checklists_atrasados = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE',
            created_at__lt=agora - timedelta(hours=2)
        ).select_related('equipamento', 'equipamento__cliente')
        
        if checklists_atrasados.exists():
            # Agrupar por cliente
            por_cliente = {}
            for checklist in checklists_atrasados:
                cliente = checklist.equipamento.cliente.razao_social
                if cliente not in por_cliente:
                    por_cliente[cliente] = []
                por_cliente[cliente].append(checklist)
            
            # Enviar notificações (implementar depois)
            total_atrasados = checklists_atrasados.count()
            logger.warning(f"⚠️ {total_atrasados} checklists atrasados encontrados")
            
            return f"Checklists atrasados: {total_atrasados}"
        
        return "Nenhum checklist atrasado"
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar checklists: {e}")
        raise

# ================================================================
# TASKS DE MANUTENÇÃO
# ================================================================

@shared_task
def verificar_alertas_manutencao():
    """Verifica e cria alertas de manutenção preventiva"""
    try:
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import AlertaManutencao
        
        hoje = date.today()
        alertas_criados = 0
        
        # Equipamentos com manutenção vencida ou próxima
        equipamentos = Equipamento.objects.filter(
            ativo=True,
            proxima_manutencao_preventiva__lte=hoje + timedelta(days=7)
        )
        
        for equipamento in equipamentos:
            dias_restantes = (equipamento.proxima_manutencao_preventiva - hoje).days
            
            # Determinar criticidade baseada nos dias restantes
            if dias_restantes < 0:
                criticidade = 'CRITICA'
                titulo = f"Manutenção VENCIDA - {equipamento.nome}"
            elif dias_restantes <= 3:
                criticidade = 'ALTA'
                titulo = f"Manutenção urgente - {equipamento.nome}"
            else:
                criticidade = 'MEDIA'
                titulo = f"Manutenção próxima - {equipamento.nome}"
            
            # Verificar se já existe alerta ativo
            if not AlertaManutencao.objects.filter(
                equipamento=equipamento,
                tipo='PREVENTIVA',
                status__in=['ATIVO', 'NOTIFICADO'],
                data_prevista=equipamento.proxima_manutencao_preventiva
            ).exists():
                
                AlertaManutencao.objects.create(
                    equipamento=equipamento,
                    tipo='PREVENTIVA',
                    titulo=titulo,
                    descricao=f"Manutenção preventiva programada para {equipamento.proxima_manutencao_preventiva}. Dias restantes: {dias_restantes}",
                    criticidade=criticidade,
                    data_prevista=equipamento.proxima_manutencao_preventiva
                )
                alertas_criados += 1
        
        logger.info(f"✅ {alertas_criados} alertas de manutenção criados")
        return f"Alertas criados: {alertas_criados}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar manutenções: {e}")
        raise

# ================================================================
# TASKS FINANCEIRAS
# ================================================================

@shared_task
def verificar_contas_vencidas():
    """Verifica contas vencidas e próximas ao vencimento"""
    try:
        from backend.apps.financeiro.models import ContaFinanceira
        
        hoje = date.today()
        
        # Contas vencidas
        vencidas = ContaFinanceira.objects.filter(
            status='PENDENTE',
            data_vencimento__lt=hoje
        ).update(status='VENCIDO')
        
        # Contas próximas ao vencimento (próximos 7 dias)
        proximas = ContaFinanceira.objects.filter(
            status='PENDENTE',
            data_vencimento__range=[hoje, hoje + timedelta(days=7)]
        ).count()
        
        logger.info(f"✅ {vencidas} contas marcadas como vencidas, {proximas} próximas ao vencimento")
        return f"Vencidas: {vencidas}, Próximas: {proximas}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar contas: {e}")
        raise

@shared_task
def calcular_metricas_financeiras():
    """Calcula métricas financeiras do mês"""
    try:
        from backend.apps.financeiro.models import ContaFinanceira
        from backend.apps.dashboard.models import KPISnapshot
        
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        
        # Faturamento do mês
        faturamento = ContaFinanceira.objects.filter(
            tipo='RECEBER',
            status='PAGO',
            data_pagamento__range=[inicio_mes, hoje]
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        
        # Despesas do mês
        despesas = ContaFinanceira.objects.filter(
            tipo='PAGAR',
            status='PAGO',
            data_pagamento__range=[inicio_mes, hoje]
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        
        # Contas a receber em aberto
        a_receber = ContaFinanceira.objects.filter(
            tipo='RECEBER',
            status__in=['PENDENTE', 'VENCIDO']
        ).aggregate(total=Sum('valor_restante'))['total'] or 0
        
        # Contas a pagar em aberto
        a_pagar = ContaFinanceira.objects.filter(
            tipo='PAGAR',
            status__in=['PENDENTE', 'VENCIDO']
        ).aggregate(total=Sum('valor_restante'))['total'] or 0
        
        # Atualizar KPI snapshot
        snapshot, created = KPISnapshot.objects.get_or_create(
            data_snapshot=hoje,
            defaults={
                'faturamento_mes': faturamento,
                'contas_a_receber': a_receber,
                'contas_a_pagar': a_pagar
            }
        )
        
        if not created:
            snapshot.faturamento_mes = faturamento
            snapshot.contas_a_receber = a_receber
            snapshot.contas_a_pagar = a_pagar
            snapshot.save()
        
        logger.info(f"✅ Métricas financeiras calculadas - Faturamento: R$ {faturamento}")
        return f"Faturamento: R$ {faturamento:.2f}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao calcular métricas financeiras: {e}")
        raise

# ================================================================
# TASKS DE ESTOQUE
# ================================================================

@shared_task
def verificar_estoque_baixo():
    """Verifica produtos com estoque baixo"""
    try:
        from backend.apps.almoxarifado.models import Produto
        from backend.apps.dashboard.models import AlertaDashboard
        
        produtos_baixo = Produto.objects.filter(estoque_atual__lt=5)
        
        if produtos_baixo.exists():
            count = produtos_baixo.count()
            
            # Criar alerta no dashboard
            AlertaDashboard.objects.get_or_create(
                tipo='ESTOQUE',
                titulo=f"{count} produtos com estoque baixo",
                defaults={
                    'descricao': f"Existem {count} produtos com estoque abaixo de 5 unidades. Verifique e faça pedidos de reposição.",
                    'prioridade': 'MEDIA',
                    'ativo': True,
                    'icone': '📦',
                    'link_acao': '/admin/almoxarifado/produto/?estoque_atual__lt=5'
                }
            )
            
            logger.warning(f"⚠️ {count} produtos com estoque baixo")
            return f"Produtos com estoque baixo: {count}"
        
        return "Estoque normal"
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar estoque: {e}")
        raise

# ================================================================
# TASKS DE BACKUP E LIMPEZA
# ================================================================

@shared_task
def backup_dados_importantes():
    """Backup dos dados mais importantes do sistema"""
    try:
        from django.core import serializers
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import ChecklistNR12, TipoEquipamentoNR12
        from backend.apps.clientes.models import Cliente
        import json
        import os
        
        hoje = date.today()
        timestamp = hoje.strftime('%Y%m%d')
        backup_dir = f"backups/{timestamp}"
        
        # Criar diretório se não existir
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup de equipamentos
        equipamentos = serializers.serialize('json', Equipamento.objects.all())
        with open(f"{backup_dir}/equipamentos.json", 'w') as f:
            f.write(equipamentos)
        
        # Backup de clientes
        clientes = serializers.serialize('json', Cliente.objects.all())
        with open(f"{backup_dir}/clientes.json", 'w') as f:
            f.write(clientes)
        
        # Backup de tipos NR12
        tipos_nr12 = serializers.serialize('json', TipoEquipamentoNR12.objects.all())
        with open(f"{backup_dir}/tipos_nr12.json", 'w') as f:
            f.write(tipos_nr12)
        
        # Backup de checklists dos últimos 30 dias
        data_limite = hoje - timedelta(days=30)
        checklists = serializers.serialize(
            'json', 
            ChecklistNR12.objects.filter(data_checklist__gte=data_limite)
        )
        with open(f"{backup_dir}/checklists_recentes.json", 'w') as f:
            f.write(checklists)
        
        logger.info(f"✅ Backup realizado em {backup_dir}")
        return f"Backup realizado: {backup_dir}"
        
    except Exception as e:
        logger.error(f"❌ Erro no backup: {e}")
        raise

@shared_task
def limpeza_dados_antigos():
    """Remove dados antigos desnecessários"""
    try:
        from backend.apps.dashboard.models import AlertaDashboard, KPISnapshot
        
        # Remover alertas inativos antigos (30 dias)
        data_corte_alertas = timezone.now() - timedelta(days=30)
        alertas_removidos = AlertaDashboard.objects.filter(
            ativo=False,
            criado_em__lt=data_corte_alertas
        ).delete()[0]
        
        # Manter apenas KPIs dos últimos 180 dias
        data_corte_kpis = date.today() - timedelta(days=180)
        kpis_removidos = KPISnapshot.objects.filter(
            data_snapshot__lt=data_corte_kpis
        ).delete()[0]
        
        logger.info(f"✅ Limpeza concluída - Alertas: {alertas_removidos}, KPIs: {kpis_removidos}")
        return f"Removidos: {alertas_removidos} alertas, {kpis_removidos} KPIs"
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        raise

# ================================================================
# TASKS DE NOTIFICAÇÕES
# ================================================================

@shared_task
def enviar_relatorio_diario():
    """Envia relatório diário por email"""
    try:
        from backend.apps.dashboard.models import obter_resumo_dashboard
        
        hoje = date.today()
        resumo = obter_resumo_dashboard()
        
        # Preparar conteúdo do email
        assunto = f"Relatório Diário Mandacaru ERP - {hoje.strftime('%d/%m/%Y')}"
        
        corpo = f"""
        📊 RELATÓRIO DIÁRIO - {hoje.strftime('%d/%m/%Y')}
        ================================================
        
        🔧 EQUIPAMENTOS:
        • Total: {resumo['kpis']['total_equipamentos']}
        • Operacionais: {resumo['kpis']['equipamentos_operacionais']}
        • Em manutenção: {resumo['kpis']['equipamentos_manutencao']}
        • NR12 ativos: {resumo['kpis']['equipamentos_nr12_ativos']}
        
        📋 CHECKLISTS NR12:
        • Pendentes: {resumo['kpis']['checklists_pendentes']}
        • Concluídos: {resumo['kpis']['checklists_concluidos']}
        • Com problemas: {resumo['kpis']['checklists_com_problemas']}
        
        🚨 ALERTAS:
        • Críticos: {resumo['kpis']['alertas_criticos']}
        • Ativos: {resumo['kpis']['alertas_ativos']}
        
        💰 FINANCEIRO:
        • Contas vencidas: R$ {resumo['kpis']['contas_vencidas']:,.2f}
        • A vencer: R$ {resumo['kpis']['contas_a_vencer']:,.2f}
        • Faturamento mês: R$ {resumo['kpis']['faturamento_mes']:,.2f}
        
        --
        Sistema Mandacaru ERP
        """
        
        # Enviar email (configurar destinatários no settings)
        destinatarios = getattr(settings, 'RELATORIO_EMAIL_DESTINATARIOS', [])
        if destinatarios:
            send_mail(
                assunto,
                corpo,
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
                fail_silently=False,
            )
            logger.info(f"✅ Relatório enviado para {len(destinatarios)} destinatários")
        
        return f"Relatório enviado para {len(destinatarios)} destinatários"
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar relatório: {e}")
        raise

# ================================================================
# TASK PRINCIPAL DE MONITORAMENTO
# ================================================================

@shared_task
def monitoramento_sistema():
    """Task principal que monitora a saúde do sistema"""
    try:
        import psutil
        from django.db import connection
        
        # Verificar uso de CPU e memória
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Verificar conexão com banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_ok = True
        
        # Log da saúde do sistema
        logger.info(f"🖥️ Sistema - CPU: {cpu_percent}%, RAM: {memory.percent}%, DB: {'✅' if db_ok else '❌'}")
        
        # Alertar se recursos críticos
        if cpu_percent > 90 or memory.percent > 90:
            logger.warning(f"⚠️ Recursos do sistema em nível crítico!")
        
        return f"CPU: {cpu_percent}%, RAM: {memory.percent}%"
        
    except Exception as e:
        logger.error(f"❌ Erro no monitoramento: {e}")
        return f"Erro: {str(e)}"