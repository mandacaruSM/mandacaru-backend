# ================================================================
# ARQUIVO: backend/apps/bot_telegram/notifications.py
# Sistema de Notificações via Telegram
# ================================================================

import requests
import logging
from django.conf import settings
from datetime import date, datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Classe para envio de notificações via Telegram"""
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def enviar_mensagem(self, chat_id: str, texto: str, parse_mode: str = 'HTML') -> bool:
        """Envia mensagem para um chat específico"""
        if not self.bot_token:
            logger.warning("Token do Telegram não configurado")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': texto,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Mensagem enviada para {chat_id}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no envio: {e}")
            return False
    
    def enviar_para_multiplos(self, chat_ids: List[str], texto: str) -> Dict[str, bool]:
        """Envia mensagem para múltiplos chats"""
        resultados = {}
        
        for chat_id in chat_ids:
            resultados[chat_id] = self.enviar_mensagem(chat_id, texto)
        
        return resultados
    
    def formatar_checklist_pendente(self, checklist) -> str:
        """Formata mensagem para checklist pendente"""
        return f"""
🔔 <b>CHECKLIST PENDENTE</b>

📋 <b>Equipamento:</b> {checklist.equipamento.nome}
🏢 <b>Cliente:</b> {checklist.equipamento.cliente.razao_social}
📅 <b>Data:</b> {checklist.data_checklist.strftime('%d/%m/%Y')}
🌅 <b>Turno:</b> {checklist.get_turno_display()}

⏰ <b>Status:</b> Aguardando execução

🔗 <b>Link:</b> /checklist_{checklist.uuid}

⚠️ <i>Clique no link acima para executar o checklist</i>
        """.strip()
    
    def formatar_alerta_manutencao(self, alerta) -> str:
        """Formata mensagem para alerta de manutenção"""
        dias_restantes = (alerta.data_prevista - date.today()).days
        
        if dias_restantes < 0:
            status_emoji = "🔴"
            status_texto = f"VENCIDA há {abs(dias_restantes)} dia(s)"
        elif dias_restantes == 0:
            status_emoji = "🟠"
            status_texto = "VENCE HOJE"
        elif dias_restantes <= 3:
            status_emoji = "🟡"
            status_texto = f"Vence em {dias_restantes} dia(s)"
        else:
            status_emoji = "🟢"
            status_texto = f"Prevista para {dias_restantes} dia(s)"
        
        return f"""
{status_emoji} <b>ALERTA DE MANUTENÇÃO</b>

🔧 <b>Equipamento:</b> {alerta.equipamento.nome}
🏢 <b>Cliente:</b> {alerta.equipamento.cliente.razao_social}
📋 <b>Tipo:</b> {alerta.get_tipo_display()}
⚡ <b>Criticidade:</b> {alerta.get_criticidade_display()}

📅 <b>Data Prevista:</b> {alerta.data_prevista.strftime('%d/%m/%Y')}
⏰ <b>Status:</b> {status_texto}

📝 <b>Descrição:</b>
{alerta.descricao}

🔗 <b>Gerenciar:</b> /alerta_{alerta.id}
        """.strip()
    
    def formatar_resumo_diario(self, dados_resumo: Dict) -> str:
        """Formata mensagem de resumo diário"""
        hoje = date.today().strftime('%d/%m/%Y')
        
        return f"""
📊 <b>RESUMO DIÁRIO - {hoje}</b>

🔧 <b>EQUIPAMENTOS</b>
• Total: {dados_resumo.get('total_equipamentos', 0)}
• Operacionais: {dados_resumo.get('equipamentos_operacionais', 0)}
• Em manutenção: {dados_resumo.get('equipamentos_manutencao', 0)}

📋 <b>CHECKLISTS NR12</b>
• Pendentes: {dados_resumo.get('checklists_pendentes', 0)}
• Concluídos: {dados_resumo.get('checklists_concluidos', 0)}
• Com problemas: {dados_resumo.get('checklists_problemas', 0)}

🚨 <b>ALERTAS</b>
• Críticos: {dados_resumo.get('alertas_criticos', 0)}
• Ativos: {dados_resumo.get('alertas_ativos', 0)}

💰 <b>FINANCEIRO</b>
• Contas vencidas: R$ {dados_resumo.get('contas_vencidas', 0):,.2f}
• A vencer (7 dias): R$ {dados_resumo.get('contas_a_vencer', 0):,.2f}

📦 <b>ESTOQUE</b>
• Produtos baixo: {dados_resumo.get('produtos_estoque_baixo', 0)}

⏰ <i>Atualizado às {datetime.now().strftime('%H:%M')}</i>
        """.strip()
    
    def formatar_checklist_concluido(self, checklist) -> str:
        """Formata mensagem para checklist concluído"""
        status_emoji = "✅" if not checklist.necessita_manutencao else "⚠️"
        status_texto = "Aprovado" if not checklist.necessita_manutencao else "Com problemas"
        
        total_itens = checklist.itens.count()
        itens_ok = checklist.itens.filter(status='OK').count()
        itens_nok = checklist.itens.filter(status='NOK').count()
        
        return f"""
{status_emoji} <b>CHECKLIST CONCLUÍDO</b>

📋 <b>Equipamento:</b> {checklist.equipamento.nome}
🏢 <b>Cliente:</b> {checklist.equipamento.cliente.razao_social}
📅 <b>Data:</b> {checklist.data_checklist.strftime('%d/%m/%Y')}
🌅 <b>Turno:</b> {checklist.get_turno_display()}

📊 <b>Resultados:</b>
• Total de itens: {total_itens}
• Conformes (OK): {itens_ok}
• Não conformes (NOK): {itens_nok}
• Não aplicáveis: {checklist.itens.filter(status='NA').count()}

🎯 <b>Status:</b> {status_texto}
👤 <b>Responsável:</b> {checklist.responsavel.first_name if checklist.responsavel else 'Sistema'}

{f'⚠️ <b>Ação necessária:</b> Equipamento necessita manutenção' if checklist.necessita_manutencao else ''}
        """.strip()


# ================================================================
# FUNÇÕES DE NOTIFICAÇÃO ESPECÍFICAS
# ================================================================

def enviar_notificacao_checklist(checklist):
    """Envia notificação de checklist pendente"""
    try:
        from backend.apps.auth_cliente.models import UsuarioCliente
        
        notifier = TelegramNotifier()
        
        # Buscar usuários do cliente com Telegram configurado
        usuarios_cliente = UsuarioCliente.objects.filter(
            cliente=checklist.equipamento.cliente,
            telegram_chat_id__isnull=False,
            ativo=True
        )
        
        if not usuarios_cliente.exists():
            logger.info(f"Nenhum usuário com Telegram para cliente {checklist.equipamento.cliente.razao_social}")
            return
        
        mensagem = notifier.formatar_checklist_pendente(checklist)
        chat_ids = [user.telegram_chat_id for user in usuarios_cliente]
        
        resultados = notifier.enviar_para_multiplos(chat_ids, mensagem)
        
        enviados = sum(1 for sucesso in resultados.values() if sucesso)
        logger.info(f"✅ Notificação de checklist enviada para {enviados}/{len(chat_ids)} usuários")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar checklist: {e}")
        return {}

def enviar_notificacao_alerta_manutencao(alerta):
    """Envia notificação de alerta de manutenção"""
    try:
        from backend.apps.auth_cliente.models import UsuarioCliente
        
        notifier = TelegramNotifier()
        
        # Buscar usuários do cliente + administradores
        usuarios_notificar = UsuarioCliente.objects.filter(
            Q(cliente=alerta.equipamento.cliente) | Q(is_staff=True),
            telegram_chat_id__isnull=False,
            ativo=True
        ).distinct()
        
        if not usuarios_notificar.exists():
            logger.info(f"Nenhum usuário com Telegram para alerta {alerta.id}")
            return
        
        mensagem = notifier.formatar_alerta_manutencao(alerta)
        chat_ids = [user.telegram_chat_id for user in usuarios_notificar]
        
        resultados = notifier.enviar_para_multiplos(chat_ids, mensagem)
        
        # Marcar alerta como notificado
        if any(resultados.values()):
            alerta.marcar_como_notificado()
        
        enviados = sum(1 for sucesso in resultados.values() if sucesso)
        logger.info(f"✅ Notificação de alerta enviada para {enviados}/{len(chat_ids)} usuários")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar alerta: {e}")
        return {}

def enviar_resumo_diario():
    """Envia resumo diário para administradores"""
    try:
        from backend.apps.auth_cliente.models import UsuarioCliente
        from backend.apps.dashboard.models import obter_resumo_dashboard
        
        notifier = TelegramNotifier()
        
        # Buscar administradores com Telegram
        admins = UsuarioCliente.objects.filter(
            is_staff=True,
            telegram_chat_id__isnull=False,
            ativo=True
        )
        
        if not admins.exists():
            logger.info("Nenhum administrador com Telegram configurado")
            return
        
        # Obter dados do dashboard
        resumo = obter_resumo_dashboard()
        mensagem = notifier.formatar_resumo_diario(resumo['kpis'])
        
        chat_ids = [admin.telegram_chat_id for admin in admins]
        resultados = notifier.enviar_para_multiplos(chat_ids, mensagem)
        
        enviados = sum(1 for sucesso in resultados.values() if sucesso)
        logger.info(f"✅ Resumo diário enviado para {enviados}/{len(chat_ids)} administradores")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar resumo diário: {e}")
        return {}

def notificar_checklist_concluido(checklist):
    """Notifica quando checklist é concluído"""
    try:
        from backend.apps.auth_cliente.models import UsuarioCliente
        
        # Só notificar se houver problemas ou for solicitado
        if not checklist.necessita_manutencao:
            return
        
        notifier = TelegramNotifier()
        
        # Notificar cliente e administradores
        usuarios_notificar = UsuarioCliente.objects.filter(
            Q(cliente=checklist.equipamento.cliente) | Q(is_staff=True),
            telegram_chat_id__isnull=False,
            ativo=True
        ).distinct()
        
        if not usuarios_notificar.exists():
            return
        
        mensagem = notifier.formatar_checklist_concluido(checklist)
        chat_ids = [user.telegram_chat_id for user in usuarios_notificar]
        
        resultados = notifier.enviar_para_multiplos(chat_ids, mensagem)
        
        enviados = sum(1 for sucesso in resultados.values() if sucesso)
        logger.info(f"✅ Notificação de checklist concluído enviada para {enviados} usuários")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar checklist concluído: {e}")
        return {}

def enviar_notificacao_personalizada(titulo: str, mensagem: str, destinatarios: List[str] = None):
    """Envia notificação personalizada"""
    try:
        from backend.apps.auth_cliente.models import UsuarioCliente
        
        notifier = TelegramNotifier()
        
        if destinatarios:
            # Usar destinatários específicos
            chat_ids = destinatarios
        else:
            # Enviar para todos os administradores
            admins = UsuarioCliente.objects.filter(
                is_staff=True,
                telegram_chat_id__isnull=False,
                ativo=True
            )
            chat_ids = [admin.telegram_chat_id for admin in admins]
        
        if not chat_ids:
            logger.info("Nenhum destinatário com Telegram configurado")
            return
        
        # Formatar mensagem
        texto_formatado = f"""
🔔 <b>{titulo}</b>

{mensagem}

⏰ <i>{datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>
        """.strip()
        
        resultados = notifier.enviar_para_multiplos(chat_ids, texto_formatado)
        
        enviados = sum(1 for sucesso in resultados.values() if sucesso)
        logger.info(f"✅ Notificação personalizada '{titulo}' enviada para {enviados} usuários")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificação personalizada: {e}")
        return {}


# ================================================================
# TASKS CELERY PARA NOTIFICAÇÕES
# ================================================================

from celery import shared_task
from django.db.models import Q

@shared_task
def notificar_checklists_atrasados():
    """Task para notificar checklists atrasados"""
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from datetime import timedelta
        from django.utils import timezone
        
        # Checklists pendentes há mais de 2 horas
        limite = timezone.now() - timedelta(hours=2)
        atrasados = ChecklistNR12.objects.filter(
            status='PENDENTE',
            data_checklist=date.today(),
            created_at__lt=limite
        ).select_related('equipamento', 'equipamento__cliente')
        
        notificacoes_enviadas = 0
        
        for checklist in atrasados:
            resultado = enviar_notificacao_checklist(checklist)
            if any(resultado.values()):
                notificacoes_enviadas += 1
        
        logger.info(f"✅ {notificacoes_enviadas} notificações de atraso enviadas")
        return f"Notificações enviadas: {notificacoes_enviadas}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar atrasos: {e}")
        raise

@shared_task
def notificar_alertas_urgentes():
    """Task para notificar alertas urgentes"""
    try:
        from backend.apps.nr12_checklist.models import AlertaManutencao
        
        # Alertas críticos não notificados
        alertas_urgentes = AlertaManutencao.objects.filter(
            status='ATIVO',
            criticidade__in=['ALTA', 'CRITICA'],
            data_prevista__lte=date.today() + timedelta(days=3)
        )
        
        notificacoes_enviadas = 0
        
        for alerta in alertas_urgentes:
            resultado = enviar_notificacao_alerta_manutencao(alerta)
            if any(resultado.values()):
                notificacoes_enviadas += 1
        
        logger.info(f"✅ {notificacoes_enviadas} notificações de alerta enviadas")
        return f"Alertas notificados: {notificacoes_enviadas}"
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar alertas: {e}")
        raise

@shared_task
def enviar_resumo_diario_task():
    """Task para enviar resumo diário"""
    try:
        resultado = enviar_resumo_diario()
        enviados = sum(1 for sucesso in resultado.values() if sucesso)
        return f"Resumo enviado para {enviados} administradores"
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar resumo: {e}")
        raise

@shared_task
def notificar_backup_concluido():
    """Task para notificar quando backup é concluído"""
    try:
        titulo = "✅ Backup Concluído"
        mensagem = f"""
O backup automático do sistema foi concluído com sucesso.

📅 Data: {date.today().strftime('%d/%m/%Y')}
⏰ Horário: {datetime.now().strftime('%H:%M')}

Todos os dados importantes foram salvos com segurança.
        """.strip()
        
        resultado = enviar_notificacao_personalizada(titulo, mensagem)
        enviados = sum(1 for sucesso in resultado.values() if sucesso)
        
        return f"Notificação de backup enviada para {enviados} administradores"
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar backup: {e}")
        raise


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def verificar_configuracao_telegram():
    """Verifica se o Telegram está configurado corretamente"""
    try:
        from django.conf import settings
        
        if not getattr(settings, 'TELEGRAM_BOT_TOKEN', ''):
            return False, "Token do bot não configurado"
        
        # Testar conexão com API
        notifier = TelegramNotifier()
        url = f"{notifier.base_url}/getMe"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['username']
                return True, f"Bot @{bot_name} configurado corretamente"
            else:
                return False, "Token inválido"
        else:
            return False, f"Erro na API: {response.status_code}"
            
    except Exception as e:
        return False, f"Erro ao verificar: {e}"

def obter_estatisticas_notificacoes():
    """Obtém estatísticas das notificações"""
    try:
        from backend.apps.auth_cliente.models import UsuarioCliente
        
        # Usuários com Telegram configurado
        usuarios_telegram = UsuarioCliente.objects.filter(
            telegram_chat_id__isnull=False,
            ativo=True
        )
        
        clientes_com_telegram = usuarios_telegram.filter(
            cliente__isnull=False
        ).count()
        
        admins_com_telegram = usuarios_telegram.filter(
            is_staff=True
        ).count()
        
        return {
            'total_usuarios_telegram': usuarios_telegram.count(),
            'clientes_com_telegram': clientes_com_telegram,
            'admins_com_telegram': admins_com_telegram,
            'configuracao_ok': verificar_configuracao_telegram()[0]
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        return {}

def testar_notificacao(chat_id: str, mensagem: str = None):
    """Testa envio de notificação para um chat"""
    if not mensagem:
        mensagem = f"""
🧪 <b>TESTE DE NOTIFICAÇÃO</b>

Este é um teste do sistema de notificações do Mandacaru ERP.

📅 Data: {date.today().strftime('%d/%m/%Y')}
⏰ Horário: {datetime.now().strftime('%H:%M:%S')}

Se você recebeu esta mensagem, o sistema está funcionando corretamente! ✅
        """.strip()
    
    notifier = TelegramNotifier()
    resultado = notifier.enviar_mensagem(chat_id, mensagem)
    
    return resultado