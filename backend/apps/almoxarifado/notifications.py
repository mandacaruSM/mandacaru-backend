# ----------------------------------------------------------------
# 10. NOTIFICAÇÕES E ALERTAS
# backend/apps/almoxarifado/notifications.py
# ----------------------------------------------------------------

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from backend.apps.almoxarifado.models import EstoqueCombustivel
from backend.apps.abastecimento.models import RegistroAbastecimento
import logging

logger = logging.getLogger(__name__)

class NotificacaoEstoque:
    """Sistema de notificações para controle de estoque"""
    
    @staticmethod
    def enviar_alerta_estoque_baixo(estoque_combustivel, abastecimento=None):
        """Envia alerta quando estoque fica baixo"""
        try:
            assunto = f"🚨 ESTOQUE BAIXO: {estoque_combustivel.tipo_combustivel.nome}"
            
            contexto = {
                'estoque': estoque_combustivel,
                'abastecimento': abastecimento,
                'empresa': getattr(settings, 'EMPRESA_NOME', 'Mandacaru ERP'),
            }
            
            # Render do template de email
            mensagem_html = render_to_string(
                'almoxarifado/emails/estoque_baixo.html', 
                contexto
            )
            mensagem_texto = render_to_string(
                'almoxarifado/emails/estoque_baixo.txt', 
                contexto
            )
            
            # Lista de destinatários
            destinatarios = NotificacaoEstoque._get_destinatarios_almoxarifado()
            
            if destinatarios:
                send_mail(
                    subject=assunto,
                    message=mensagem_texto,
                    html_message=mensagem_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=destinatarios,
                    fail_silently=False
                )
                
                logger.info(f"✅ Alerta de estoque baixo enviado para {len(destinatarios)} destinatários")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar alerta de estoque: {e}")
    
    @staticmethod
    def enviar_relatorio_consumo_diario():
        """Envia relatório diário de consumo"""
        from datetime import date, timedelta
        
        try:
            hoje = date.today()
            ontem = hoje - timedelta(days=1)
            
            # Abastecimentos de ontem
            abastecimentos_ontem = RegistroAbastecimento.objects.filter(
                origem_combustivel='ALMOXARIFADO',
                data_abastecimento__date=ontem
            ).select_related('equipamento', 'tipo_combustivel')
            
            if not abastecimentos_ontem.exists():
                return  # Não enviar se não houve abastecimentos
            
            # Calcular totais
            from django.db.models import Sum, Count
            totais = abastecimentos_ontem.aggregate(
                total_litros=Sum('quantidade_litros'),
                total_valor=Sum('valor_total'),
                total_abastecimentos=Count('id')
            )
            
            contexto = {
                'data': ontem,
                'abastecimentos': abastecimentos_ontem,
                'totais': totais,
                'estoques_baixos': EstoqueCombustivel.objects.filter(
                    ativo=True
                ).select_related('tipo_combustivel'),
                'empresa': getattr(settings, 'EMPRESA_NOME', 'Mandacaru ERP'),
            }
            
            assunto = f"📊 Relatório de Consumo - {ontem.strftime('%d/%m/%Y')}"
            
            mensagem_html = render_to_string(
                'almoxarifado/emails/relatorio_diario.html',
                contexto
            )
            
            destinatarios = NotificacaoEstoque._get_destinatarios_gestores()
            
            if destinatarios:
                send_mail(
                    subject=assunto,
                    message=f"Relatório de consumo de {ontem.strftime('%d/%m/%Y')}",
                    html_message=mensagem_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=destinatarios,
                    fail_silently=False
                )
                
                logger.info(f"✅ Relatório diário enviado para {len(destinatarios)} gestores")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar relatório diário: {e}")
    
    @staticmethod
    def _get_destinatarios_almoxarifado():
        """Retorna lista de emails do pessoal do almoxarifado"""
        # Implementar conforme sua estrutura de usuários
        return getattr(settings, 'EMAILS_ALMOXARIFADO', [
            'almoxarifado@empresa.com',
            'supervisor@empresa.com'
        ])
    
    @staticmethod
    def _get_destinatarios_gestores():
        """Retorna lista de emails dos gestores"""
        return getattr(settings, 'EMAILS_GESTORES', [
            'gerencia@empresa.com',
            'operacoes@empresa.com'
        ])