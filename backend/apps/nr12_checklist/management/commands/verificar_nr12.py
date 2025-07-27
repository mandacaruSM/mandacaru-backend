# backend/apps/nr12_checklist/management/commands/verificar_nr12.py

from django.core.management.base import BaseCommand
from django.conf import settings
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistPadrao, TipoEquipamentoNR12
from datetime import date, timedelta
import json

class Command(BaseCommand):
    help = 'Verifica configuração completa do sistema NR12'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corrigir',
            action='store_true',
            help='Corrige problemas encontrados automaticamente'
        )
        parser.add_argument(
            '--relatorio',
            action='store_true',
            help='Gera relatório detalhado'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 VERIFICAÇÃO COMPLETA DO SISTEMA NR12'))
        self.stdout.write('=' * 60)
        
        problemas = []
        
        # 1. Verificar Celery
        problemas.extend(self.verificar_celery())
        
        # 2. Verificar Modelos
        problemas.extend(self.verificar_modelos())
        
        # 3. Verificar Equipamentos
        problemas.extend(self.verificar_equipamentos())
        
        # 4. Verificar Schedules
        problemas.extend(self.verificar_schedules())
        
        # 5. Verificar Checklists Recentes
        problemas.extend(self.verificar_checklists_recentes())
        
        # Resumo de problemas
        self.exibir_resumo(problemas)
        
        # Corrigir problemas se solicitado
        if options['corrigir']:
            self.corrigir_problemas(problemas)
        
        # Gerar relatório se solicitado
        if options['relatorio']:
            self.gerar_relatorio()

    def verificar_celery(self):
        """Verifica configuração do Celery"""
        self.stdout.write('\n🔧 VERIFICANDO CELERY:')
        self.stdout.write('-' * 30)
        
        problemas = []
        
        # Verificar se CELERY_BEAT_SCHEDULE está configurado
        if hasattr(settings, 'CELERY_BEAT_SCHEDULE'):
            schedule = settings.CELERY_BEAT_SCHEDULE
            
            # Verificar tasks NR12
            tasks_nr12 = [
                'checklists_diarios_6h',
                'checklists_semanais_segunda_6h', 
                'checklists_mensais_1_6h'
            ]
            
            for task_name in tasks_nr12:
                if task_name in schedule:
                    self.stdout.write(f'   ✅ {task_name}: Configurado')
                else:
                    self.stdout.write(f'   ❌ {task_name}: NÃO configurado')
                    problemas.append(f'Task {task_name} não está no CELERY_BEAT_SCHEDULE')
        else:
            self.stdout.write('   ❌ CELERY_BEAT_SCHEDULE não configurado')
            problemas.append('CELERY_BEAT_SCHEDULE não existe no settings.py')
        
        # Verificar broker
        if hasattr(settings, 'CELERY_BROKER_URL'):
            self.stdout.write(f'   ✅ Broker: {settings.CELERY_BROKER_URL}')
        else:
            self.stdout.write('   ❌ CELERY_BROKER_URL não configurado')
            problemas.append('CELERY_BROKER_URL não configurado')
        
        return problemas

    def verificar_modelos(self):
        """Verifica integridade dos modelos"""
        self.stdout.write('\n📊 VERIFICANDO MODELOS:')
        self.stdout.write('-' * 30)
        
        problemas = []
        
        # Tipos NR12
        tipos_count = TipoEquipamentoNR12.objects.count()
        self.stdout.write(f'   Tipos de Equipamento NR12: {tipos_count}')
        if tipos_count == 0:
            problemas.append('Nenhum tipo de equipamento NR12 cadastrado')
        
        # Itens padrão por tipo
        for tipo in TipoEquipamentoNR12.objects.all():
            itens_count = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=tipo,
                ativo=True
            ).count()
            self.stdout.write(f'   Itens padrão ({tipo.nome}): {itens_count}')
            if itens_count == 0:
                problemas.append(f'Tipo {tipo.nome} não tem itens de checklist padrão')
        
        # Equipamentos configurados
        equipamentos_nr12 = Equipamento.objects.filter(ativo_nr12=True)
        self.stdout.write(f'   Equipamentos ativos NR12: {equipamentos_nr12.count()}')
        
        # Equipamentos sem tipo NR12
        sem_tipo = equipamentos_nr12.filter(tipo_nr12__isnull=True).count()
        if sem_tipo > 0:
            self.stdout.write(f'   ⚠️ Equipamentos sem tipo NR12: {sem_tipo}')
            problemas.append(f'{sem_tipo} equipamentos NR12 sem tipo configurado')
        
        # Equipamentos sem frequência
        sem_freq = equipamentos_nr12.filter(
            frequencias_checklist__isnull=True
        ).count() + equipamentos_nr12.filter(
            frequencias_checklist=[]
        ).count()
        
        if sem_freq > 0:
            self.stdout.write(f'   ⚠️ Equipamentos sem frequência: {sem_freq}')
            problemas.append(f'{sem_freq} equipamentos NR12 sem frequência configurada')
        
        return problemas

    def verificar_equipamentos(self):
        """Verifica configuração detalhada dos equipamentos"""
        self.stdout.write('\n🔧 VERIFICANDO EQUIPAMENTOS:')
        self.stdout.write('-' * 30)
        
        problemas = []
        
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        
        for freq in ['DIARIA', 'SEMANAL', 'MENSAL']:
            count = equipamentos.filter(
                frequencias_checklist__contains=[freq],
                tipo_nr12__isnull=False
            ).count()
            self.stdout.write(f'   Equipamentos {freq}: {count}')
            
            if count == 0:
                problemas.append(f'Nenhum equipamento configurado para frequência {freq}')
        
        # Verificar equipamentos problemáticos
        equipamentos_problemas = equipamentos.filter(
            tipo_nr12__isnull=True
        ) | equipamentos.filter(
            frequencias_checklist__isnull=True
        ) | equipamentos.filter(
            frequencias_checklist=[]
        )
        
        if equipamentos_problemas.exists():
            self.stdout.write('\n   🚨 EQUIPAMENTOS COM PROBLEMAS:')
            for eq in equipamentos_problemas[:5]:  # Mostrar apenas 5
                issues = []
                if not eq.tipo_nr12:
                    issues.append('sem tipo NR12')
                if not eq.frequencias_checklist:
                    issues.append('sem frequência')
                
                # ✅ CORRIGIDO: usar razao_social
                cliente_nome = "N/A"
                if eq.cliente:
                    cliente_nome = eq.cliente.razao_social or eq.cliente.nome_fantasia or "N/A"
                
                self.stdout.write(f'      📌 {eq.nome} ({cliente_nome}): {", ".join(issues)}')
        
        return problemas

    def verificar_schedules(self):
        """Verifica agendamentos do Celery"""
        self.stdout.write('\n⏰ VERIFICANDO SCHEDULES:')
        self.stdout.write('-' * 30)
        
        problemas = []
        
        if hasattr(settings, 'CELERY_BEAT_SCHEDULE'):
            schedule = settings.CELERY_BEAT_SCHEDULE
            
            # Verificar horários configurados
            schedules_esperados = {
                'checklists_diarios_6h': 'Todo dia às 6:00',
                'checklists_semanais_segunda_6h': 'Segunda-feira às 6:00',
                'checklists_mensais_1_6h': 'Dia 1 às 6:00'
            }
            
            for task_name, descricao in schedules_esperados.items():
                if task_name in schedule:
                    task_config = schedule[task_name]
                    self.stdout.write(f'   ✅ {descricao}: Configurado')
                    
                    # Verificar se a task existe
                    task_path = task_config.get('task', '')
                    if 'nr12_checklist.tasks' in task_path:
                        self.stdout.write(f'      Task: {task_path}')
                    else:
                        problemas.append(f'Task {task_name} aponta para path incorreto: {task_path}')
                else:
                    self.stdout.write(f'   ❌ {descricao}: NÃO configurado')
                    problemas.append(f'Schedule {task_name} não configurado')
        
        return problemas

    def verificar_checklists_recentes(self):
        """Verifica checklists criados recentemente"""
        self.stdout.write('\n📋 VERIFICANDO CHECKLISTS RECENTES:')
        self.stdout.write('-' * 30)
        
        problemas = []
        hoje = date.today()
        
        # Últimos 7 dias
        for i in range(7):
            data = hoje - timedelta(days=i)
            count = ChecklistNR12.objects.filter(data_checklist=data).count()
            
            if i == 0:
                self.stdout.write(f'   Hoje ({data}): {count} checklists')
                if count == 0:
                    problemas.append('Nenhum checklist criado hoje')
            elif i <= 3:
                self.stdout.write(f'   {data}: {count} checklists')
        
        # Checklists por status hoje
        for status_code, status_name in ChecklistNR12.STATUS_CHOICES:
            count = ChecklistNR12.objects.filter(
                data_checklist=hoje,
                status=status_code
            ).count()
            if count > 0:
                self.stdout.write(f'   Status {status_name}: {count}')
        
        # Checklists atrasados
        atrasados = ChecklistNR12.objects.filter(
            status='PENDENTE',
            data_checklist__lt=hoje
        ).count()
        
        if atrasados > 0:
            self.stdout.write(f'   ⚠️ Checklists atrasados: {atrasados}')
            problemas.append(f'{atrasados} checklists estão atrasados')
        
        return problemas

    def exibir_resumo(self, problemas):
        """Exibe resumo dos problemas encontrados"""
        self.stdout.write('\n📊 RESUMO DA VERIFICAÇÃO:')
        self.stdout.write('=' * 50)
        
        if not problemas:
            self.stdout.write(self.style.SUCCESS('✅ SISTEMA NR12 FUNCIONANDO PERFEITAMENTE!'))
            return
        
        self.stdout.write(self.style.WARNING(f'⚠️ {len(problemas)} PROBLEMAS ENCONTRADOS:'))
        self.stdout.write('')
        
        for i, problema in enumerate(problemas, 1):
            self.stdout.write(f'   {i}. {problema}')
        
        self.stdout.write('')
        self.stdout.write('💡 Use --corrigir para tentar corrigir automaticamente')

    def corrigir_problemas(self, problemas):
        """Tenta corrigir problemas automaticamente"""
        self.stdout.write('\n🔧 CORRIGINDO PROBLEMAS:')
        self.stdout.write('-' * 30)
        
        corrigidos = 0
        
        # Criar tipos NR12 básicos se não existirem
        if TipoEquipamentoNR12.objects.count() == 0:
            tipos_basicos = [
                {'nome': 'Escavadeira', 'descricao': 'Escavadeiras hidráulicas'},
                {'nome': 'Retroescavadeira', 'descricao': 'Retroescavadeiras'},
                {'nome': 'Trator', 'descricao': 'Tratores agrícolas e industriais'},
                {'nome': 'Caminhão', 'descricao': 'Caminhões e veículos pesados'},
            ]
            
            for tipo_data in tipos_basicos:
                TipoEquipamentoNR12.objects.create(**tipo_data)
                self.stdout.write(f'   ✅ Criado tipo: {tipo_data["nome"]}')
                corrigidos += 1
        
        # Criar itens padrão básicos para tipos sem itens
        for tipo in TipoEquipamentoNR12.objects.all():
            if not ItemChecklistPadrao.objects.filter(tipo_equipamento=tipo).exists():
                itens_basicos = [
                    'Verificar níveis de óleo e fluidos',
                    'Testar funcionamento dos freios',
                    'Verificar estado dos pneus/esteiras',
                    'Testar luzes e sinalização',
                    'Verificar dispositivos de segurança',
                    'Limpar filtros de ar',
                    'Verificar vazamentos',
                    'Testar sistema hidráulico',
                ]
                
                for i, item in enumerate(itens_basicos, 1):
                    ItemChecklistPadrao.objects.create(
                        tipo_equipamento=tipo,
                        item=item,
                        descricao=f'Verificação padrão: {item}',
                        criticidade='MEDIA',
                        ordem=i
                    )
                
                self.stdout.write(f'   ✅ Criados {len(itens_basicos)} itens para {tipo.nome}')
                corrigidos += 1
        
        self.stdout.write(f'\n✅ {corrigidos} problemas corrigidos automaticamente')

    def gerar_relatorio(self):
        """Gera relatório detalhado do sistema"""
        self.stdout.write('\n📄 RELATÓRIO DETALHADO:')
        self.stdout.write('=' * 50)
        
        hoje = date.today()
        
        # Estatísticas gerais
        stats = {
            'tipos_nr12': TipoEquipamentoNR12.objects.count(),
            'itens_padrao': ItemChecklistPadrao.objects.count(),
            'equipamentos_nr12': Equipamento.objects.filter(ativo_nr12=True).count(),
            'checklists_hoje': ChecklistNR12.objects.filter(data_checklist=hoje).count(),
            'checklists_total': ChecklistNR12.objects.count(),
        }
        
        self.stdout.write('📊 ESTATÍSTICAS GERAIS:')
        for key, value in stats.items():
            self.stdout.write(f'   {key.replace("_", " ").title()}: {value}')
        
        # Equipamentos por frequência
        self.stdout.write('\n🔧 EQUIPAMENTOS POR FREQUÊNCIA:')
        for freq in ['DIARIA', 'SEMANAL', 'MENSAL']:
            count = Equipamento.objects.filter(
                ativo_nr12=True,
                frequencias_checklist__contains=[freq]
            ).count()
            self.stdout.write(f'   {freq}: {count} equipamentos')
        
        # Checklists por status (últimos 7 dias)
        self.stdout.write('\n📋 CHECKLISTS POR STATUS (últimos 7 dias):')
        data_inicio = hoje - timedelta(days=7)
        
        for status_code, status_name in ChecklistNR12.STATUS_CHOICES:
            count = ChecklistNR12.objects.filter(
                data_checklist__gte=data_inicio,
                status=status_code
            ).count()
            self.stdout.write(f'   {status_name}: {count}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Relatório concluído!'))