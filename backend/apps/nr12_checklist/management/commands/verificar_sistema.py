# ===============================================
# ARQUIVO: backend/apps/nr12_checklist/management/commands/verificar_sistema.py
# Comando para verificar integridade completa do sistema - CORRIGIDO
# ===============================================

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.utils import timezone
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Verifica integridade completa do sistema NR12 e Bot'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrigir problemas encontrados automaticamente'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Saída detalhada'
        )
        parser.add_argument(
            '--categoria',
            type=str,
            choices=['operadores', 'equipamentos', 'checklists', 'qrcodes', 'api', 'bot'],
            help='Verificar apenas uma categoria específica'
        )
    
    def handle(self, *args, **options):
        self.fix_mode = options['fix']
        self.verbose = options['verbose']
        self.categoria = options['categoria']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 VERIFICAÇÃO COMPLETA DO SISTEMA MANDACARU')
        )
        self.stdout.write('=' * 60)
        
        # Contadores de problemas
        self.problemas_encontrados = 0
        self.problemas_corrigidos = 0
        
        try:
            if not self.categoria or self.categoria == 'operadores':
                self._verificar_operadores()
            
            if not self.categoria or self.categoria == 'equipamentos':
                self._verificar_equipamentos()
            
            if not self.categoria or self.categoria == 'checklists':
                self._verificar_checklists()
            
            if not self.categoria or self.categoria == 'qrcodes':
                self._verificar_qr_codes()
            
            if not self.categoria or self.categoria == 'api':
                self._verificar_apis()
            
            if not self.categoria or self.categoria == 'bot':
                self._verificar_bot_integration()
            
            self._resumo_final()
            
        except Exception as e:
            raise CommandError(f'Erro durante verificação: {e}')
    
    def _verificar_operadores(self):
        """Verifica consistência dos operadores"""
        self.stdout.write('\n👥 VERIFICANDO OPERADORES')
        self.stdout.write('-' * 40)
        
        from backend.apps.operadores.models import Operador
        
        # 1. Operadores sem chat_id único
        operadores_chat_duplicado = Operador.objects.filter(
            chat_id_telegram__isnull=False
        ).exclude(chat_id_telegram='').values('chat_id_telegram').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        if operadores_chat_duplicado:
            self._reportar_problema(
                f"📱 {operadores_chat_duplicado.count()} chat_ids duplicados encontrados"
            )
            
            if self.fix_mode:
                # Limpar chat_ids duplicados (manter apenas o mais recente)
                for chat_data in operadores_chat_duplicado:
                    chat_id = chat_data['chat_id_telegram']
                    ops_duplicados = Operador.objects.filter(
                        chat_id_telegram=chat_id
                    ).order_by('-ultimo_acesso_bot')
                    
                    # Manter apenas o primeiro (mais recente)
                    for op in ops_duplicados[1:]:
                        op.chat_id_telegram = None
                        op.save()
                
                self._reportar_correcao("Chat_ids duplicados limpos")
        
        # 2. Operadores ativos sem permissões do bot
        ops_sem_bot = Operador.objects.filter(
            status='ATIVO',
            ativo_bot=False
        )
        
        if ops_sem_bot.exists():
            self._reportar_problema(
                f"🤖 {ops_sem_bot.count()} operadores ativos sem acesso ao bot"
            )
            
            if self.fix_mode:
                ops_sem_bot.update(ativo_bot=True)
                self._reportar_correcao(f"{ops_sem_bot.count()} operadores habilitados para bot")
        
        # 3. Operadores sem equipamentos ou clientes
        ops_sem_acesso = []
        for op in Operador.objects.filter(status='ATIVO', ativo_bot=True):
            if not op.get_equipamentos_disponiveis().exists():
                ops_sem_acesso.append(op)
        
        if ops_sem_acesso:
            self._reportar_problema(
                f"🔧 {len(ops_sem_acesso)} operadores sem acesso a equipamentos"
            )
            
            if self.fix_mode:
                from backend.apps.equipamentos.models import Equipamento
                try:
                    from backend.apps.clientes.models import Cliente
                    clientes_gerais = Cliente.objects.all()[:3]
                except ImportError:
                    clientes_gerais = []
                
                equipamentos_gerais = Equipamento.objects.filter(ativo_nr12=True)[:5]
                
                for op in ops_sem_acesso:
                    if equipamentos_gerais:
                        op.equipamentos_autorizados.set(equipamentos_gerais)
                    if clientes_gerais:
                        op.clientes_autorizados.set(clientes_gerais)
                
                self._reportar_correcao(f"{len(ops_sem_acesso)} operadores com acesso configurado")
        
        # 4. Verificar se método get_equipamentos_disponiveis existe
        try:
            operador_teste = Operador.objects.first()
            if operador_teste:
                equipamentos_disponiveis = operador_teste.get_equipamentos_disponiveis()
                self.stdout.write(f'   ✅ Método get_equipamentos_disponiveis() funcionando')
        except AttributeError:
            self._reportar_problema("⚙️ Método get_equipamentos_disponiveis() não implementado")
        except Exception as e:
            self._reportar_problema(f"⚙️ Erro em get_equipamentos_disponiveis(): {e}")
        
        self.stdout.write('   ✅ Verificação de operadores concluída')
    
    def _verificar_equipamentos(self):
        """Verifica consistência dos equipamentos - CORRIGIDO"""
        self.stdout.write('\n🔧 VERIFICANDO EQUIPAMENTOS')
        self.stdout.write('-' * 40)
        
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.nr12_checklist.models import TipoEquipamentoNR12
        
        # 1. Equipamentos sem tipo NR12
        eq_sem_tipo = Equipamento.objects.filter(
            ativo_nr12=True,
            tipo_nr12__isnull=True
        )
        
        if eq_sem_tipo.exists():
            self._reportar_problema(
                f"📋 {eq_sem_tipo.count()} equipamentos NR12 sem tipo definido"
            )
            
            if self.fix_mode:
                # Criar tipo genérico se não existir
                tipo_generico, created = TipoEquipamentoNR12.objects.get_or_create(
                    nome="Equipamento Genérico",
                    defaults={'descricao': 'Tipo genérico para equipamentos sem classificação'}
                )
                
                eq_sem_tipo.update(tipo_nr12=tipo_generico)
                self._reportar_correcao(f"{eq_sem_tipo.count()} equipamentos com tipo genérico atribuído")
        
        # 2. Verificar campos QR - CORRIGIDO para usar qr_code ao invés de qr_code_data
        eq_sem_qr = Equipamento.objects.filter(
            ativo_nr12=True,
            qr_code__isnull=True  # Mudado de qr_code_data para qr_code
        )
        
        if eq_sem_qr.exists():
            self._reportar_problema(
                f"🔲 {eq_sem_qr.count()} equipamentos sem QR code"
            )
            
            if self.fix_mode:
                # Tentar importar e usar gerador de QR
                try:
                    from backend.apps.equipamentos.qr_utils import QRCodeGenerator
                    
                    corrigidos = 0
                    for eq in eq_sem_qr[:10]:  # Limitar para não sobrecarregar
                        try:
                            result = QRCodeGenerator.gerar_qr_equipamento(eq)
                            if result.get('success'):
                                corrigidos += 1
                        except Exception as e:
                            if self.verbose:
                                self.stdout.write(f"      ⚠️ Erro ao gerar QR para {eq.nome}: {e}")
                    
                    if corrigidos > 0:
                        self._reportar_correcao(f"{corrigidos} QR codes gerados")
                    
                except ImportError:
                    self._reportar_problema("📦 Módulo qr_utils não encontrado - QR codes não corrigidos")
        
        # 3. Equipamentos sem código válido
        eq_sem_codigo_valido = []
        for eq in Equipamento.objects.filter(ativo_nr12=True)[:20]:
            codigo = getattr(eq, 'codigo', None)
            if not codigo or codigo.strip() == '':
                eq_sem_codigo_valido.append(eq)
        
        if eq_sem_codigo_valido:
            self._reportar_problema(
                f"🔢 {len(eq_sem_codigo_valido)} equipamentos sem código válido"
            )
        
        # 4. Verificar se equipamentos têm clientes associados
        eq_sem_cliente = Equipamento.objects.filter(
            ativo_nr12=True,
            cliente__isnull=True
        )
        
        if eq_sem_cliente.exists():
            self._reportar_problema(
                f"🏢 {eq_sem_cliente.count()} equipamentos sem cliente associado"
            )
        
        self.stdout.write('   ✅ Verificação de equipamentos concluída')
    
    def _verificar_checklists(self):
        """Verifica consistência dos checklists"""
        self.stdout.write('\n📋 VERIFICANDO CHECKLISTS')
        self.stdout.write('-' * 40)
        
        from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado
        
        # 1. Checklists sem itens
        checklists_vazios = ChecklistNR12.objects.annotate(
            itens_count=models.Count('itens')
        ).filter(itens_count=0)
        
        if checklists_vazios.exists():
            self._reportar_problema(
                f"📝 {checklists_vazios.count()} checklists sem itens"
            )
            
            if self.fix_mode:
                try:
                    from backend.apps.core.tasks import criar_itens_checklist
                    
                    corrigidos = 0
                    for checklist in checklists_vazios[:20]:  # Limitar
                        try:
                            itens_criados = criar_itens_checklist(checklist)
                            if itens_criados > 0:
                                corrigidos += 1
                        except Exception as e:
                            if self.verbose:
                                self.stdout.write(f"      ⚠️ Erro ao criar itens para checklist {checklist.id}: {e}")
                    
                    if corrigidos > 0:
                        self._reportar_correcao(f"{corrigidos} checklists com itens criados")
                        
                except ImportError:
                    self._reportar_problema("📦 Módulo tasks não encontrado - itens não criados")
        
        # 2. Checklists órfãos (sem responsável e em andamento)
        checklists_orfaos = ChecklistNR12.objects.filter(
            status='EM_ANDAMENTO',
            responsavel__isnull=True
        )
        
        if checklists_orfaos.exists():
            self._reportar_problema(
                f"👤 {checklists_orfaos.count()} checklists órfãos (sem responsável)"
            )
        
        # 3. Checklists antigos pendentes
        data_limite = date.today() - timedelta(days=7)
        checklists_antigos = ChecklistNR12.objects.filter(
            status='PENDENTE',
            data_checklist__lt=data_limite
        )
        
        if checklists_antigos.exists():
            self._reportar_problema(
                f"📅 {checklists_antigos.count()} checklists pendentes há mais de 7 dias"
            )
        
        # 4. Verificar integridade dos dados
        total_checklists = ChecklistNR12.objects.count()
        checklists_com_equipamento = ChecklistNR12.objects.filter(equipamento__isnull=False).count()
        
        if total_checklists > 0:
            taxa_integridade = (checklists_com_equipamento / total_checklists) * 100
            self.stdout.write(f'   📊 Taxa de integridade: {taxa_integridade:.1f}%')
            
            if taxa_integridade < 95:
                self._reportar_problema(f"📊 Taxa de integridade baixa: {taxa_integridade:.1f}%")
        
        self.stdout.write('   ✅ Verificação de checklists concluída')
    
    def _verificar_qr_codes(self):
        """Verifica sistema de QR codes"""
        self.stdout.write('\n🔲 VERIFICANDO QR CODES')
        self.stdout.write('-' * 40)
        
        from backend.apps.equipamentos.models import Equipamento
        from backend.apps.operadores.models import Operador
        
        # 1. Equipamentos com QR code gerado
        eq_com_qr = Equipamento.objects.filter(
            ativo_nr12=True,
            qr_code__isnull=False
        ).exclude(qr_code='')
        
        eq_total_nr12 = Equipamento.objects.filter(ativo_nr12=True).count()
        
        if eq_total_nr12 > 0:
            taxa_qr_equipamentos = (eq_com_qr.count() / eq_total_nr12) * 100
            self.stdout.write(f'   📊 Equipamentos com QR: {eq_com_qr.count()}/{eq_total_nr12} ({taxa_qr_equipamentos:.1f}%)')
            
            if taxa_qr_equipamentos < 80:
                self._reportar_problema(f"🔲 Poucos equipamentos com QR code: {taxa_qr_equipamentos:.1f}%")
        
        # 2. Operadores com QR code - CORRIGIDO
        ops_com_qr = Operador.objects.filter(
            status='ATIVO',
            qr_code__isnull=False
        ).exclude(qr_code='')
        
        ops_total_ativos = Operador.objects.filter(status='ATIVO').count()
        
        if ops_total_ativos > 0:
            taxa_qr_operadores = (ops_com_qr.count() / ops_total_ativos) * 100
            self.stdout.write(f'   📊 Operadores com QR code: {ops_com_qr.count()}/{ops_total_ativos} ({taxa_qr_operadores:.1f}%)')
        
        # 3. Testar geração de QR
        try:
            from backend.apps.equipamentos.qr_utils import QRCodeGenerator
            self.stdout.write('   ✅ Módulo QRCodeGenerator encontrado')
            
            # Testar validação - CORRIGIDO: sem usar 'types'
            teste_qr = '{"tipo": "equipamento", "id": 1, "codigo": "TEST"}'
            resultado = QRCodeGenerator.validar_qr_data(teste_qr)

            if isinstance(resultado, dict) and 'valid' in resultado:
                self.stdout.write('   ✅ Função de validação QR funcionando')
            else:
                self._reportar_problema("🔲 Função de validação QR com problemas")
                
        except ImportError:
            self._reportar_problema("📦 Módulo QRCodeGenerator não encontrado")
        except Exception as e:
            self._reportar_problema(f"🔲 Erro no sistema QR: {e}")
        
        self.stdout.write('   ✅ Verificação de QR codes concluída')
    
    def _verificar_apis(self):
        """Verifica endpoints da API"""
        self.stdout.write('\n📡 VERIFICANDO APIs')
        self.stdout.write('-' * 40)
        
        # Verificar se views_bot existem
        try:
            from backend.apps.nr12_checklist.views_bot import checklists_bot, equipamentos_operador
            self.stdout.write('   ✅ Views NR12 do bot encontradas')
        except ImportError as e:
            self._reportar_problema(f"📡 Views NR12 do bot não encontradas: {e}")
        
        try:
            from backend.apps.equipamentos.views_bot import equipamentos_publicos, checklists_equipamento
            self.stdout.write('   ✅ Views equipamentos do bot encontradas')
        except ImportError as e:
            self._reportar_problema(f"📡 Views equipamentos do bot não encontradas: {e}")
        
        try:
            from backend.apps.operadores.views_bot import atualizar_operador
            self.stdout.write('   ✅ Views operadores do bot encontradas')
        except ImportError as e:
            self._reportar_problema(f"📡 Views operadores do bot não encontradas: {e}")
        
        # Verificar se URLs estão configuradas
        from django.urls import reverse, NoReverseMatch
        
        urls_teste = [
            ('checklists-bot', []),
            ('nr12-checklists-bot', []),
            ('equipamentos-publicos-bot', []),  # CORRIGIDO: nome correto
            ('operador-equipamentos-bot', [1]),  # CORRIGIDO: nome correto
        ]
        
        for url_name, args in urls_teste:
            try:
                reverse(url_name, args=args)
                self.stdout.write(f'   ✅ URL {url_name} configurada')
            except NoReverseMatch:
                self._reportar_problema(f"🔗 URL {url_name} não encontrada")
        
        self.stdout.write('   ✅ Verificação de APIs concluída')
    
    def _verificar_bot_integration(self):
        """Verifica integração com bot"""
        self.stdout.write('\n🤖 VERIFICANDO INTEGRAÇÃO DO BOT')
        self.stdout.write('-' * 40)
        
        # Verificar se arquivos do bot existem
        import os
        from django.conf import settings
        
        bot_files = [
            'mandacaru_bot/bot_main/main.py',
            'mandacaru_bot/bot_checklist/handlers.py',
            'mandacaru_bot/bot_qr/handlers.py',
            'mandacaru_bot/core/config.py'
        ]
        
        project_root = getattr(settings, 'BASE_DIR', None)
        if project_root:
            parent_dir = project_root.parent
            
            for bot_file in bot_files:
                file_path = parent_dir / bot_file
                if file_path.exists():
                    self.stdout.write(f'   ✅ {bot_file} encontrado')
                else:
                    self._reportar_problema(f'🤖 {bot_file} não encontrado')
        else:
            self._reportar_problema("⚙️ BASE_DIR não configurado")
        
        # Verificar configurações do bot
        config_bot = [
            ('TELEGRAM_BOT_TOKEN', 'Token do bot Telegram'),
            ('API_BASE_URL', 'URL base da API'),
        ]
        
        for config, descricao in config_bot:
            if hasattr(settings, config) and getattr(settings, config):
                self.stdout.write(f'   ✅ {config} configurado')
            else:
                self._reportar_problema(f'⚙️ {config} não configurado ({descricao})')
        
        self.stdout.write('   ✅ Verificação de integração do bot concluída')
    
    def _reportar_problema(self, mensagem):
        """Reporta um problema encontrado"""
        self.problemas_encontrados += 1
        self.stdout.write(
            self.style.WARNING(f'   ❌ {mensagem}')
        )
    
    def _reportar_correcao(self, mensagem):
        """Reporta uma correção realizada"""
        self.problemas_corrigidos += 1
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ CORRIGIDO: {mensagem}')
        )
    
    def _resumo_final(self):
        """Mostra resumo final da verificação"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS('📊 RESUMO DA VERIFICAÇÃO')
        )
        self.stdout.write('=' * 60)
        
        self.stdout.write(f'❌ Problemas encontrados: {self.problemas_encontrados}')
        
        if self.fix_mode:
            self.stdout.write(f'✅ Problemas corrigidos: {self.problemas_corrigidos}')
            problemas_restantes = self.problemas_encontrados - self.problemas_corrigidos
            self.stdout.write(f'⚠️ Problemas restantes: {problemas_restantes}')
        else:
            self.stdout.write('💡 Execute com --fix para corrigir problemas automaticamente')
        
        # Classificação do sistema
        if self.problemas_encontrados == 0:
            classificacao = '🟢 SISTEMA ÍNTEGRO'
            cor = self.style.SUCCESS
        elif self.problemas_encontrados <= 5:
            classificacao = '🟡 PEQUENOS AJUSTES NECESSÁRIOS'
            cor = self.style.WARNING
        elif self.problemas_encontrados <= 15:
            classificacao = '🟠 CORREÇÕES RECOMENDADAS'
            cor = self.style.WARNING
        else:
            classificacao = '🔴 CORREÇÕES URGENTES NECESSÁRIAS'
            cor = self.style.ERROR
        
        self.stdout.write(f'\n🎯 STATUS: {cor(classificacao)}')
        
        # Recomendações
        if self.problemas_encontrados > 0:
            self.stdout.write('\n💡 PRÓXIMOS PASSOS RECOMENDADOS:')
            
            if self.problemas_encontrados > 15:
                self.stdout.write('   1. Implementar correções dos modelos')
                self.stdout.write('   2. Executar: python manage.py verificar_sistema --fix')
                self.stdout.write('   3. Testar todos os endpoints da API')
                self.stdout.write('   4. Verificar logs de erro')
            elif self.problemas_encontrados > 5:
                self.stdout.write('   1. Executar: python manage.py verificar_sistema --fix')
                self.stdout.write('   2. Testar funcionalidades principais')
            else:
                self.stdout.write('   1. Executar: python manage.py verificar_sistema --fix')
                self.stdout.write('   2. Sistema praticamente pronto para produção')
        else:
            self.stdout.write('\n🎉 SISTEMA TOTALMENTE ÍNTEGRO!')
            self.stdout.write('   • Todos os componentes funcionais')
            self.stdout.write('   • Pronto para uso em produção')
            self.stdout.write('   • Execute testes de carga se necessário')
        
        self.stdout.write('\n' + '=' * 60)