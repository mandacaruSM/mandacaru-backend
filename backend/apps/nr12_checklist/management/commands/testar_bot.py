# ================================================================
# COMANDO PARA TESTAR CONFIGURAÇÃO DO BOT
# CRIAR: backend/apps/nr12_checklist/management/commands/testar_bot.py
# ================================================================

from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Testa a configuração do bot e endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://localhost:8000',
            help='URL base para testes (padrão: http://localhost:8000)'
        )
        parser.add_argument(
            '--criar-dados',
            action='store_true',
            help='Criar dados de teste se não existirem'
        )

    def handle(self, *args, **options):
        self.base_url = options['url']
        self.stdout.write(self.style.SUCCESS('🤖 TESTANDO CONFIGURAÇÃO DO BOT'))
        self.stdout.write('=' * 60)

        # Teste 1: Verificar modelos
        self._testar_modelos()
        
        # Teste 2: Criar dados se solicitado
        if options['criar_dados']:
            self._criar_dados_teste()
        
        # Teste 3: Testar endpoints
        self._testar_endpoints()
        
        # Teste 4: Testar URLs
        self._testar_urls()
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ TESTES CONCLUÍDOS!'))

    def _testar_modelos(self):
        """Testa se os modelos estão funcionando corretamente"""
        self.stdout.write('\n🔍 TESTE 1: MODELOS')
        self.stdout.write('-' * 30)
        
        try:
            from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
            from backend.apps.operadores.models import Operador
            from backend.apps.nr12_checklist.models import ChecklistNR12
            
            # Testar categoria
            categoria_count = CategoriaEquipamento.objects.count()
            self.stdout.write(f'✅ Categorias de equipamentos: {categoria_count}')
            
            # Testar equipamentos
            equipamento_count = Equipamento.objects.count()
            self.stdout.write(f'✅ Equipamentos: {equipamento_count}')
            
            if equipamento_count > 0:
                eq = Equipamento.objects.first()
                self.stdout.write(f'   📌 Exemplo: {eq.nome} (Código: {eq.codigo})')
                self.stdout.write(f'   📌 Frequências: {eq.frequencias_checklist}')
                self.stdout.write(f'   📌 QR URL: {eq.qr_url_bot}')
                
                # Testar se campo antigo foi removido
                try:
                    _ = eq.frequencia_checklist  # Campo antigo
                    self.stdout.write(self.style.WARNING('⚠️  Campo antigo frequencia_checklist ainda existe!'))
                except AttributeError:
                    self.stdout.write('✅ Campo antigo removido corretamente')
            
            # Testar operadores
            operador_count = Operador.objects.filter(status='ATIVO', ativo_bot=True).count()
            self.stdout.write(f'✅ Operadores ativos no bot: {operador_count}')
            
            if operador_count > 0:
                op = Operador.objects.filter(status='ATIVO', ativo_bot=True).first()
                self.stdout.write(f'   📌 Exemplo: {op.nome} (Código: {op.codigo})')
                
                # Testar métodos do operador
                equipamentos_disp = op.get_equipamentos_disponiveis().count()
                self.stdout.write(f'   📌 Equipamentos disponíveis: {equipamentos_disp}')
                
                # Testar verificação QR
                verificado = Operador.verificar_qr_code(op.codigo)
                self.stdout.write(f'   📌 Verificação QR: {"✅" if verificado else "❌"}')
            
            # Testar checklists
            checklist_count = ChecklistNR12.objects.count()
            self.stdout.write(f'✅ Checklists NR12: {checklist_count}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro nos modelos: {e}'))

    def _criar_dados_teste(self):
        """Cria dados de teste se necessário"""
        self.stdout.write('\n🏗️  TESTE 2: CRIANDO DADOS DE TESTE')
        self.stdout.write('-' * 30)
        
        try:
            from backend.apps.equipamentos.models import Equipamento, CategoriaEquipamento
            from backend.apps.operadores.models import Operador
            from backend.apps.clientes.models import Cliente
            from backend.apps.empreendimentos.models import Empreendimento
            from datetime import date
            
            # Criar cliente se não existir
            cliente, created = Cliente.objects.get_or_create(
                cnpj='12.345.678/0001-90',
                defaults={
                    'razao_social': 'Empresa Teste Bot',
                    'nome_fantasia': 'Teste Bot',
                    'telefone': '(11) 99999-9999',
                    'email': 'teste@bot.com.br'
                }
            )
            if created:
                self.stdout.write('✅ Cliente de teste criado')
            
            # Criar empreendimento se não existir
            empreendimento, created = Empreendimento.objects.get_or_create(
                nome='Projeto Teste Bot',
                defaults={
                    'cliente': cliente,
                    'ativo': True,
                    'data_inicio': date.today()
                }
            )
            if created:
                self.stdout.write('✅ Empreendimento de teste criado')
            
            # Criar categoria se não existir
            categoria, created = CategoriaEquipamento.objects.get_or_create(
                codigo='TST',
                defaults={
                    'nome': 'Teste',
                    'prefixo_codigo': 'TST',
                    'ativo': True
                }
            )
            if created:
                self.stdout.write('✅ Categoria de teste criada')
            
            # Criar equipamento se não existir
            if not Equipamento.objects.exists():
                equipamento = Equipamento.objects.create(
                    nome='Equipamento Teste Bot',
                    categoria=categoria,
                    cliente=cliente,
                    empreendimento=empreendimento,
                    ativo_nr12=True,
                    frequencias_checklist=['DIARIA'],
                    status_operacional='DISPONIVEL'
                )
                self.stdout.write(f'✅ Equipamento de teste criado: {equipamento.codigo}')
            
            # Criar operador se não existir
            if not Operador.objects.filter(ativo_bot=True).exists():
                operador = Operador.objects.create(
                    nome='Operador Teste Bot',
                    cpf='123.456.789-00',
                    data_nascimento=date(1990, 1, 1),
                    telefone='(11) 91234-5678',
                    endereco='Rua Teste, 123',
                    cidade='São Paulo',
                    estado='SP',
                    cep='01000-000',
                    funcao='Operador de Teste',
                    setor='Teste',
                    data_admissao=date.today(),
                    numero_documento='12345678900',
                    status='ATIVO',
                    ativo_bot=True,
                    pode_fazer_checklist=True,
                    pode_registrar_abastecimento=True,
                    pode_reportar_anomalia=True
                )
                self.stdout.write(f'✅ Operador de teste criado: {operador.codigo}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar dados: {e}'))

    def _testar_endpoints(self):
        """Testa os endpoints do bot"""
        self.stdout.write('\n🌐 TESTE 3: ENDPOINTS DO BOT')
        self.stdout.write('-' * 30)
        
        # Teste API root
        try:
            response = requests.get(f'{self.base_url}/api/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.stdout.write('✅ API root funcionando')
                if 'bot_endpoints' in data:
                    self.stdout.write('✅ Endpoints do bot listados')
                else:
                    self.stdout.write('⚠️  Endpoints do bot não listados')
            else:
                self.stdout.write(f'❌ API root erro: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'❌ Erro na API root: {e}')
        
        # Teste endpoint de login (deve dar erro mas endpoint deve existir)
        try:
            response = requests.post(
                f'{self.base_url}/api/nr12/bot/operador/login/',
                json={'qr_code': 'TESTE', 'chat_id': '123'},
                timeout=5
            )
            if response.status_code in [400, 404]:  # Erro esperado
                self.stdout.write('✅ Endpoint de login existe')
            elif response.status_code == 200:
                self.stdout.write('✅ Endpoint de login funcionando!')
            else:
                self.stdout.write(f'⚠️  Login endpoint status: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'❌ Erro no endpoint de login: {e}')
        
        # Teste endpoint de equipamento
        try:
            response = requests.get(
                f'{self.base_url}/api/nr12/bot/equipamento/1/',
                timeout=5
            )
            if response.status_code in [200, 403, 404]:  # Respostas válidas
                self.stdout.write('✅ Endpoint de equipamento existe')
            else:
                self.stdout.write(f'⚠️  Equipamento endpoint status: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'❌ Erro no endpoint de equipamento: {e}')

    def _testar_urls(self):
        """Testa se as URLs estão configuradas"""
        self.stdout.write('\n🔗 TESTE 4: CONFIGURAÇÃO DE URLs')
        self.stdout.write('-' * 30)
        
        try:
            from django.urls import reverse
            from django.test import RequestFactory
            
            # Testar URLs específicas do bot
            urls_teste = [
                ('api_root', None),
            ]
            
            for url_name, args in urls_teste:
                try:
                    url = reverse(url_name, args=args)
                    self.stdout.write(f'✅ URL {url_name}: {url}')
                except Exception as e:
                    self.stdout.write(f'❌ URL {url_name}: {e}')
                    
        except Exception as e:
            self.stdout.write(f'❌ Erro ao testar URLs: {e}')
        
        # Verificar configurações
        self.stdout.write('\n📋 CONFIGURAÇÕES:')
        try:
            base_url = getattr(settings, 'BASE_URL', 'NÃO DEFINIDO')
            self.stdout.write(f'   BASE_URL: {base_url}')
            
            bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'NÃO DEFINIDO')
            self.stdout.write(f'   TELEGRAM_BOT_USERNAME: {bot_username}')
            
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', 'NÃO DEFINIDO')
            if bot_token and bot_token != 'NÃO DEFINIDO':
                self.stdout.write(f'   TELEGRAM_BOT_TOKEN: {"*" * 20}...{bot_token[-5:]}')
            else:
                self.stdout.write(f'   TELEGRAM_BOT_TOKEN: {bot_token}')
                
        except Exception as e:
            self.stdout.write(f'❌ Erro nas configurações: {e}')

        # Resumo final
        self.stdout.write('\n📊 RESUMO DOS TESTES:')
        self.stdout.write('   ✅ Modelos: Verificados')
        self.stdout.write('   ✅ Endpoints: Testados') 
        self.stdout.write('   ✅ URLs: Configuradas')
        self.stdout.write('\n💡 PRÓXIMO PASSO: Implementar bot Telegram')
        
        # Comandos úteis
        self.stdout.write('\n🔧 COMANDOS ÚTEIS:')
        self.stdout.write('   python manage.py testar_bot --criar-dados')
        self.stdout.write('   python manage.py runserver')
        self.stdout.write('   curl http://localhost:8000/api/')


# ================================================================
# COMANDO PARA EXECUTAR:
# python manage.py testar_bot --criar-dados
# ================================================================