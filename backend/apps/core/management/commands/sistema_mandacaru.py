# ================================================================
# ARQUIVO: backend/apps/core/management/commands/sistema_mandacaru.py
# Comandos principais para manutenção do sistema
# ================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Count, Sum
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Comandos principais para manutenção do sistema Mandacaru ERP'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'acao',
            choices=[
                'status',
                'inicializar',
                'backup',
                'limpeza',
                'diagnostico',
                'resetar_demo',
                'gerar_dados_teste',
                'verificar_integridade'
            ],
            help='Ação a ser executada'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a execução sem confirmação'
        )
        
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de dias para operações de limpeza/backup'
        )
    
    def handle(self, *args, **options):
        acao = options['acao']
        
        self.stdout.write(f"🚀 Executando: {acao.upper()}")
        self.stdout.write("=" * 50)
        
        try:
            if acao == 'status':
                self._mostrar_status()
            elif acao == 'inicializar':
                self._inicializar_sistema(options['force'])
            elif acao == 'backup':
                self._fazer_backup(options['dias'])
            elif acao == 'limpeza':
                self._limpeza_sistema(options['dias'], options['force'])
            elif acao == 'diagnostico':
                self._diagnostico_completo()
            elif acao == 'resetar_demo':
                self._resetar_dados_demo(options['force'])
            elif acao == 'gerar_dados_teste':
                self._gerar_dados_teste()
            elif acao == 'verificar_integridade':
                self._verificar_integridade()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro: {str(e)}")
            )
            raise
    
    def _mostrar_status(self):
        """Mostra status geral do sistema"""
        self.stdout.write("📊 STATUS DO SISTEMA")
        self.stdout.write("-" * 30)
        
        # Status dos apps principais
        apps_status = self._verificar_apps()
        for app, status in apps_status.items():
            icon = "✅" if status['ok'] else "❌"
            self.stdout.write(f"{icon} {app}: {status['info']}")
        
        # Estatísticas gerais
        self.stdout.write("\n📈 ESTATÍSTICAS GERAIS")
        self.stdout.write("-" * 30)
        
        stats = self._obter_estatisticas_gerais()
        for categoria, dados in stats.items():
            self.stdout.write(f"🔹 {categoria}:")
            for item, valor in dados.items():
                self.stdout.write(f"   • {item}: {valor}")
    
    def _verificar_apps(self):
        """Verifica status dos apps principais"""
        status = {}
        
        try:
            from backend.apps.equipamentos.models import Equipamento
            total_eq = Equipamento.objects.count()
            status['Equipamentos'] = {
                'ok': True, 
                'info': f"{total_eq} equipamentos cadastrados"
            }
        except Exception as e:
            status['Equipamentos'] = {'ok': False, 'info': f"Erro: {e}"}
        
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            hoje = date.today()
            checklists_hoje = ChecklistNR12.objects.filter(data_checklist=hoje).count()
            status['Checklists NR12'] = {
                'ok': True,
                'info': f"{checklists_hoje} checklists hoje"
            }
        except Exception as e:
            status['Checklists NR12'] = {'ok': False, 'info': f"Erro: {e}"}
        
        try:
            from backend.apps.clientes.models import Cliente
            total_clientes = Cliente.objects.count()
            status['Clientes'] = {
                'ok': True,
                'info': f"{total_clientes} clientes cadastrados"
            }
        except Exception as e:
            status['Clientes'] = {'ok': False, 'info': f"Erro: {e}"}
        
        try:
            from backend.apps.dashboard.models import KPISnapshot
            ultimo_kpi = KPISnapshot.objects.last()
            if ultimo_kpi:
                dias_atras = (date.today() - ultimo_kpi.data_snapshot).days
                status['Dashboard'] = {
                    'ok': dias_atras <= 1,
                    'info': f"Último KPI: {dias_atras} dia(s) atrás"
                }
            else:
                status['Dashboard'] = {'ok': False, 'info': 'Nenhum KPI registrado'}
        except Exception as e:
            status['Dashboard'] = {'ok': False, 'info': f"Erro: {e}"}
        
        return status
    
    def _obter_estatisticas_gerais(self):
        """Obtém estatísticas gerais do sistema"""
        stats = {}
        
        try:
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12, AlertaManutencao
            from backend.apps.almoxarifado.models import Produto
            from backend.apps.financeiro.models import ContaFinanceira
            
            hoje = date.today()
            
            # Equipamentos
            equipamentos = Equipamento.objects.all()
            stats['Equipamentos'] = {
                'Total': equipamentos.count(),
                'Ativos NR12': equipamentos.filter(ativo_nr12=True).count(),
                'Tipos únicos': equipamentos.values('categoria').distinct().count()
            }
            
            # Checklists
            checklists = ChecklistNR12.objects.filter(data_checklist=hoje)
            stats['Checklists (Hoje)'] = {
                'Total': checklists.count(),
                'Pendentes': checklists.filter(status='PENDENTE').count(),
                'Concluídos': checklists.filter(status='CONCLUIDO').count(),
                'Com problemas': checklists.filter(necessita_manutencao=True).count()
            }
            
            # Alertas
            alertas = AlertaManutencao.objects.filter(status__in=['ATIVO', 'NOTIFICADO'])
            stats['Alertas'] = {
                'Ativos': alertas.count(),
                'Críticos': alertas.filter(criticidade='CRITICA').count(),
                'Vencidos': alertas.filter(data_prevista__lt=hoje).count()
            }
            
            # Estoque
            produtos = Produto.objects.all()
            stats['Estoque'] = {
                'Produtos': produtos.count(),
                'Estoque baixo': produtos.filter(estoque_atual__lt=5).count(),
                'Zerados': produtos.filter(estoque_atual=0).count()
            }
            
            # Financeiro
            contas = ContaFinanceira.objects.all()
            vencidas = contas.filter(status='VENCIDO').aggregate(
                total=Sum('valor_restante')
            )['total'] or 0
            
            stats['Financeiro'] = {
                'Contas abertas': contas.filter(status__in=['PENDENTE', 'VENCIDO']).count(),
                'Valor vencido': f"R$ {vencidas:,.2f}",
                'Faturamento mês': self._calcular_faturamento_mes()
            }
            
        except Exception as e:
            stats['Erro'] = {'Mensagem': str(e)}
        
        return stats
    
    def _calcular_faturamento_mes(self):
        """Calcula faturamento do mês atual"""
        try:
            from backend.apps.financeiro.models import ContaFinanceira
            
            hoje = date.today()
            inicio_mes = hoje.replace(day=1)
            
            faturamento = ContaFinanceira.objects.filter(
                tipo='RECEBER',
                status='PAGO',
                data_pagamento__range=[inicio_mes, hoje]
            ).aggregate(total=Sum('valor_pago'))['total'] or 0
            
            return f"R$ {faturamento:,.2f}"
        except:
            return "Erro no cálculo"
    
    def _inicializar_sistema(self, force=False):
        """Inicializa o sistema com dados básicos"""
        self.stdout.write("🔧 INICIALIZANDO SISTEMA")
        self.stdout.write("-" * 30)
        
        if not force:
            resposta = input("⚠️ Isso criará dados básicos. Continuar? (s/N): ")
            if resposta.lower() != 's':
                self.stdout.write("❌ Operação cancelada")
                return
        
        # 1. Criar categorias de equipamentos
        self.stdout.write("1️⃣ Criando categorias de equipamentos...")
        try:
            from backend.apps.equipamentos.models import criar_categorias_mandacaru
            criar_categorias_mandacaru()
            self.stdout.write("   ✅ Categorias criadas")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro: {e}")
        
        # 2. Criar tipos NR12
        self.stdout.write("2️⃣ Criando tipos e itens NR12...")
        try:
            from backend.apps.nr12_checklist.models import criar_tipos_nr12_mandacaru
            criar_tipos_nr12_mandacaru()
            self.stdout.write("   ✅ Tipos NR12 criados")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro: {e}")
        
        # 3. Criar usuário admin se não existir
        self.stdout.write("3️⃣ Verificando usuário admin...")
        try:
            from backend.apps.auth_cliente.models import UsuarioCliente
            if not UsuarioCliente.objects.filter(is_superuser=True).exists():
                admin = UsuarioCliente.objects.create_superuser(
                    username='admin',
                    email='admin@mandacaru.com',
                    password='admin123',
                    first_name='Administrador',
                    last_name='Mandacaru'
                )
                self.stdout.write("   ✅ Usuário admin criado (admin/admin123)")
            else:
                self.stdout.write("   ℹ️ Usuário admin já existe")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro: {e}")
        
        # 4. Calcular KPIs iniciais
        self.stdout.write("4️⃣ Calculando KPIs iniciais...")
        try:
            from backend.apps.dashboard.models import KPISnapshot
            KPISnapshot.calcular_kpis_hoje()
            self.stdout.write("   ✅ KPIs calculados")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro: {e}")
        
        self.stdout.write("\n🎉 Sistema inicializado com sucesso!")
    
    def _fazer_backup(self, dias):
        """Faz backup dos dados importantes"""
        self.stdout.write(f"💾 FAZENDO BACKUP ({dias} dias)")
        self.stdout.write("-" * 30)
        
        try:
            from django.core import serializers
            import json
            import os
            from datetime import datetime
            
            # Criar diretório de backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"backups/{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup de modelos principais
            modelos_backup = [
                ('clientes', 'backend.apps.clientes.models.Cliente'),
                ('equipamentos', 'backend.apps.equipamentos.models.Equipamento'),
                ('categorias_eq', 'backend.apps.equipamentos.models.CategoriaEquipamento'),
                ('tipos_nr12', 'backend.apps.nr12_checklist.models.TipoEquipamentoNR12'),
                ('itens_checklist', 'backend.apps.nr12_checklist.models.ItemChecklistPadrao'),
                ('usuarios', 'backend.apps.auth_cliente.models.UsuarioCliente'),
            ]
            
            # Backup dos últimos N dias
            data_limite = date.today() - timedelta(days=dias)
            modelos_recentes = [
                ('checklists', 'backend.apps.nr12_checklist.models.ChecklistNR12', 'data_checklist'),
                ('alertas', 'backend.apps.nr12_checklist.models.AlertaManutencao', 'data_identificacao'),
                ('kpis', 'backend.apps.dashboard.models.KPISnapshot', 'data_snapshot'),
            ]
            
            arquivos_criados = 0
            
            # Backup dos modelos principais
            for nome, model_path in modelos_backup:
                try:
                    module_name, class_name = model_path.rsplit('.', 1)
                    module = __import__(module_name, fromlist=[class_name])
                    model_class = getattr(module, class_name)
                    
                    data = serializers.serialize('json', model_class.objects.all())
                    
                    with open(f"{backup_dir}/{nome}.json", 'w', encoding='utf-8') as f:
                        f.write(data)
                    
                    count = model_class.objects.count()
                    self.stdout.write(f"   ✅ {nome}: {count} registros")
                    arquivos_criados += 1
                    
                except Exception as e:
                    self.stdout.write(f"   ❌ {nome}: {e}")
            
            # Backup dos dados recentes
            for nome, model_path, date_field in modelos_recentes:
                try:
                    module_name, class_name = model_path.rsplit('.', 1)
                    module = __import__(module_name, fromlist=[class_name])
                    model_class = getattr(module, class_name)
                    
                    filter_kwargs = {f"{date_field}__gte": data_limite}
                    queryset = model_class.objects.filter(**filter_kwargs)
                    data = serializers.serialize('json', queryset)
                    
                    with open(f"{backup_dir}/{nome}_recentes.json", 'w', encoding='utf-8') as f:
                        f.write(data)
                    
                    count = queryset.count()
                    self.stdout.write(f"   ✅ {nome} (últimos {dias} dias): {count} registros")
                    arquivos_criados += 1
                    
                except Exception as e:
                    self.stdout.write(f"   ❌ {nome}: {e}")
            
            # Salvar metadados do backup
            metadata = {
                'data_backup': datetime.now().isoformat(),
                'dias_incluidos': dias,
                'arquivos_criados': arquivos_criados,
                'versao_sistema': '1.0.0'
            }
            
            with open(f"{backup_dir}/metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.stdout.write(f"\n💾 Backup concluído em: {backup_dir}")
            self.stdout.write(f"📁 {arquivos_criados} arquivos criados")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro no backup: {e}")
            raise
    
    def _limpeza_sistema(self, dias, force=False):
        """Limpa dados antigos do sistema"""
        self.stdout.write(f"🧹 LIMPEZA DO SISTEMA (>{dias} dias)")
        self.stdout.write("-" * 30)
        
        if not force:
            resposta = input(f"⚠️ Isso removerá dados com mais de {dias} dias. Continuar? (s/N): ")
            if resposta.lower() != 's':
                self.stdout.write("❌ Operação cancelada")
                return
        
        data_corte = date.today() - timedelta(days=dias)
        removidos_total = 0
        
        # Limpar alertas do dashboard inativos
        try:
            from backend.apps.dashboard.models import AlertaDashboard
            removidos = AlertaDashboard.objects.filter(
                ativo=False,
                criado_em__date__lt=data_corte
            ).delete()[0]
            self.stdout.write(f"   🗑️ Alertas dashboard inativos: {removidos}")
            removidos_total += removidos
        except Exception as e:
            self.stdout.write(f"   ❌ Erro alertas dashboard: {e}")
        
        # Limpar KPIs muito antigos (manter 1 ano)
        try:
            from backend.apps.dashboard.models import KPISnapshot
            data_corte_kpi = date.today() - timedelta(days=365)
            removidos = KPISnapshot.objects.filter(
                data_snapshot__lt=data_corte_kpi
            ).delete()[0]
            self.stdout.write(f"   🗑️ KPIs antigos (>1 ano): {removidos}")
            removidos_total += removidos
        except Exception as e:
            self.stdout.write(f"   ❌ Erro KPIs: {e}")
        
        # Limpar logs de sistema (se existirem)
        try:
            import os
            import glob
            
            log_files = glob.glob("logs/*.log")
            for log_file in log_files:
                try:
                    stat = os.stat(log_file)
                    file_date = date.fromtimestamp(stat.st_mtime)
                    if file_date < data_corte:
                        os.remove(log_file)
                        self.stdout.write(f"   🗑️ Log removido: {log_file}")
                        removidos_total += 1
                except Exception:
                    pass
        except Exception as e:
            self.stdout.write(f"   ❌ Erro logs: {e}")
        
        self.stdout.write(f"\n🧹 Limpeza concluída: {removidos_total} itens removidos")
    
    def _diagnostico_completo(self):
        """Executa diagnóstico completo do sistema"""
        self.stdout.write("🔍 DIAGNÓSTICO COMPLETO")
        self.stdout.write("-" * 30)
        
        # 1. Verificar integridade do banco
        self.stdout.write("1️⃣ Verificando integridade do banco...")
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write("   ✅ Conexão com banco OK")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro no banco: {e}")
        
        # 2. Verificar migrações pendentes
        self.stdout.write("2️⃣ Verificando migrações...")
        try:
            from django.core.management import call_command
            from io import StringIO
            
            output = StringIO()
            call_command('showmigrations', '--plan', stdout=output)
            migracoes_output = output.getvalue()
            
            if '[ ]' in migracoes_output:
                self.stdout.write("   ⚠️ Existem migrações pendentes")
                self.stdout.write("   💡 Execute: python manage.py migrate")
            else:
                self.stdout.write("   ✅ Todas as migrações aplicadas")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro nas migrações: {e}")
        
        # 3. Verificar permissões de arquivos
        self.stdout.write("3️⃣ Verificando permissões...")
        try:
            import os
            
            diretorios_verificar = ['media', 'staticfiles', 'logs']
            for diretorio in diretorios_verificar:
                if os.path.exists(diretorio):
                    if os.access(diretorio, os.W_OK):
                        self.stdout.write(f"   ✅ {diretorio}: escrita OK")
                    else:
                        self.stdout.write(f"   ❌ {diretorio}: sem permissão de escrita")
                else:
                    self.stdout.write(f"   ⚠️ {diretorio}: não existe")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro nas permissões: {e}")
        
        # 4. Verificar configurações críticas
        self.stdout.write("4️⃣ Verificando configurações...")
        try:
            from django.conf import settings
            
            configs_criticas = [
                ('SECRET_KEY', 'unsafe-secret-key'),
                ('DEBUG', True),
                ('ALLOWED_HOSTS', []),
            ]
            
            for config, valor_inseguro in configs_criticas:
                valor_atual = getattr(settings, config, None)
                
                if config == 'SECRET_KEY' and valor_atual == valor_inseguro:
                    self.stdout.write(f"   ⚠️ {config}: usando valor padrão (inseguro)")
                elif config == 'DEBUG' and valor_atual == valor_inseguro:
                    self.stdout.write(f"   ⚠️ DEBUG ativo em produção")
                elif config == 'ALLOWED_HOSTS' and not valor_atual:
                    self.stdout.write(f"   ⚠️ ALLOWED_HOSTS vazio")
                else:
                    self.stdout.write(f"   ✅ {config}: configurado")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro nas configurações: {e}")
        
        # 5. Verificar recursos do sistema
        self.stdout.write("5️⃣ Verificando recursos do sistema...")
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = "✅" if cpu_percent < 80 else "⚠️" if cpu_percent < 95 else "❌"
            self.stdout.write(f"   {cpu_status} CPU: {cpu_percent}%")
            
            # Memória
            memory = psutil.virtual_memory()
            mem_status = "✅" if memory.percent < 80 else "⚠️" if memory.percent < 95 else "❌"
            self.stdout.write(f"   {mem_status} Memória: {memory.percent}%")
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_status = "✅" if disk.percent < 80 else "⚠️" if disk.percent < 95 else "❌"
            self.stdout.write(f"   {disk_status} Disco: {disk.percent}%")
            
        except ImportError:
            self.stdout.write("   ℹ️ psutil não instalado - instale com: pip install psutil")
        except Exception as e:
            self.stdout.write(f"   ❌ Erro nos recursos: {e}")
        
        self.stdout.write("\n🔍 Diagnóstico concluído")
    
    def _resetar_dados_demo(self, force=False):
        """Reseta dados para demonstração"""
        self.stdout.write("🔄 RESETAR DADOS DEMO")
        self.stdout.write("-" * 30)
        
        if not force:
            resposta = input("⚠️ Isso removerá TODOS os dados. Continuar? (s/N): ")
            if resposta.lower() != 's':
                self.stdout.write("❌ Operação cancelada")
                return
        
        try:
            # Limpar dados principais (manter estrutura)
            from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado, AlertaManutencao
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.clientes.models import Cliente
            from backend.apps.empreendimentos.models import Empreendimento
            from backend.apps.financeiro.models import ContaFinanceira
            from backend.apps.almoxarifado.models import MovimentacaoEstoque
            from backend.apps.dashboard.models import AlertaDashboard, KPISnapshot
            
            # Remover dados transacionais
            modelos_limpar = [
                (ItemChecklistRealizado, "Itens de checklist"),
                (ChecklistNR12, "Checklists"),
                (AlertaManutencao, "Alertas de manutenção"),
                (MovimentacaoEstoque, "Movimentações estoque"),
                (ContaFinanceira, "Contas financeiras"),
                (AlertaDashboard, "Alertas dashboard"),
                (KPISnapshot, "KPIs"),
                (Equipamento, "Equipamentos"),
                (Empreendimento, "Empreendimentos"),
                (Cliente, "Clientes"),
            ]
            
            total_removido = 0
            for modelo, nome in modelos_limpar:
                count = modelo.objects.count()
                modelo.objects.all().delete()
                self.stdout.write(f"   🗑️ {nome}: {count} removidos")
                total_removido += count
            
            self.stdout.write(f"\n🔄 Reset concluído: {total_removido} registros removidos")
            self.stdout.write("💡 Execute 'inicializar' para recriar dados básicos")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro no reset: {e}")
            raise
    
    def _gerar_dados_teste(self):
        """Gera dados de teste para demonstração"""
        self.stdout.write("🎭 GERANDO DADOS DE TESTE")
        self.stdout.write("-" * 30)
        
        try:
            # Importar factories ou criar dados manualmente
            self._criar_cliente_teste()
            self._criar_equipamentos_teste()
            self._criar_checklists_teste()
            
            self.stdout.write("\n🎭 Dados de teste criados com sucesso!")
            
        except Exception as e:
            self.stdout.write(f"❌ Erro ao gerar dados: {e}")
            raise
    
    def _criar_cliente_teste(self):
        """Cria cliente de teste"""
        from backend.apps.clientes.models import Cliente
        from backend.apps.empreendimentos.models import Empreendimento
        
        cliente, created = Cliente.objects.get_or_create(
            cnpj='12.345.678/0001-90',
            defaults={
                'razao_social': 'Empresa Demo Ltda',
                'nome_fantasia': 'Demo Corp',
                'email': 'contato@demo.com',
                'telefone': '(11) 99999-9999',
                'rua': 'Rua das Demos, 123',
                'numero': '123',
                'bairro': 'Centro',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01234-567'
            }
        )
        
        empreendimento, created = Empreendimento.objects.get_or_create(
            cliente=cliente,
            nome='Obra Demo',
            defaults={
                'descricao': 'Empreendimento para demonstração',
                'endereco': 'Avenida dos Testes, 456',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01234-567',
                'distancia_km': 25.5
            }
        )
        
        self.stdout.write("   ✅ Cliente e empreendimento demo criados")
        return cliente, empreendimento
    
    def _criar_equipamentos_teste(self):
        """Cria equipamentos de teste"""
        from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
        from backend.apps.nr12_checklist.models import TipoEquipamentoNR12
        from backend.apps.clientes.models import Cliente
        from backend.apps.empreendimentos.models import Empreendimento
        
        cliente = Cliente.objects.first()
        empreendimento = Empreendimento.objects.first()
        
        if not cliente or not empreendimento:
            self.stdout.write("   ⚠️ Cliente/empreendimento não encontrado")
            return
        
        # Buscar ou criar categoria
        categoria, _ = CategoriaEquipamento.objects.get_or_create(
            codigo='ESC',
            defaults={
                'nome': 'Escavadeiras',
                'prefixo_codigo': 'ESC',
                'descricao': 'Escavadeiras hidráulicas'
            }
        )
        
        # Buscar tipo NR12
        tipo_nr12 = TipoEquipamentoNR12.objects.filter(
            nome__icontains='escavadeira'
        ).first()
        
        # Criar equipamentos de teste
        equipamentos_teste = [
            {
                'nome': 'Escavadeira CAT 320',
                'marca': 'Caterpillar',
                'modelo': '320D',
                'n_serie': 'CAT001'
            },
            {
                'nome': 'Escavadeira Volvo EC160',
                'marca': 'Volvo',
                'modelo': 'EC160E',
                'n_serie': 'VOL001'
            }
        ]
        
        for eq_data in equipamentos_teste:
            equipamento, created = Equipamento.objects.get_or_create(
                n_serie=eq_data['n_serie'],
                defaults={
                    'nome': eq_data['nome'],
                    'categoria': categoria,
                    'marca': eq_data['marca'],
                    'modelo': eq_data['modelo'],
                    'cliente': cliente,
                    'empreendimento': empreendimento,
                    'ativo_nr12': True,
                    'frequencia_checklist': 'DIARIO',
                    'tipo_nr12': tipo_nr12,
                    'horimetro': 1250.5
                }
            )
            
            if created:
                self.stdout.write(f"   ✅ Equipamento criado: {eq_data['nome']}")
    
    def _criar_checklists_teste(self):
        """Cria checklists de teste"""
        from backend.apps.nr12_checklist.models import ChecklistNR12
        from backend.apps.equipamentos.models import Equipamento
        import uuid
        
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        
        if not equipamentos.exists():
            self.stdout.write("   ⚠️ Nenhum equipamento NR12 encontrado")
            return
        
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        
        turnos = ['MANHA', 'TARDE']
        checklists_criados = 0
        
        for equipamento in equipamentos[:2]:  # Apenas 2 equipamentos
            for data in [ontem, hoje]:
                for turno in turnos:
                    checklist, created = ChecklistNR12.objects.get_or_create(
                        equipamento=equipamento,
                        data_checklist=data,
                        turno=turno,
                        defaults={
                            'status': 'PENDENTE' if data == hoje else 'CONCLUIDO',
                            'uuid': uuid.uuid4(),
                            'necessita_manutencao': False
                        }
                    )
                    
                    if created:
                        checklists_criados += 1
        
        self.stdout.write(f"   ✅ {checklists_criados} checklists de teste criados")
    
    def _verificar_integridade(self):
        """Verifica integridade dos dados"""
        self.stdout.write("🔍 VERIFICAÇÃO DE INTEGRIDADE")
        self.stdout.write("-" * 30)
        
        problemas = []
        
        # 1. Equipamentos sem categoria
        try:
            from backend.apps.equipamentos.models import Equipamento
            sem_categoria = Equipamento.objects.filter(categoria__isnull=True)
            if sem_categoria.exists():
                problemas.append(f"❌ {sem_categoria.count()} equipamentos sem categoria")
            else:
                self.stdout.write("   ✅ Todos equipamentos têm categoria")
        except Exception as e:
            problemas.append(f"❌ Erro ao verificar categorias: {e}")
        
        # 2. Checklists órfãos
        try:
            from backend.apps.nr12_checklist.models import ChecklistNR12
            orfaos = ChecklistNR12.objects.filter(equipamento__isnull=True)
            if orfaos.exists():
                problemas.append(f"❌ {orfaos.count()} checklists órfãos")
            else:
                self.stdout.write("   ✅ Todos checklists têm equipamento")
        except Exception as e:
            problemas.append(f"❌ Erro ao verificar checklists: {e}")
        
        # 3. Usuários sem cliente
        try:
            from backend.apps.auth_cliente.models import UsuarioCliente
            sem_cliente = UsuarioCliente.objects.filter(
                cliente__isnull=True,
                is_staff=False
            )
            if sem_cliente.exists():
                problemas.append(f"❌ {sem_cliente.count()} usuários sem cliente")
            else:
                self.stdout.write("   ✅ Usuários organizados corretamente")
        except Exception as e:
            problemas.append(f"❌ Erro ao verificar usuários: {e}")
        
        # Mostrar problemas encontrados
        if problemas:
            self.stdout.write("\n⚠️ PROBLEMAS ENCONTRADOS:")
            for problema in problemas:
                self.stdout.write(f"   {problema}")
        else:
            self.stdout.write("\n✅ Nenhum problema de integridade encontrado")
        
        return len(problemas) == 0