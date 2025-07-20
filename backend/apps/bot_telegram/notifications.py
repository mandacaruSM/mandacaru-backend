# ================================================================
# ARQUIVO: backend/apps/bot_telegram/notifications.py
# Sistema de notificações via Telegram
# ================================================================

import logging
from django.conf import settings
from datetime import date, timedelta
from celery import shared_task

logger = logging.getLogger(__name__)

def enviar_notificacao_checklist(checklist):
    """
    Envia notificação sobre checklist pendente
    """
    try:
        # Aqui você implementaria o envio via API do Telegram
        # Por enquanto, apenas loggar
        logger.info(f"📋 Notificação: Checklist {checklist.uuid} pendente para {checklist.equipamento.nome}")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar notificação de checklist: {e}")
        return False

@shared_task
def notificar_checklists_atrasados():
    """
    Task para notificar checklists atrasados
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        hoje = date.today()
        checklists_atrasados = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).select_related('equipamento', 'equipamento__cliente')
        
        notificados = 0
        for checklist in checklists_atrasados:
            if enviar_notificacao_checklist(checklist):
                notificados += 1
        
        logger.info(f"✅ {notificados} notificações de checklist enviadas")
        return f"Notificações enviadas: {notificados}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar checklists atrasados: {e}")
        raise

@shared_task
def enviar_resumo_diario_task():
    """
    Task para enviar resumo diário
    """
    try:
        from backend.apps.dashboard.models import obter_resumo_dashboard
        
        resumo = obter_resumo_dashboard()
        
        # Preparar mensagem
        mensagem = f"""
📊 RESUMO DIÁRIO - {date.today().strftime('%d/%m/%Y')}

🔧 Equipamentos: {resumo['kpis']['total_equipamentos']} total
📋 Checklists: {resumo['kpis']['checklists_pendentes']} pendentes
🚨 Alertas: {resumo['kpis']['alertas_criticos']} críticos
💰 Faturamento mês: R$ {resumo['kpis']['faturamento_mes']:,.2f}
        """
        
        # Aqui você enviaria via API do Telegram
        logger.info(f"📊 Resumo diário preparado: {mensagem}")
        
        return "Resumo diário enviado"
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar resumo diário: {e}")
        raise