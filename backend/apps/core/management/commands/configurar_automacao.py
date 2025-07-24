# ================================================================
# COMANDO COMPLETO PARA CONFIGURAR AUTOMAÇÃO DE CHECKLISTS
# backend/apps/core/management/commands/configurar_automacao.py
# ================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.db.models import Count, Q
from django.conf import settings
import json
import sys

class Command(BaseCommand):
    help = '''
    Configura e gerencia o sistema completo de automação de checklists NR12
    
    Funcionalidades:
    - Configuração inicial do sistema
    - Teste da automação
    - Verificação de configurações
    - Status dos checklists
    - Diagnóstico completo
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--inicial',
            action='store_true',
            help='Configuração inicial completa do sistema'
        )
        parser.add_argument(
            '--testar',
            action='store_true',
            help='Testa a geração de checklists automáticos'
        )
        parser.add_argument(
            '--verificar-celery',
            action='store_true',
            help='Verifica configuração do Celery e agendamentos'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mostra status atual detalhado dos checklists'
        )
        parser.add_argument(
            '--diagnostico',
            action='store_true',
            help='Executa diagnóstico completo do sistema'
        )
        parser.add_argument(
            '--criar-dados-teste',
            action='store_true',
            help='Cria dados de teste para validação'
        )
        parser.add_argument(
            '--equipamento-id',
            type=int,
            help='ID do equipamento para configurar (usado com --configurar-frequencia)'
        )
        parser.add_argument(
            '--frequencias',
            nargs='+',
            choices=['DIARIA', 'SEMANAL', 'MENSAL'],
            help='Frequências para configurar no equipamento'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 SISTEMA DE AUTOMAÇÃO DE CHECKLISTS NR12'))
        self.stdout.write('=' * 70)
        self.stdout.write('📅 Agendamentos automáticos:')
        self.stdout.write('   • DIÁRIO: Todo dia às 6h da manhã')
        self.stdout.write('   • SEMANAL: Toda segunda-feira às 6h da manhã')
        self.stdout.write('   • MENSAL: Todo dia 1º às 6h da manhã')
        self.stdout.write('=' * 70)
        
        # Executar ações baseadas nos argumentos
        if options['inicial']:
            self._configuracao_inicial()
        elif options['testar']:
            self._testar_automacao()
        elif options['verificar_celery']:
            self._verificar_celery()
        elif options['status']:
            self._mostrar_status_detalhado()
        elif options['diagnostico']:
            self._executar_diagnostico_completo()
        elif options['criar_dados_teste']:
            self._criar_dados_teste()
        elif options['equipamento_id'] and options['frequencias']:
            self._configurar_frequencia_equipamento(options['equipamento_id'], options['frequencias'])
        else:
            self._mostrar_menu_interativo()

    def _mostrar_menu_interativo(self):
        """Mostra menu interativo para o usuário"""
        self.stdout.write('\n🔧 OPÇÕES DISPONÍVEIS:')
        self.stdout.write('-' * 30)
        
        opcoes = [
            ('1', 'Configuração inicial completa', '--inicial'),
            ('2', 'Verificar status atual', '--status'),
            ('3', 'Testar automação', '--testar'),
            ('4', 'Verificar Celery', '--verificar-celery'),
            ('5', 'Diagnóstico completo', '--diagnostico'),
            ('6', 'Criar dados de teste', '--criar-dados-teste'),
        ]
        
        for num, desc, cmd in opcoes:
            self.stdout.write(f'   {num}. {desc}')
            self.stdout.write(f'      python manage.py configurar_automacao {cmd}')
        
        self.stdout.write('\n💡 Para mais opções, execute: python manage.py configurar_automacao --help')

    def _configuracao_inicial(self):
        """Executa configuração inicial completa do sistema"""
        self.stdout.write('\n🔧 CONFIGURAÇÃO INICIAL DO SISTEMA')
        self.stdout.write('=' * 45)
        
        # Passo 1: Verificar dependências
        self._verificar_dependencias()
        
        # Passo 2: Configurar modelos base
        self._configurar_modelos_base()
        
        # Passo 3: Verificar equipamentos
        self._verificar_e_configurar_equipamentos()
        
        # Passo 4: Configurar tipos NR12
        self._configurar_tipos_nr12()
        
        # Passo 5: Verificar Celery
        self._verificar_configuracao_celery()
        
        # Passo 6: Mostrar próximos passos
        self._mostrar_proximos_passos()

    def _verificar_dependencias(self):
        """Verifica se todas as dependências estão instaladas"""
        self.stdout.write('\n📦 VERIFICANDO DEPENDÊNCIAS')
        self.stdout.write('-' * 30)
        
        dependencias = [
            ('celery', 'Celery para tasks assíncronas'),
            ('redis', 'Redis para broker do Celery'),
            ('django_filters', 'Django filters para APIs'),
            ('qrcode', 'QR Code para checklists'),
        ]
        
        for pacote, descricao in dependencias:
            try:
                __import__(pacote)
                self.stdout.write(f'✅ {pacote}: {descricao}')
            except ImportError:
                self.stdout.write(self.style.ERROR(f'❌ {pacote}: NÃO INSTALADO - {descricao}'))
                self.stdout.write(f'   Execute: pip install {pacote}')

    def _configurar_modelos_base(self):
        """Configura modelos base necessários"""
        self.stdout.write('\n🏗️ CONFIGURANDO MODELOS BASE')
        self.stdout.write('-' * 35)
        
        # Verificar migrações
        try:
            from django.core.management import call_command
            from io import StringIO
            
            # Verificar se há migrações pendentes
            out = StringIO()
            call_command('showmigrations', '--plan', stdout=out)
            migrations_output = out.getvalue()
            
            if '[ ]' in migrations_output:
                self.stdout.write('🔄 Aplicando migrações pendentes...')
                call_command('migrate', verbosity=0)
                self.stdout.write('✅ Migrações aplicadas')
            else:
                self.stdout.write('✅ Todas as migrações estão aplicadas')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro nas migrações: {e}'))

    def _verificar_e_configurar_equipamentos(self):
        """Verifica e configura equipamentos"""
        self.stdout.write('\n🔧 VERIFICANDO EQUIPAMENTOS')
        self.stdout.write('-' * 30)
        
        try:
            from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
            
            # Estatísticas
            total_equipamentos = Equipamento.objects.count()
            equipamentos_nr12 = Equipamento.objects.filter(ativo_nr12=True).count()
            com_frequencia = Equipamento.objects.exclude(frequencias_checklist=[]).count()
            sem_frequencia = Equipamento.objects.filter(
                ativo_nr12=True,
                frequencias_checklist=[]
            ).count()
            
            self.stdout.write(f'📊 Total de equipamentos: {total_equipamentos}')
            self.stdout.write(f'✅ Ativos NR12: {equipamentos_nr12}')
            self.stdout.write(f'🔄 Com frequência configurada: {com_frequencia}')
            self.stdout.write(f'⚠️ Sem frequência configurada: {sem_frequencia}')
            
            # Mostrar categorias
            categorias = CategoriaEquipamento.objects.annotate(
                total_eq=Count('equipamentos')
            ).order_by('-total_eq')
            
            self.stdout.write('\n📋 Categorias de equipamentos:')
            for categoria in categorias:
                self.stdout.write(f'   • {categoria.nome}: {categoria.total_eq} equipamentos')
            
            # Sugerir configuração se necessário
            if sem_frequencia > 0:
                self._sugerir_configuracao_frequencias(sem_frequencia)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar equipamentos: {e}'))

    def _sugerir_configuracao_frequencias(self, total_sem_freq):
        """Sugere configuração de frequências"""
        self.stdout.write(f'\n💡 CONFIGURAÇÃO DE FREQUÊNCIAS')
        self.stdout.write('-' * 35)
        
        try:
            from backend.apps.equipamentos.models import Equipamento
            
            equipamentos_sem_freq = Equipamento.objects.filter(
                ativo_nr12=True,
                frequencias_checklist=[]
            ).select_related('categoria')[:10]
            
            self.stdout.write(f'🔧 {total_sem_freq} equipamentos precisam de configuração:')
            
            for eq in equipamentos_sem_freq:
                categoria = eq.categoria.nome if eq.categoria else 'Sem categoria'
                self.stdout.write(f'   • ID {eq.id}: {eq.nome} ({categoria})')
            
            if total_sem_freq > 10:
                self.stdout.write(f'   ... e mais {total_sem_freq - 10} equipamentos')
            
            self.stdout.write('\n📝 Para configurar frequências:')
            self.stdout.write('1. Via Django Admin:')
            self.stdout.write('   - Acesse /admin/equipamentos/equipamento/')
            self.stdout.write('   - Edite cada equipamento')
            self.stdout.write('   - Marque as frequências desejadas')
            
            self.stdout.write('\n2. Via comando (exemplo):')
            self.stdout.write('   python manage.py configurar_automacao --equipamento-id 1 --frequencias DIARIA SEMANAL')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))

    def _configurar_frequencia_equipamento(self, equipamento_id, frequencias):
        """Configura frequência para um equipamento específico"""
        try:
            from backend.apps.equipamentos.models import Equipamento
            
            equipamento = Equipamento.objects.get(id=equipamento_id)
            equipamento.frequencias_checklist = frequencias
            equipamento.ativo_nr12 = True
            equipamento.save()
            
            self.stdout.write(f'✅ Equipamento {equipamento.nome} configurado com frequências: {", ".join(frequencias)}')
            
        except Equipamento.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Equipamento com ID {equipamento_id} não encontrado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao configurar equipamento: {e}'))

    def _configurar_tipos_nr12(self):
        """Configura tipos NR12 e itens padrão"""
        self.stdout.write('\n📋 CONFIGURANDO TIPOS NR12')
        self.stdout.write('-' * 30)
        
        try:
            from backend.apps.nr12_checklist.models import TipoEquipamentoNR12, ItemChecklistPadrao
            from django.core.management import call_command
            
            tipos_count = TipoEquipamentoNR12.objects.count()
            itens_count = ItemChecklistPadrao.objects.count()
            
            self.stdout.write(f'📊 Tipos NR12 existentes: {tipos_count}')
            self.stdout.write(f'📝 Itens padrão existentes: {itens_count}')
            
            if tipos_count == 0:
                self.stdout.write('🔄 Criando tipos e itens padrão...')
                try:
                    call_command('criar_checklist', verbosity=0)
                    self.stdout.write('✅ Tipos e itens padrão criados')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️ Erro ao criar tipos: {e}'))
                    self.stdout.write('💡 Execute manualmente: python manage.py criar_checklist')
            else:
                self.stdout.write('✅ Tipos NR12 já configurados')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao configurar tipos NR12: {e}'))

    def _verificar_configuracao_celery(self):
        """Verifica configuração do Celery"""
        self.stdout.write('\n🔍 VERIFICANDO CONFIGURAÇÃO DO CELERY')
        self.stdout.write('-' * 42)
        
        try:
            # Verificar se o Celery está configurado
            from celery import current_app
            
            # Verificar agendamentos principais
            beat_schedule = current_app.conf.beat_schedule
            
            tasks_principais = [
                ('gerar-checklists-automaticos', '🕕 Geração automática de checklists'),
                ('verificar-checklists-atrasados', '⏰ Verificação de checklists atrasados'),
                ('notificar-checklists-pendentes', '📢 Notificação de checklists pendentes'),
                ('relatorio-checklists-semanal', '📊 Relatório semanal'),
            ]
            
            for task_name, descricao in tasks_principais:
                if task_name in beat_schedule:
                    schedule = beat_schedule[task_name]['schedule']
                    self.stdout.write(f'✅ {descricao}')
                    self.stdout.write(f'   Agendamento: {schedule}')
                else:
                    self.stdout.write(f'❌ {descricao}: NÃO CONFIGURADO')
            
            # Mostrar resumo dos agendamentos
            self._mostrar_resumo_agendamentos()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na verificação do Celery: {e}'))
            self.stdout.write('💡 Certifique-se de que o arquivo backend/celery.py está configurado corretamente')

    def _mostrar_resumo_agendamentos(self):
        """Mostra resumo dos agendamentos configurados"""
        self.stdout.write('\n📅 RESUMO DOS AGENDAMENTOS:')
        self.stdout.write('-' * 25)
        
        agendamentos = [
            ('6:00', 'Geração automática de checklists (diário/semanal/mensal)'),
            ('7:00', 'Verificação de checklists atrasados'),
            ('8:00, 10:00, 12:00, 14:00, 16:00, 18:00', 'Notificação de checklists pendentes'),
            ('7:30 (segunda-feira)', 'Relatório semanal de checklists'),
            ('5:00', 'Cálculo de KPIs diários'),
            ('2:00', 'Backup diário'),
        ]
        
        for horario, descricao in agendamentos:
            self.stdout.write(f'🕐 {horario}: {descricao}')

    def _verificar_celery(self):
        """Verifica detalhadamente a configuração do Celery"""
        self.stdout.write('\n🔍 DIAGNÓSTICO DETALHADO DO CELERY')
        self.stdout.write('=' * 40)
        
        try:
            from celery import current_app
            import redis
            
            # 1. Verificar configuração básica
            self.stdout.write('\n📋 Configuração básica:')
            self.stdout.write(f'   • Timezone: {current_app.conf.timezone}')
            self.stdout.write(f'   • Broker: {current_app.conf.broker_url}')
            self.stdout.write(f'   • Result backend: {current_app.conf.result_backend}')
            
            # 2. Testar conexão com Redis
            self.stdout.write('\n🔗 Testando conexão com Redis:')
            try:
                r = redis.Redis.from_url(current_app.conf.broker_url)
                r.ping()
                self.stdout.write('   ✅ Conexão com Redis OK')
            except Exception as e:
                self.stdout.write(f'   ❌ Erro de conexão com Redis: {e}')
            
            # 3. Verificar tasks registradas
            self.stdout.write('\n📝 Tasks registradas:')
            registered_tasks = current_app.tasks
            
            task_patterns = [
                'backend.apps.core.tasks',
                'backend.apps.bot_telegram',
                'backend.apps.nr12_checklist',
            ]
            
            for pattern in task_patterns:
                matching_tasks = [name for name in registered_tasks.keys() if pattern in name]
                self.stdout.write(f'   • {pattern}: {len(matching_tasks)} tasks')
            
            # 4. Verificar agendamentos
            self.stdout.write('\n⏰ Agendamentos configurados:')
            beat_schedule = current_app.conf.beat_schedule
            self.stdout.write(f'   Total de agendamentos: {len(beat_schedule)}')
            
            for name, config in beat_schedule.items():
                if 'checklist' in name.lower():
                    self.stdout.write(f'   ✅ {name}: {config["schedule"]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na verificação: {e}'))

    def _testar_automacao(self):
        """Testa a automação de checklists"""
        self.stdout.write('\n🧪 TESTANDO AUTOMAÇÃO DE CHECKLISTS')
        self.stdout.write('=' * 40)
        
        try:
            from backend.apps.core.tasks import gerar_checklists_automatico
            from backend.apps.equipamentos.models import Equipamento
            
            # 1. Verificar pré-requisitos
            self.stdout.write('\n📋 Verificando pré-requisitos:')
            
            equipamentos_ativos = Equipamento.objects.filter(
                ativo_nr12=True
            ).exclude(frequencias_checklist=[])
            
            if not equipamentos_ativos.exists():
                self.stdout.write('❌ Nenhum equipamento ativo com frequência configurada')
                self.stdout.write('💡 Configure primeiro os equipamentos com --inicial')
                return
            
            self.stdout.write(f'✅ {equipamentos_ativos.count()} equipamentos ativos encontrados')
            
            # 2. Mostrar equipamentos que serão processados
            self.stdout.write('\n🔧 Equipamentos que serão processados:')
            for eq in equipamentos_ativos[:5]:
                freq_str = ', '.join(eq.frequencias_checklist)
                self.stdout.write(f'   • {eq.nome}: {freq_str}')
            
            if equipamentos_ativos.count() > 5:
                self.stdout.write(f'   ... e mais {equipamentos_ativos.count() - 5} equipamentos')
            
            # 3. Executar teste
            self.stdout.write('\n🚀 Executando teste de geração automática...')
            
            try:
                # Tentar executar direto primeiro
                from backend.apps.core.tasks import gerar_checklists_automatico
                resultado = gerar_checklists_automatico()
                self.stdout.write(f'✅ Teste executado com sucesso: {resultado}')
                
            except Exception as e:
                # Se falhar, tentar via Celery
                self.stdout.write(f'⚠️ Execução direta falhou: {e}')
                self.stdout.write('🔄 Tentando via Celery...')
                
                task_result = gerar_checklists_automatico.delay()
                self.stdout.write(f'⏳ Task submetida: {task_result.id}')
                
                # Aguardar resultado por 30 segundos
                try:
                    resultado = task_result.get(timeout=30)
                    self.stdout.write(f'✅ Resultado via Celery: {resultado}')
                except Exception as timeout_error:
                    self.stdout.write(f'⏳ Task em execução (timeout 30s): {timeout_error}')
                    self.stdout.write('💡 Verifique os logs do Celery worker')
            
            # 4. Verificar resultados
            self._verificar_resultados_teste()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no teste: {e}'))
            
    def _verificar_resultados_teste(self):
        """Verifica os resultados do teste"""
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            
            hoje = date.today()
            checklists_hoje = ChecklistNR12.objects.filter(data_checklist=hoje)
            
            if checklists_hoje.exists():
                total = checklists_hoje.count()
                por_status = checklists_hoje.values('status').annotate(total=Count('id'))
                
                self.stdout.write(f'\n📊 Resultados do teste:')
                self.stdout.write(f'   Total de checklists para hoje: {total}')
                
                for stat in por_status:
                    self.stdout.write(f'   {stat["status"]}: {stat["total"]}')
            else:
                self.stdout.write('\n⚠️ Nenhum checklist foi criado para hoje')
                self.stdout.write('💡 Verifique se há equipamentos com frequência DIARIA configurada')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar resultados: {e}'))

    def _mostrar_status_detalhado(self):
        """Mostra status detalhado dos checklists"""
        self.stdout.write('\n📊 STATUS DETALHADO DOS CHECKLISTS')
        self.stdout.write('=' * 40)
        
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            from backend.apps.equipamentos.models import Equipamento
            
            hoje = date.today()
            ontem = hoje - timedelta(days=1)
            esta_semana_inicio = hoje - timedelta(days=hoje.weekday())
            este_mes_inicio = hoje.replace(day=1)
            
            # Estatísticas de hoje
            self._mostrar_stats_periodo('HOJE', hoje, hoje)
            
            # Estatísticas de ontem
            self._mostrar_stats_periodo('ONTEM', ontem, ontem)
            
            # Estatísticas desta semana
            self._mostrar_stats_periodo('ESTA SEMANA', esta_semana_inicio, hoje)
            
            # Estatísticas deste mês
            self._mostrar_stats_periodo('ESTE MÊS', este_mes_inicio, hoje)
            
            # Estatísticas de equipamentos
            self._mostrar_stats_equipamentos()
            
            # Próximos agendamentos
            self._mostrar_proximos_agendamentos()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao mostrar status: {e}'))

    def _mostrar_stats_periodo(self, titulo, data_inicio, data_fim):
        """Mostra estatísticas para um período"""
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            
            checklists = ChecklistNR12.objects.filter(
                data_checklist__range=[data_inicio, data_fim]
            )
            
            if not checklists.exists():
                self.stdout.write(f'\n📅 {titulo} ({data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m/%Y")}):')
                self.stdout.write('   Nenhum checklist encontrado')
                return
            
            total = checklists.count()
            por_status = checklists.values('status').annotate(total=Count('id'))
            por_turno = checklists.values('turno').annotate(total=Count('id'))
            
            self.stdout.write(f'\n📅 {titulo} ({data_inicio.strftime("%d/%m")} a {data_fim.strftime("%d/%m/%Y")}):')
            self.stdout.write(f'   📋 Total: {total} checklists')
            
            # Por status
            self.stdout.write('   📊 Por status:')
            for stat in por_status:
                porcentagem = (stat['total'] / total * 100) if total > 0 else 0
                icon = self._get_status_icon(stat['status'])
                self.stdout.write(f'      {icon} {stat["status"]}: {stat["total"]} ({porcentagem:.1f}%)')
            
            # Por turno
            self.stdout.write('   🕐 Por turno:')
            for turno in por_turno:
                self.stdout.write(f'      • {turno["turno"]}: {turno["total"]}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro nas estatísticas de {titulo}: {e}'))

    def _get_status_icon(self, status):
        """Retorna ícone para o status"""
        icons = {
            'PENDENTE': '🟡',
            'EM_ANDAMENTO': '🔵', 
            'CONCLUIDO': '🟢',
            'ATRASADO': '🔴',
            'CANCELADO': '⚫'
        }
        return icons.get(status, '⚪')

    def _mostrar_stats_equipamentos(self):
        """Mostra estatísticas dos equipamentos"""
        try:
            from backend.apps.equipamentos.models import Equipamento
            
            self.stdout.write('\n🔧 ESTATÍSTICAS DOS EQUIPAMENTOS:')
            self.stdout.write('-' * 35)
            
            # Equipamentos por status NR12
            total_eq = Equipamento.objects.count()
            ativos_nr12 = Equipamento.objects.filter(ativo_nr12=True).count()
            com_frequencia = Equipamento.objects.exclude(frequencias_checklist=[]).count()
            
            self.stdout.write(f'📊 Total de equipamentos: {total_eq}')
            self.stdout.write(f'✅ Ativos NR12: {ativos_nr12}')
            self.stdout.write(f'🔄 Com frequência configurada: {com_frequencia}')
            
            # Por frequência
            frequencias = ['DIARIA', 'SEMANAL', 'MENSAL']
            self.stdout.write('\n📅 Por frequência:')
            
            for freq in frequencias:
                count = Equipamento.objects.filter(
                    frequencias_checklist__contains=[freq]
                ).count()
                self.stdout.write(f'   • {freq}: {count} equipamentos')
            
            # Top 5 equipamentos com mais checklists
            self._mostrar_top_equipamentos()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro nas estatísticas de equipamentos: {e}'))

    def _mostrar_top_equipamentos(self):
        """Mostra equipamentos com mais checklists"""
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            from django.db.models import Count
            
            hoje = date.today()
            inicio_mes = hoje.replace(day=1)
            
            top_equipamentos = ChecklistNR12.objects.filter(
                data_checklist__range=[inicio_mes, hoje]
            ).values(
                'equipamento__nome'
            ).annotate(
                total=Count('id')
            ).order_by('-total')[:5]
            
            if top_equipamentos:
                self.stdout.write('\n🏆 Top 5 equipamentos (este mês):')
                for i, eq in enumerate(top_equipamentos, 1):
                    self.stdout.write(f'   {i}. {eq["equipamento__nome"]}: {eq["total"]} checklists')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no top equipamentos: {e}'))

    def _mostrar_proximos_agendamentos(self):
        """Mostra próximos agendamentos"""
        self.stdout.write('\n⏰ PRÓXIMOS AGENDAMENTOS:')
        self.stdout.write('-' * 25)
        
        agora = datetime.now()
        hoje = agora.date()
        amanha = hoje + timedelta(days=1)
        
        # Calcular próximos horários
        proximos = []
        
        # Próximo agendamento diário (6h)
        if agora.hour < 6:
            proximo_diario = datetime.combine(hoje, datetime.min.time().replace(hour=6))
        else:
            proximo_diario = datetime.combine(amanha, datetime.min.time().replace(hour=6))
        
        proximos.append(('Geração automática', proximo_diario, 'Checklists diários/semanais/mensais'))
        
        # Próximo agendamento de verificação (7h)
        if agora.hour < 7:
            proximo_verificacao = datetime.combine(hoje, datetime.min.time().replace(hour=7))
        else:
            proximo_verificacao = datetime.combine(amanha, datetime.min.time().replace(hour=7))
        
        proximos.append(('Verificação atrasados', proximo_verificacao, 'Marcar checklists atrasados'))
        
        # Próxima segunda-feira (relatório semanal)
        dias_para_segunda = (7 - hoje.weekday()) % 7
        if dias_para_segunda == 0 and agora.hour >= 7:
            dias_para_segunda = 7
        proxima_segunda = hoje + timedelta(days=dias_para_segunda)
        relatorio_semanal = datetime.combine(proxima_segunda, datetime.min.time().replace(hour=7, minute=30))
        
        proximos.append(('Relatório semanal', relatorio_semanal, 'Relatório de performance'))
        
        # Mostrar próximos agendamentos
        for nome, data_hora, descricao in proximos:
            delta = data_hora - agora
            if delta.days > 0:
                tempo_str = f'em {delta.days} dias'
            else:
                horas = delta.seconds // 3600
                minutos = (delta.seconds % 3600) // 60
                tempo_str = f'em {horas}h{minutos:02d}min'
            
            self.stdout.write(f'🕐 {nome}: {data_hora.strftime("%d/%m %H:%M")} ({tempo_str})')
            self.stdout.write(f'   {descricao}')

    def _executar_diagnostico_completo(self):
        """Executa diagnóstico completo do sistema"""
        self.stdout.write('\n🔍 DIAGNÓSTICO COMPLETO DO SISTEMA')
        self.stdout.write('=' * 42)
        
        # 1. Verificar modelos e dados
        self._diagnosticar_modelos()
        
        # 2. Verificar configurações
        self._diagnosticar_configuracoes()
        
        # 3. Verificar integridade
        self._diagnosticar_integridade()
        
        # 4. Verificar performance
        self._diagnosticar_performance()
        
        # 5. Recomendações
        self._gerar_recomendacoes()

    def _diagnosticar_modelos(self):
        """Diagnostica modelos e dados"""
        self.stdout.write('\n📊 DIAGNÓSTICO DE MODELOS E DADOS')
        self.stdout.write('-' * 35)
        
        try:
            from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12, TipoEquipamentoNR12, ItemChecklistPadrao
            from backend.apps.operadores.models import Operador
            
            modelos = [
                (CategoriaEquipamento, 'Categorias de equipamento'),
                (Equipamento, 'Equipamentos'),
                (TipoEquipamentoNR12, 'Tipos NR12'),
                (ItemChecklistPadrao, 'Itens padrão'),
                (ChecklistNR12, 'Checklists'),
                (Operador, 'Operadores'),
            ]
            
            for modelo, nome in modelos:
                try:
                    count = modelo.objects.count()
                    if count > 0:
                        self.stdout.write(f'✅ {nome}: {count} registros')
                    else:
                        self.stdout.write(f'⚠️ {nome}: Nenhum registro')
                except Exception as e:
                    self.stdout.write(f'❌ {nome}: Erro - {e}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no diagnóstico de modelos: {e}'))

    def _diagnosticar_configuracoes(self):
        """Diagnostica configurações do sistema"""
        self.stdout.write('\n⚙️ DIAGNÓSTICO DE CONFIGURAÇÕES')
        self.stdout.write('-' * 32)
        
        try:
            # Verificar configurações Django
            self.stdout.write('🔧 Configurações Django:')
            self.stdout.write(f'   • DEBUG: {settings.DEBUG}')
            self.stdout.write(f'   • TIMEZONE: {settings.TIME_ZONE}')
            
            # Verificar apps instalados
            apps_necessarios = [
                'backend.apps.core',
                'backend.apps.nr12_checklist',
                'backend.apps.equipamentos',
                'backend.apps.operadores',
                'celery',
                'django_filters',
            ]
            
            self.stdout.write('\n📦 Apps instalados:')
            for app in apps_necessarios:
                if app in settings.INSTALLED_APPS or app in sys.modules:
                    self.stdout.write(f'   ✅ {app}')
                else:
                    self.stdout.write(f'   ❌ {app}')
            
            # Verificar configurações do Celery
            try:
                from celery import current_app
                self.stdout.write('\n🔄 Configurações Celery:')
                self.stdout.write(f'   • Broker: {current_app.conf.broker_url}')
                self.stdout.write(f'   • Timezone: {current_app.conf.timezone}')
                self.stdout.write(f'   • Tasks: {len(current_app.conf.beat_schedule)} agendadas')
            except Exception as e:
                self.stdout.write(f'   ❌ Celery: {e}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no diagnóstico de configurações: {e}'))

    def _diagnosticar_integridade(self):
        """Diagnostica integridade dos dados"""
        self.stdout.write('\n🔍 DIAGNÓSTICO DE INTEGRIDADE')
        self.stdout.write('-' * 30)
        
        problemas = []
        
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado
            from backend.apps.equipamentos.models import Equipamento
            
            # 1. Equipamentos órfãos
            equipamentos_sem_categoria = Equipamento.objects.filter(categoria__isnull=True).count()
            if equipamentos_sem_categoria > 0:
                problemas.append(f'❌ {equipamentos_sem_categoria} equipamentos sem categoria')
            
            # 2. Checklists órfãos
            checklists_orfaos = ChecklistNR12.objects.filter(equipamento__isnull=True).count()
            if checklists_orfaos > 0:
                problemas.append(f'❌ {checklists_orfaos} checklists órfãos')
            
            # 3. Checklists sem itens
            checklists_sem_itens = ChecklistNR12.objects.filter(
                itens_realizados__isnull=True
            ).count()
            if checklists_sem_itens > 0:
                problemas.append(f'❌ {checklists_sem_itens} checklists sem itens')
            
            # 4. Equipamentos sem tipo NR12
            equipamentos_sem_tipo = Equipamento.objects.filter(
                ativo_nr12=True,
                tipo_nr12__isnull=True
            ).count()
            if equipamentos_sem_tipo > 0:
                problemas.append(f'⚠️ {equipamentos_sem_tipo} equipamentos NR12 sem tipo configurado')
            
            # Mostrar resultados
            if not problemas:
                self.stdout.write('✅ Integridade dos dados OK')
            else:
                self.stdout.write('⚠️ Problemas encontrados:')
                for problema in problemas:
                    self.stdout.write(f'   {problema}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no diagnóstico de integridade: {e}'))

    def _diagnosticar_performance(self):
        """Diagnostica performance do sistema"""
        self.stdout.write('\n⚡ DIAGNÓSTICO DE PERFORMANCE')
        self.stdout.write('-' * 30)
        
        try:
            from django.db import connection
            from django.core.cache import cache
            import time
            
            # Teste de consulta simples
            start_time = time.time()
            from backend.apps.equipamentos.models import Equipamento
            count = Equipamento.objects.count()
            query_time = (time.time() - start_time) * 1000
            
            self.stdout.write(f'🔍 Consulta simples: {query_time:.2f}ms ({count} equipamentos)')
            
            # Número de consultas
            queries_count = len(connection.queries)
            self.stdout.write(f'📊 Consultas executadas: {queries_count}')
            
            # Teste de cache (se configurado)
            try:
                cache.set('test_key', 'test_value', 10)
                cache_value = cache.get('test_key')
                if cache_value == 'test_value':
                    self.stdout.write('✅ Cache funcionando')
                else:
                    self.stdout.write('⚠️ Cache não funcionando corretamente')
            except Exception:
                self.stdout.write('⚠️ Cache não configurado')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no diagnóstico de performance: {e}'))

    def _gerar_recomendacoes(self):
        """Gera recomendações baseadas no diagnóstico"""
        self.stdout.write('\n💡 RECOMENDAÇÕES')
        self.stdout.write('-' * 15)
        
        recomendacoes = []
        
        try:
            from backend.apps.equipamentos.models import Equipamento
            
            # Verificar equipamentos sem frequência
            sem_frequencia = Equipamento.objects.filter(
                ativo_nr12=True,
                frequencias_checklist=[]
            ).count()
            
            if sem_frequencia > 0:
                recomendacoes.append(f'🔧 Configure frequências para {sem_frequencia} equipamentos')
                recomendacoes.append('   Execute: python manage.py configurar_automacao --inicial')
            
            # Verificar Celery
            try:
                from celery import current_app
                if not current_app.conf.beat_schedule:
                    recomendacoes.append('⏰ Configure agendamentos do Celery')
                    recomendacoes.append('   Verifique o arquivo backend/celery.py')
            except:
                recomendacoes.append('🔄 Instale e configure o Celery')
                recomendacoes.append('   Execute: pip install celery redis')
            
            # Verificar tipos NR12
            from backend.apps.nr12_checklist.models import TipoEquipamentoNR12
            if TipoEquipamentoNR12.objects.count() == 0:
                recomendacoes.append('📋 Crie tipos e itens padrão NR12')
                recomendacoes.append('   Execute: python manage.py criar_checklist')
            
            # Mostrar recomendações
            if recomendacoes:
                for rec in recomendacoes:
                    self.stdout.write(rec)
            else:
                self.stdout.write('✅ Sistema configurado corretamente!')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao gerar recomendações: {e}'))

    def _criar_dados_teste(self):
        """Cria dados de teste para validação"""
        self.stdout.write('\n🧪 CRIANDO DADOS DE TESTE')
        self.stdout.write('=' * 30)
        
        try:
            from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
            from backend.apps.clientes.models import Cliente
            from backend.apps.empreendimentos.models import Empreendimento
            from backend.apps.nr12_checklist.models import TipoEquipamentoNR12
            
            # 1. Criar categoria teste
            categoria, created = CategoriaEquipamento.objects.get_or_create(
                codigo='TEST',
                defaults={
                    'nome': 'Categoria Teste',
                    'descricao': 'Categoria para equipamentos de teste',
                    'prefixo_codigo': 'TEST',
                    'ativo': True
                }
            )
            if created:
                self.stdout.write('✅ Categoria teste criada')
            else:
                self.stdout.write('ℹ️ Categoria teste já existia')

            # 2. Criar cliente teste
            cliente, created = Cliente.objects.get_or_create(
                cnpj='12345678000100',
                defaults={
                    'razao_social': 'Cliente Teste Ltda',
                    'nome_fantasia': 'Cliente Teste',
                    'ativo': True
                }
            )
            if created:
                self.stdout.write('✅ Cliente teste criado')
            else:
                self.stdout.write('ℹ️ Cliente teste já existia')
            
            # 2.1. Criar empreendimento teste
            empreendimento, created = Empreendimento.objects.get_or_create(
                nome='Empreendimento Teste',
                defaults={
                    'descricao': 'Empreendimento para testes de automação',
                    'cliente': cliente,
                    'endereco': 'Rua Teste, 123',
                    'cidade': 'Cidade Teste',
                    'estado': 'SP',
                    'distancia_km': 10.5,  # Campo obrigatório
                    'ativo': True
                }
            )
            if created:
                self.stdout.write('✅ Empreendimento teste criado')
            else:
                self.stdout.write('ℹ️ Empreendimento teste já existia')
            
            # 3. Criar tipo NR12 teste
            tipo_nr12, created = TipoEquipamentoNR12.objects.get_or_create(
                nome='Equipamento Teste',
                defaults={'descricao': 'Tipo de equipamento para testes de automação'}
            )
            if created:
                self.stdout.write('✅ Tipo NR12 teste criado')
            else:
                self.stdout.write('ℹ️ Tipo NR12 teste já existia')
            
            # 4. Criar equipamentos teste
            equipamentos_teste = [
                ('Equipamento Teste Diário', ['DIARIA']),
                ('Equipamento Teste Semanal', ['SEMANAL']),
                ('Equipamento Teste Mensal', ['MENSAL']),
                ('Equipamento Teste Completo', ['DIARIA', 'SEMANAL', 'MENSAL']),
            ]
            
            equipamentos_criados = 0
            equipamentos_atualizados = 0
            
            for nome, frequencias in equipamentos_teste:
                # Verificar se já existe por nome
                equipamento, created = Equipamento.objects.get_or_create(
                    nome=nome,
                    cliente=cliente,  # Adicionar na busca para evitar duplicação
                    defaults={
                        'descricao': f'Equipamento de teste para automação - Frequência: {", ".join(frequencias)}',
                        'categoria': categoria,
                        'empreendimento': empreendimento,
                        'tipo_nr12': tipo_nr12,
                        'ativo': True,
                        'ativo_nr12': True,
                        'frequencias_checklist': frequencias,
                        'marca': 'Teste',
                        'modelo': 'Automação',
                        'status': 'OPERACIONAL',
                        'status_operacional': 'DISPONIVEL',
                        'horimetro_atual': 0.0
                    }
                )
                
                if created:
                    equipamentos_criados += 1
                    self.stdout.write(f'✅ {nome} criado com código: {equipamento.codigo}')
                else:
                    # Atualizar frequências se já existir
                    equipamento.frequencias_checklist = frequencias
                    equipamento.ativo_nr12 = True
                    equipamento.tipo_nr12 = tipo_nr12
                    equipamento.save()
                    equipamentos_atualizados += 1
                    self.stdout.write(f'🔄 {nome} atualizado com código: {equipamento.codigo}')
            
            # 5. Criar itens padrão se não existirem
            self._criar_itens_padrao_teste(tipo_nr12)
            
            # Resumo
            self.stdout.write('\n📊 RESUMO DOS DADOS DE TESTE:')
            self.stdout.write(f'   📋 Categoria: {categoria.nome}')
            self.stdout.write(f'   👤 Cliente: {cliente.razao_social}')
            self.stdout.write(f'   🏗️ Empreendimento: {empreendimento.nome}')
            self.stdout.write(f'   📝 Tipo NR12: {tipo_nr12.nome}')
            self.stdout.write(f'   🔧 Equipamentos criados: {equipamentos_criados}')
            self.stdout.write(f'   🔄 Equipamentos atualizados: {equipamentos_atualizados}')
            
            self.stdout.write('\n🎉 Dados de teste criados com sucesso!')
            self.stdout.write('💡 Agora você pode testar a automação com: --testar')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar dados de teste: {e}'))
            import traceback
            self.stdout.write(f'📝 Detalhes do erro:\n{traceback.format_exc()}')

    def _criar_itens_padrao_teste(self, tipo_nr12):
        """Cria itens padrão de teste para o tipo NR12"""
        try:
            from backend.apps.nr12_checklist.models import ItemChecklistPadrao
            
            # Verificar se já existem itens
            if ItemChecklistPadrao.objects.filter(tipo_equipamento=tipo_nr12).exists():
                self.stdout.write('ℹ️ Itens padrão já existem para o tipo teste')
                return
            
            # Criar itens básicos de teste
            itens_teste = [
                ('Verificar nível do óleo do motor', 'Conferir nível do óleo', 'CRITICA', 1),
                ('Verificar sistema de freios', 'Testar funcionamento dos freios', 'CRITICA', 2),
                ('Verificar pneus/esteiras', 'Inspecionar estado dos pneus', 'ALTA', 3),
                ('Verificar luzes de sinalização', 'Testar faróis e sinalizadores', 'MEDIA', 4),
                ('Verificar buzina', 'Testar sinal sonoro', 'MEDIA', 5),
            ]
            
            itens_criados = 0
            for item, descricao, criticidade, ordem in itens_teste:
                ItemChecklistPadrao.objects.create(
                    tipo_equipamento=tipo_nr12,
                    item=item,
                    descricao=descricao,
                    criticidade=criticidade,
                    ordem=ordem,
                    ativo=True
                )
                itens_criados += 1
            
            self.stdout.write(f'✅ {itens_criados} itens padrão criados para testes')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Erro ao criar itens padrão: {e}'))

    def _mostrar_proximos_passos(self):
        """Mostra próximos passos após configuração"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ CONFIGURAÇÃO INICIAL CONCLUÍDA'))
        self.stdout.write('=' * 70)
        
        self.stdout.write('\n🚀 PRÓXIMOS PASSOS PARA ATIVAR A AUTOMAÇÃO:')
        self.stdout.write('\n1. 🔧 Configure frequências dos equipamentos:')
        self.stdout.write('   • Acesse /admin/equipamentos/equipamento/')
        self.stdout.write('   • Para cada equipamento, marque: DIARIA, SEMANAL ou MENSAL')
        self.stdout.write('   • Ou use: python manage.py configurar_automacao --equipamento-id X --frequencias DIARIA')
        
        self.stdout.write('\n2. 🔄 Inicie os serviços do Celery:')
        self.stdout.write('   • Terminal 1: celery -A backend worker -l info')
        self.stdout.write('   • Terminal 2: celery -A backend beat -l info')
        
        self.stdout.write('\n3. 🧪 Teste a automação:')
        self.stdout.write('   • python manage.py configurar_automacao --testar')
        
        self.stdout.write('\n4. 📊 Monitore o sistema:')
        self.stdout.write('   • python manage.py configurar_automacao --status')
        self.stdout.write('   • python manage.py configurar_automacao --diagnostico')
        
        self.stdout.write('\n⏰ AGENDAMENTOS AUTOMÁTICOS CONFIGURADOS:')
        self.stdout.write('• 6h00: Gerar checklists (diário/semanal/mensal)')
        self.stdout.write('• 7h00: Verificar checklists atrasados')
        self.stdout.write('• 8h-18h (a cada 2h): Notificar checklists pendentes')
        self.stdout.write('• Segunda 7h30: Relatório semanal')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Sistema pronto para automação completa!'))