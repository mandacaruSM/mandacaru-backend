# ===============================================
# backend/apps/core/management/commands/testar_correcoes_bot.py
# Comando para testar as correções do bot
# ===============================================

from django.core.management.base import BaseCommand
import requests
import json

class Command(BaseCommand):
    help = 'Testa as correções do bot após implementação'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://localhost:8000',
            help='URL base para testes'
        )

    def handle(self, *args, **options):
        self.base_url = options['url']
        self.stdout.write(self.style.SUCCESS('🧪 TESTANDO CORREÇÕES DO BOT'))
        self.stdout.write('=' * 50)

        # Teste 1: Verificar se o servidor responde
        if not self._testar_servidor():
            return

        # Teste 2: Testar endpoints das views_bot
        self._testar_views_bot()
        
        # Teste 3: Testar imports e modelos
        self._testar_models()

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ TESTES CONCLUÍDOS!'))

    def _testar_servidor(self):
        """Testa se o servidor Django está rodando"""
        self.stdout.write('\n🔍 TESTE 1: SERVIDOR')
        self.stdout.write('-' * 30)
        
        try:
            response = requests.get(f'{self.base_url}/api/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(f"✅ Servidor rodando: {data.get('message', 'OK')}")
                return True
            else:
                self.stdout.write(self.style.ERROR(f'❌ Servidor retornou: {response.status_code}'))
                return False
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro de conexão: {e}'))
            self.stdout.write('💡 Execute: python manage.py runserver')
            return False

    def _testar_views_bot(self):
        """Testa os endpoints específicos do bot"""
        self.stdout.write('\n🔍 TESTE 2: VIEWS DO BOT')
        self.stdout.write('-' * 30)

        endpoints_teste = [
            ('/api/nr12/', 'API NR12'),
            ('/api/operadores/', 'API Operadores'),
            ('/api/equipamentos/', 'API Equipamentos'),
            ('/api/checklists/', 'Checklists Bot'),
            ('/api/nr12/checklists/', 'NR12 Checklists Bot'),
        ]

        for endpoint, nome in endpoints_teste:
            try:
                response = requests.get(f'{self.base_url}{endpoint}', timeout=5)
                if response.status_code == 200:
                    self.stdout.write(f'✅ {nome}: OK')
                elif response.status_code in [403, 404]:
                    self.stdout.write(f'⚠️ {nome}: {response.status_code} (normal se precisar autenticação)')
                else:
                    self.stdout.write(f'❌ {nome}: {response.status_code}')
            except Exception as e:
                self.stdout.write(f'❌ {nome}: Erro - {e}')

    def _testar_models(self):
        """Testa se os modelos estão importando corretamente"""
        self.stdout.write('\n🔍 TESTE 3: MODELOS E IMPORTS')
        self.stdout.write('-' * 30)

        try:
            # Testar imports dos modelos principais
            from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado
            self.stdout.write('✅ Modelos NR12: OK')
            
            from backend.apps.operadores.models import Operador
            self.stdout.write('✅ Modelo Operador: OK')
            
            from backend.apps.equipamentos.models import Equipamento
            self.stdout.write('✅ Modelo Equipamento: OK')

            # Testar imports das views_bot
            from backend.apps.nr12_checklist.views_bot import checklists_bot, equipamentos_operador
            self.stdout.write('✅ Views Bot NR12: OK')
            
            from backend.apps.operadores.views_bot import operador_por_chat_id, validar_operador_login
            self.stdout.write('✅ Views Bot Operadores: OK')
            
            from backend.apps.equipamentos.views_bot import equipamentos_publicos, checklists_equipamento
            self.stdout.write('✅ Views Bot Equipamentos: OK')

            # Testar métodos do modelo Operador
            if hasattr(Operador, 'get_equipamentos_disponiveis'):
                self.stdout.write('✅ Método get_equipamentos_disponiveis: OK')
            else:
                self.stdout.write('❌ Método get_equipamentos_disponiveis: FALTANDO')
                
            if hasattr(Operador, 'get_resumo_para_bot'):
                self.stdout.write('✅ Método get_resumo_para_bot: OK')
            else:
                self.stdout.write('❌ Método get_resumo_para_bot: FALTANDO')

        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro de importação: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro nos modelos: {e}'))

    def _testar_bot_integration(self):
        """Testa integração específica do bot"""
        self.stdout.write('\n🔍 TESTE 4: INTEGRAÇÃO BOT')
        self.stdout.write('-' * 30)

        try:
            # Testar se consegue simular um operador
            from backend.apps.operadores.models import Operador
            
            operador_teste = Operador.objects.filter(ativo_bot=True).first()
            
            if operador_teste:
                self.stdout.write(f'✅ Operador teste encontrado: {operador_teste.nome}')
                
                # Testar método get_equipamentos_disponiveis
                equipamentos = operador_teste.get_equipamentos_disponiveis()
                self.stdout.write(f'✅ Equipamentos disponíveis: {equipamentos.count()}')
                
                # Testar método get_resumo_para_bot  
                resumo = operador_teste.get_resumo_para_bot()
                self.stdout.write(f'✅ Resumo para bot: {resumo.get("nome", "OK")}')
                
            else:
                self.stdout.write('⚠️ Nenhum operador ativo para bot encontrado')
                self.stdout.write('💡 Execute: python manage.py criar_dados_teste')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na integração: {e}'))