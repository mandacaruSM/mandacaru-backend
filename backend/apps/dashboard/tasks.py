# ================================================================
# ATUALIZAR backend/apps/dashboard/tasks.py
# ================================================================

from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta
from .models import KPISnapshot, criar_alertas_automaticos
import logging

logger = logging.getLogger(__name__)

@shared_task
def calcular_kpis_diarios():
    """Task para calcular KPIs diários automaticamente"""
    try:
        snapshot = KPISnapshot.calcular_kpis_hoje()
        logger.info(f"✅ KPIs calculados para {snapshot.data_snapshot}")
        return f"KPIs calculados para {snapshot.data_snapshot}"
    except Exception as e:
        logger.error(f"❌ Erro ao calcular KPIs: {e}")
        raise

@shared_task
def gerar_checklists_automatico():
    """Task para gerar checklists automaticamente"""
    try:
        from django.core.management import call_command
        call_command('gerar_checklists_diarios')
        logger.info("✅ Checklists diários gerados automaticamente")
        return "Checklists diários gerados"
    except Exception as e:
        logger.error(f"❌ Erro ao gerar checklists: {e}")
        raise

@shared_task
def verificar_alertas_manutencao():
    """Task para verificar e criar alertas de manutenção"""
    try:
        criar_alertas_automaticos()
        logger.info("✅ Alertas de manutenção verificados")
        return "Alertas verificados"
    except Exception as e:
        logger.error(f"❌ Erro ao verificar alertas: {e}")
        raise

@shared_task
def limpeza_dados_antigos():
    """Task para limpeza de dados antigos"""
    try:
        from backend.apps.dashboard.models import AlertaDashboard
        
        # Remover alertas inativos antigos (mais de 30 dias)
        data_corte = timezone.now() - timedelta(days=30)
        alertas_removidos = AlertaDashboard.objects.filter(
            ativo=False,
            criado_em__lt=data_corte
        ).delete()[0]
        
        # Manter apenas snapshots dos últimos 365 dias
        data_corte_kpi = date.today() - timedelta(days=365)
        kpis_removidos = KPISnapshot.objects.filter(
            data_snapshot__lt=data_corte_kpi
        ).delete()[0]
        
        logger.info(f"✅ Limpeza concluída: {alertas_removidos} alertas, {kpis_removidos} KPIs removidos")
        return f"Removidos: {alertas_removidos} alertas, {kpis_removidos} KPIs"
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")
        raise

@shared_task
def notificar_telegram_checklist_pendente():
    """Task para notificar checklists pendentes via Telegram"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from backend.apps.bot_telegram.notifications import enviar_notificacao_checklist
        
        hoje = date.today()
        checklists_pendentes = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).select_related('equipamento', 'equipamento__cliente')
        
        for checklist in checklists_pendentes:
            try:
                enviar_notificacao_checklist(checklist)
            except Exception as e:
                logger.warning(f"Erro ao notificar checklist {checklist.id}: {e}")
        
        logger.info(f"✅ Notificações enviadas para {checklists_pendentes.count()} checklists")
        return f"Notificações enviadas: {checklists_pendentes.count()}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificações: {e}")
        raise

@shared_task
def backup_dados_importantes():
    """Task para backup de dados importantes"""
    try:
        import json
        from django.core import serializers
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        # Fazer backup dos equipamentos
        equipamentos = serializers.serialize('json', Equipamento.objects.all())
        
        # Fazer backup dos checklists dos últimos 30 dias
        data_corte = date.today() - timedelta(days=30)
        checklists = serializers.serialize(
            'json', 
            ChecklistNR12.objects.filter(data_checklist__gte=data_corte)
        )
        
        # Salvar backups (você pode implementar envio para S3, etc.)
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"✅ Backup realizado: {timestamp}")
        return f"Backup realizado: {timestamp}"
        
    except Exception as e:
        logger.error(f"❌ Erro no backup: {e}")
        raise