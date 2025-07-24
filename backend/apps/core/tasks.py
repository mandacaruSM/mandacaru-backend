# ================================================================
# SISTEMA COMPLETO DE AUTOMAÇÃO DE CHECKLISTS NR12
# backend/apps/core/tasks.py - VERSÃO COMPLETA
# ================================================================

from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
import logging
import uuid

logger = logging.getLogger(__name__)

# ================================================================
# TASK PRINCIPAL - GERAÇÃO AUTOMÁTICA DE CHECKLISTS
# ================================================================

@shared_task
def gerar_checklists_automatico():
    """
    Task principal para gerar checklists automaticamente
    
    HORÁRIOS:
    - Diário: Todo dia às 6h da manhã
    - Semanal: Toda segunda-feira às 6h da manhã  
    - Mensal: Todo dia 1º às 6h da manhã
    
    LÓGICA:
    - Verifica a frequência configurada em cada equipamento
    - Cria checklists para os turnos: MANHA, TARDE, NOITE
    - Evita duplicação verificando se já existe checklist para a data
    """
    try:
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        hoje = date.today()
        dia_semana = hoje.weekday()  # 0=segunda, 6=domingo
        dia_mes = hoje.day
        
        # Log início da execução
        logger.info(f"🚀 Iniciando geração automática de checklists para {hoje}")
        logger.info(f"   Dia da semana: {dia_semana} (0=segunda)")
        logger.info(f"   Dia do mês: {dia_mes}")
        
        # Buscar equipamentos ativos com frequência configurada
        equipamentos_ativos = Equipamento.objects.filter(
            ativo_nr12=True,
            frequencias_checklist__isnull=False
        ).exclude(frequencias_checklist=[]).select_related('categoria', 'cliente', 'tipo_nr12')
        
        if not equipamentos_ativos.exists():
            logger.warning("⚠️ Nenhum equipamento ativo com frequência configurada")
            return "Nenhum equipamento configurado para gerar checklists"
        
        logger.info(f"📊 {equipamentos_ativos.count()} equipamentos ativos encontrados")
        
        checklists_criados = 0
        equipamentos_processados = 0
        turnos = ['MANHA', 'TARDE', 'NOITE']
        
        # Processar cada equipamento
        for equipamento in equipamentos_ativos:
            equipamento_gerou_hoje = False
            
            # Verificar cada frequência configurada no equipamento
            for frequencia in equipamento.frequencias_checklist:
                deve_gerar = _deve_gerar_checklist(frequencia, dia_semana, dia_mes)
                
                if deve_gerar:
                    logger.info(f"✅ {equipamento.nome} - Gerando checklist {frequencia}")
                    
                    # Gerar checklist para cada turno
                    for turno in turnos:
                        # Verificar se já existe checklist para esta data/turno
                        checklist_existente = ChecklistNR12.objects.filter(
                            equipamento=equipamento,
                            data_checklist=hoje,
                            turno=turno
                        ).exists()
                        
                        if not checklist_existente:
                            # Criar novo checklist
                            checklist = ChecklistNR12.objects.create(
                                equipamento=equipamento,
                                data_checklist=hoje,
                                turno=turno,
                                status='PENDENTE',
                                uuid=uuid.uuid4(),
                                necessita_manutencao=False,
                                observacoes=f'Checklist {frequencia.lower()} gerado automaticamente'
                            )
                            
                            # Criar itens do checklist
                            itens_criados = _criar_itens_checklist(checklist)
                            checklists_criados += 1
                            equipamento_gerou_hoje = True
                            
                            logger.info(f"   📋 Checklist {turno} criado com {itens_criados} itens")
                        else:
                            logger.info(f"   ℹ️ Checklist {turno} já existe para hoje")
                else:
                    logger.debug(f"❌ {equipamento.nome} - {frequencia}: não deve gerar hoje")
            
            if equipamento_gerou_hoje:
                equipamentos_processados += 1
        
        # Log resultado final
        resultado = f"✅ Automação concluída: {checklists_criados} checklists criados para {equipamentos_processados} equipamentos"
        logger.info(resultado)
        
        # Enviar notificação se configurado
        if checklists_criados > 0:
            _notificar_checklists_gerados(checklists_criados, equipamentos_processados, hoje)
        
        return resultado
        
    except Exception as e:
        erro = f"❌ Erro na geração automática de checklists: {e}"
        logger.error(erro, exc_info=True)
        raise

def _deve_gerar_checklist(frequencia, dia_semana, dia_mes):
    """
    Determina se deve gerar checklist baseado na frequência
    
    Args:
        frequencia (str): DIARIA, SEMANAL ou MENSAL
        dia_semana (int): 0=segunda, 1=terça, ..., 6=domingo
        dia_mes (int): Dia do mês (1-31)
    
    Returns:
        bool: True se deve gerar checklist
    """
    if frequencia == 'DIARIA':
        return True
    elif frequencia == 'SEMANAL':
        return dia_semana == 0  # Segunda-feira
    elif frequencia == 'MENSAL':
        return dia_mes == 1  # Dia 1º do mês
    else:
        logger.warning(f"⚠️ Frequência desconhecida: {frequencia}")
        return False

def _criar_itens_checklist(checklist):
    """
    Cria itens do checklist baseado no tipo NR12 do equipamento
    
    Args:
        checklist: Instância do ChecklistNR12
    
    Returns:
        int: Número de itens criados
    """
    try:
        from backend.apps.nr12_checklist.models import ItemChecklistRealizado, ItemChecklistPadrao
        
        if not checklist.equipamento.tipo_nr12:
            logger.warning(f"⚠️ Equipamento {checklist.equipamento.nome} não tem tipo NR12 configurado")
            return 0
        
        # Buscar itens padrão para este tipo de equipamento
        itens_padrao = ItemChecklistPadrao.objects.filter(
            tipo_equipamento=checklist.equipamento.tipo_nr12,
            ativo=True
        ).order_by('ordem')
        
        if not itens_padrao.exists():
            logger.warning(f"⚠️ Nenhum item padrão encontrado para tipo {checklist.equipamento.tipo_nr12.nome}")
            return 0
        
        itens_criados = 0
        
        # Criar cada item do checklist
        for item_padrao in itens_padrao:
            ItemChecklistRealizado.objects.create(
                checklist=checklist,
                item_padrao=item_padrao,
                status='PENDENTE'
                # Removido 'observacoes' - o campo correto é 'observacao' (singular)
            )
            itens_criados += 1
        
        logger.debug(f"✅ {itens_criados} itens criados para checklist {checklist.uuid}")
        return itens_criados
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar itens do checklist {checklist.uuid}: {e}")
        return 0

def _notificar_checklists_gerados(total_checklists, total_equipamentos, data):
    """
    Envia notificação sobre checklists gerados
    """
    try:
        mensagem = f"""
🚀 CHECKLISTS GERADOS AUTOMATICAMENTE

📅 Data: {data.strftime('%d/%m/%Y')}
📋 Total de checklists: {total_checklists}
🔧 Equipamentos processados: {total_equipamentos}
⏰ Horário: {datetime.now().strftime('%H:%M')}

✅ Sistema funcionando corretamente!
        """
        
        logger.info(f"📢 Notificação: {total_checklists} checklists gerados")
        
        # Aqui você pode implementar envio via Telegram, email, etc.
        # Por enquanto apenas log
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificação: {e}")

# ================================================================
# TASKS DE MONITORAMENTO E CONTROLE
# ================================================================

@shared_task
def verificar_checklists_atrasados():
    """
    Verifica e marca checklists atrasados (do dia anterior)
    Executa todo dia às 7h da manhã
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        ontem = date.today() - timedelta(days=1)
        
        # Buscar checklists pendentes de ontem
        checklists_atrasados = ChecklistNR12.objects.filter(
            data_checklist=ontem,
            status='PENDENTE'
        ).select_related('equipamento')
        
        if not checklists_atrasados.exists():
            logger.info("✅ Nenhum checklist atrasado encontrado")
            return "Nenhum checklist atrasado"
        
        # Marcar como atrasados
        atrasados_count = checklists_atrasados.update(
            status='ATRASADO',
            observacoes='Checklist não realizado no prazo - marcado automaticamente como atrasado'
        )
        
        # Log detalhado
        for checklist in checklists_atrasados:
            logger.warning(f"⚠️ Checklist atrasado: {checklist.equipamento.nome} - {checklist.turno} - {ontem}")
        
        resultado = f"⚠️ {atrasados_count} checklists marcados como atrasados para {ontem}"
        logger.info(resultado)
        
        # Notificar responsáveis
        _notificar_checklists_atrasados(list(checklists_atrasados), ontem)
        
        return resultado
        
    except Exception as e:
        erro = f"❌ Erro ao verificar checklists atrasados: {e}"
        logger.error(erro, exc_info=True)
        raise

def _notificar_checklists_atrasados(checklists_atrasados, data):
    """
    Notifica responsáveis sobre checklists atrasados
    """
    try:
        if not checklists_atrasados:
            return
        
        mensagem = f"""
⚠️ CHECKLISTS ATRASADOS

📅 Data: {data.strftime('%d/%m/%Y')}
📋 Total atrasados: {len(checklists_atrasados)}

Equipamentos:
"""
        
        for checklist in checklists_atrasados[:10]:  # Limitar a 10
            mensagem += f"• {checklist.equipamento.nome} ({checklist.turno})\n"
        
        if len(checklists_atrasados) > 10:
            mensagem += f"... e mais {len(checklists_atrasados) - 10} checklists"
        
        logger.warning(f"📢 Notificação de atraso: {len(checklists_atrasados)} checklists")
        
        # Implementar envio via Telegram/email aqui
        
    except Exception as e:
        logger.error(f"❌ Erro ao notificar checklists atrasados: {e}")

@shared_task
def notificar_checklists_pendentes():
    """
    Notifica sobre checklists pendentes do dia atual
    Executa a cada 2 horas durante horário comercial (8h às 18h)
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        hoje = date.today()
        agora = datetime.now().time()
        
        # Verificar apenas durante horário comercial
        if agora.hour < 8 or agora.hour > 18:
            return "Fora do horário comercial"
        
        # Buscar checklists pendentes de hoje
        checklists_pendentes = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).select_related('equipamento', 'equipamento__cliente')
        
        if not checklists_pendentes.exists():
            logger.info("✅ Nenhum checklist pendente para hoje")
            return "Nenhum checklist pendente"
        
        total_pendentes = checklists_pendentes.count()
        
        # Agrupar por cliente para notificação
        pendentes_por_cliente = {}
        for checklist in checklists_pendentes:
            cliente = checklist.equipamento.cliente.razao_social
            if cliente not in pendentes_por_cliente:
                pendentes_por_cliente[cliente] = []
            pendentes_por_cliente[cliente].append(checklist)
        
        # Log detalhado
        logger.info(f"📋 {total_pendentes} checklists pendentes encontrados para {hoje}")
        for cliente, checklists in pendentes_por_cliente.items():
            logger.info(f"   {cliente}: {len(checklists)} pendentes")
        
        # Enviar notificações
        notificados = _enviar_notificacoes_pendentes(pendentes_por_cliente, hoje)
        
        resultado = f"📢 {total_pendentes} checklists pendentes, {notificados} notificações enviadas"
        logger.info(resultado)
        
        return resultado
        
    except Exception as e:
        erro = f"❌ Erro ao notificar checklists pendentes: {e}"
        logger.error(erro, exc_info=True)
        raise

def _enviar_notificacoes_pendentes(pendentes_por_cliente, data):
    """
    Envia notificações de checklists pendentes
    """
    try:
        notificados = 0
        
        for cliente, checklists in pendentes_por_cliente.items():
            mensagem = f"""
📋 CHECKLISTS PENDENTES

👤 Cliente: {cliente}
📅 Data: {data.strftime('%d/%m/%Y')}
⏰ Horário: {datetime.now().strftime('%H:%M')}

Equipamentos pendentes:
"""
            
            for checklist in checklists:
                mensagem += f"• {checklist.equipamento.nome} ({checklist.turno})\n"
            
            mensagem += "\n🚨 Por favor, realize os checklists pendentes!"
            
            # Implementar envio real aqui (Telegram, email, etc.)
            logger.info(f"📢 Notificação pendente para {cliente}: {len(checklists)} checklists")
            notificados += 1
        
        return notificados
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificações pendentes: {e}")
        return 0

# ================================================================
# TASKS DE RELATÓRIOS
# ================================================================

@shared_task
def gerar_relatorio_checklists_semanal():
    """
    Gera relatório semanal de checklists
    Executa toda segunda-feira às 7h da manhã
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        # Período: última semana (segunda a domingo)
        hoje = date.today()
        fim_semana = hoje - timedelta(days=1)  # Domingo
        inicio_semana = fim_semana - timedelta(days=6)  # Segunda anterior
        
        # Estatísticas gerais
        total_checklists = ChecklistNR12.objects.filter(
            data_checklist__range=[inicio_semana, fim_semana]
        ).count()
        
        # Estatísticas por status
        stats_status = ChecklistNR12.objects.filter(
            data_checklist__range=[inicio_semana, fim_semana]
        ).values('status').annotate(total=Count('id'))
        
        # Estatísticas por equipamento
        stats_equipamentos = ChecklistNR12.objects.filter(
            data_checklist__range=[inicio_semana, fim_semana]
        ).values('equipamento__nome').annotate(total=Count('id')).order_by('-total')[:10]
        
        # Preparar dados do relatório
        dados_relatorio = {
            'periodo': f"{inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m/%Y')}",
            'total_checklists': total_checklists,
            'por_status': {item['status']: item['total'] for item in stats_status},
            'top_equipamentos': list(stats_equipamentos),
            'gerado_em': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        # Log do relatório
        logger.info(f"📊 Relatório semanal gerado para {dados_relatorio['periodo']}")
        logger.info(f"   Total de checklists: {total_checklists}")
        for status, total in dados_relatorio['por_status'].items():
            logger.info(f"   {status}: {total}")
        
        # Enviar relatório
        _enviar_relatorio_semanal(dados_relatorio)
        
        return f"📊 Relatório semanal: {total_checklists} checklists no período"
        
    except Exception as e:
        erro = f"❌ Erro ao gerar relatório semanal: {e}"
        logger.error(erro, exc_info=True)
        raise

def _enviar_relatorio_semanal(dados):
    """
    Envia relatório semanal por email/Telegram
    """
    try:
        mensagem = f"""
📊 RELATÓRIO SEMANAL DE CHECKLISTS

📅 Período: {dados['periodo']}
📋 Total de checklists: {dados['total_checklists']}

📈 Por Status:
"""
        
        for status, total in dados['por_status'].items():
            porcentagem = (total / dados['total_checklists'] * 100) if dados['total_checklists'] > 0 else 0
            mensagem += f"• {status}: {total} ({porcentagem:.1f}%)\n"
        
        mensagem += f"\n🕐 Gerado em: {dados['gerado_em']}"
        
        logger.info(f"📧 Enviando relatório semanal: {dados['total_checklists']} checklists")
        
        # Implementar envio real aqui
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar relatório semanal: {e}")

# ================================================================
# TASKS DE MANUTENÇÃO
# ================================================================

@shared_task
def limpar_checklists_antigos():
    """
    Remove checklists muito antigos (mais de 2 anos)
    Executa todo domingo às 3h da manhã
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12
        
        # Data de corte: 2 anos atrás
        data_corte = date.today() - timedelta(days=730)
        
        # Contar checklists antigos
        checklists_antigos = ChecklistNR12.objects.filter(
            data_checklist__lt=data_corte
        )
        
        total_antigos = checklists_antigos.count()
        
        if total_antigos == 0:
            logger.info("✅ Nenhum checklist antigo para remover")
            return "Nenhum checklist antigo encontrado"
        
        # Remover (cuidado com cascade)
        checklists_antigos.delete()
        
        resultado = f"🧹 {total_antigos} checklists anteriores a {data_corte} removidos"
        logger.info(resultado)
        
        return resultado
        
    except Exception as e:
        erro = f"❌ Erro na limpeza de checklists antigos: {e}"
        logger.error(erro, exc_info=True)
        raise

@shared_task
def verificar_integridade_dados():
    """
    Verifica integridade dos dados de checklists
    Executa diariamente às 4h da manhã
    """
    try:
        from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado
        
        problemas = []
        
        # 1. Checklists sem itens
        checklists_sem_itens = ChecklistNR12.objects.filter(
            itens_realizados__isnull=True
        ).count()
        
        if checklists_sem_itens > 0:
            problemas.append(f"❌ {checklists_sem_itens} checklists sem itens")
        
        # 2. Itens órfãos (sem checklist)
        itens_orfaos = ItemChecklistRealizado.objects.filter(
            checklist__isnull=True
        ).count()
        
        if itens_orfaos > 0:
            problemas.append(f"❌ {itens_orfaos} itens órfãos")
        
        # 3. Checklists órfãos (sem equipamento)
        checklists_orfaos = ChecklistNR12.objects.filter(
            equipamento__isnull=True
        ).count()
        
        if checklists_orfaos > 0:
            problemas.append(f"❌ {checklists_orfaos} checklists órfãos")
        
        if not problemas:
            resultado = "✅ Integridade dos dados OK"
            logger.info(resultado)
        else:
            resultado = f"⚠️ Problemas encontrados: {'; '.join(problemas)}"
            logger.warning(resultado)
        
        return resultado
        
    except Exception as e:
        erro = f"❌ Erro na verificação de integridade: {e}"
        logger.error(erro, exc_info=True)
        raise