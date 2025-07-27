# backend/apps/nr12_checklist/tasks.py

from celery import shared_task
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistPadrao, ItemChecklistRealizado
from backend.apps.equipamentos.models import Equipamento
import logging

logger = logging.getLogger(__name__)

@shared_task
def gerar_checklists_diarios():
    """
    Gera checklists diários para equipamentos configurados
    """
    try:
        hoje = date.today()
        logger.info(f"🔄 Iniciando geração de checklists diários para {hoje}")
        
        # ✅ CORRIGIDO: Usar frequencias_checklist (plural) com __contains
        equipamentos = Equipamento.objects.filter(
            ativo_nr12=True,
            frequencias_checklist__contains=['DIARIA'],
            tipo_nr12__isnull=False
        ).select_related('tipo_nr12', 'cliente')
        
        total_equipamentos = equipamentos.count()
        logger.info(f"📊 Equipamentos encontrados para checklist diário: {total_equipamentos}")
        
        if total_equipamentos == 0:
            logger.warning("⚠️ Nenhum equipamento configurado para checklist diário")
            return "Nenhum equipamento configurado"
        
        checklists_criados = 0
        turnos = ['MANHA', 'TARDE', 'NOITE']
        
        for equipamento in equipamentos:
            logger.debug(f"🔧 Processando equipamento: {equipamento.nome}")
            
            # Verificar se tem itens padrão
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=equipamento.tipo_nr12,
                ativo=True
            )
            
            if not itens_padrao.exists():
                logger.warning(f"⚠️ Equipamento {equipamento.nome} não tem itens padrão configurados")
                continue
            
            # Criar checklist para cada turno (se não existir)
            for turno in turnos:
                checklist, criado = ChecklistNR12.objects.get_or_create(
                    equipamento=equipamento,
                    data_checklist=hoje,
                    turno=turno,
                    defaults={
                        'frequencia': 'DIARIA',
                        'status': 'PENDENTE'
                    }
                )
                
                if criado:
                    logger.debug(f"✅ Checklist criado: {equipamento.nome} - {turno}")
                    checklists_criados += 1
                    
                    # Criar itens do checklist
                    for item_padrao in itens_padrao:
                        ItemChecklistRealizado.objects.create(
                            checklist=checklist,
                            item_padrao=item_padrao,
                            status='PENDENTE'
                        )
                else:
                    logger.debug(f"ℹ️ Checklist já existe: {equipamento.nome} - {turno}")
        
        logger.info(f"✅ Checklists diários criados: {checklists_criados}")
        return f"Criados {checklists_criados} checklists diários"
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar checklists diários: {e}")
        raise

@shared_task
def gerar_checklists_semanais():
    """
    Gera checklists semanais para equipamentos configurados
    Executa toda segunda-feira
    """
    try:
        hoje = date.today()
        logger.info(f"🔄 Iniciando geração de checklists semanais para {hoje}")
        
        # ✅ CORRIGIDO: Usar frequencias_checklist (plural) com __contains
        equipamentos = Equipamento.objects.filter(
            ativo_nr12=True,
            frequencias_checklist__contains=['SEMANAL'],
            tipo_nr12__isnull=False
        ).select_related('tipo_nr12', 'cliente')
        
        total_equipamentos = equipamentos.count()
        logger.info(f"📊 Equipamentos encontrados para checklist semanal: {total_equipamentos}")
        
        if total_equipamentos == 0:
            logger.warning("⚠️ Nenhum equipamento configurado para checklist semanal")
            return "Nenhum equipamento configurado"
        
        checklists_criados = 0
        
        for equipamento in equipamentos:
            logger.debug(f"🔧 Processando equipamento: {equipamento.nome}")
            
            # Verificar se tem itens padrão
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=equipamento.tipo_nr12,
                ativo=True
            )
            
            if not itens_padrao.exists():
                logger.warning(f"⚠️ Equipamento {equipamento.nome} não tem itens padrão configurados")
                continue
            
            # Criar checklist semanal
            checklist, criado = ChecklistNR12.objects.get_or_create(
                equipamento=equipamento,
                data_checklist=hoje,
                turno='MANHA',  # Checklist semanal só no turno da manhã
                defaults={
                    'frequencia': 'SEMANAL',
                    'status': 'PENDENTE'
                }
            )
            
            if criado:
                logger.debug(f"✅ Checklist semanal criado: {equipamento.nome}")
                checklists_criados += 1
                
                # Criar itens do checklist
                for item_padrao in itens_padrao:
                    ItemChecklistRealizado.objects.create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        status='PENDENTE'
                    )
            else:
                logger.debug(f"ℹ️ Checklist semanal já existe: {equipamento.nome}")
        
        logger.info(f"✅ Checklists semanais criados: {checklists_criados}")
        return f"Criados {checklists_criados} checklists semanais"
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar checklists semanais: {e}")
        raise

@shared_task
def gerar_checklists_mensais():
    """
    Gera checklists mensais para equipamentos configurados
    Executa todo dia 1º do mês
    """
    try:
        hoje = date.today()
        logger.info(f"🔄 Iniciando geração de checklists mensais para {hoje}")
        
        # ✅ CORRIGIDO: Usar frequencias_checklist (plural) com __contains
        equipamentos = Equipamento.objects.filter(
            ativo_nr12=True,
            frequencias_checklist__contains=['MENSAL'],
            tipo_nr12__isnull=False
        ).select_related('tipo_nr12', 'cliente')
        
        total_equipamentos = equipamentos.count()
        logger.info(f"📊 Equipamentos encontrados para checklist mensal: {total_equipamentos}")
        
        if total_equipamentos == 0:
            logger.warning("⚠️ Nenhum equipamento configurado para checklist mensal")
            return "Nenhum equipamento configurado"
        
        checklists_criados = 0
        
        for equipamento in equipamentos:
            logger.debug(f"🔧 Processando equipamento: {equipamento.nome}")
            
            # Verificar se tem itens padrão
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=equipamento.tipo_nr12,
                ativo=True
            )
            
            if not itens_padrao.exists():
                logger.warning(f"⚠️ Equipamento {equipamento.nome} não tem itens padrão configurados")
                continue
            
            # Criar checklist mensal
            checklist, criado = ChecklistNR12.objects.get_or_create(
                equipamento=equipamento,
                data_checklist=hoje,
                turno='MANHA',  # Checklist mensal só no turno da manhã
                defaults={
                    'frequencia': 'MENSAL',
                    'status': 'PENDENTE'
                }
            )
            
            if criado:
                logger.debug(f"✅ Checklist mensal criado: {equipamento.nome}")
                checklists_criados += 1
                
                # Criar itens do checklist
                for item_padrao in itens_padrao:
                    ItemChecklistRealizado.objects.create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        status='PENDENTE'
                    )
            else:
                logger.debug(f"ℹ️ Checklist mensal já existe: {equipamento.nome}")
        
        logger.info(f"✅ Checklists mensais criados: {checklists_criados}")
        return f"Criados {checklists_criados} checklists mensais"
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar checklists mensais: {e}")
        raise

@shared_task
def verificar_checklists_atrasados():
    """
    Verifica checklists atrasados e gera alertas
    """
    try:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        
        # Buscar checklists pendentes de ontem
        checklists_atrasados = ChecklistNR12.objects.filter(
            status='PENDENTE',
            data_checklist__lt=hoje
        ).select_related('equipamento', 'equipamento__cliente')
        
        total_atrasados = checklists_atrasados.count()
        logger.info(f"📊 Checklists atrasados encontrados: {total_atrasados}")
        
        if total_atrasados > 0:
            # Aqui você pode implementar notificações
            logger.warning(f"⚠️ {total_atrasados} checklists estão atrasados!")
            
            # Exemplo: criar alertas de manutenção
            for checklist in checklists_atrasados:
                from backend.apps.nr12_checklist.models import AlertaManutencao
                
                AlertaManutencao.objects.get_or_create(
                    equipamento=checklist.equipamento,
                    checklist_origem=checklist,
                    defaults={
                        'tipo': 'PREVENTIVA',
                        'titulo': f'Checklist {checklist.frequencia} em atraso',
                        'descricao': f'Checklist do dia {checklist.data_checklist} não foi realizado',
                        'criticidade': 'MEDIA',
                        'data_prevista': hoje + timedelta(days=1)
                    }
                )
        
        return f"Verificados {total_atrasados} checklists atrasados"
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar checklists atrasados: {e}")
        raise