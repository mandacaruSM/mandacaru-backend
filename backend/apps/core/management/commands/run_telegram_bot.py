# =============================
# 6. COMANDO MANAGEMENT CORRIGIDO
# backend/apps/core/management/commands/run_telegram_bot.py
# =============================

import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Executa o bot do Telegram'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Executa em modo debug com logs detalhados',
        )

    def handle(self, *args, **options):
        # Caminho correto para o bot na raiz do projeto
        bot_path = os.path.join(settings.BASE_DIR, 'mandacaru_bot')
        
        self.stdout.write(f'Procurando bot em: {bot_path}')
        
        if not os.path.exists(bot_path):
            self.stdout.write(
                self.style.ERROR(f'Pasta do bot não encontrada em: {bot_path}')
            )
            
            # Sugerir localizações alternativas
            alternative_paths = [
                os.path.join(settings.BASE_DIR, 'backend', 'mandacaru_bot'),
                os.path.join(settings.BASE_DIR, '..', 'mandacaru_bot'),
            ]
            
            self.stdout.write("Tentando localizações alternativas:")
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    self.stdout.write(f"✅ Encontrado em: {alt_path}")
                    bot_path = alt_path
                    break
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "❌ Bot não encontrado em nenhuma localização. "
                        "Verifique se a pasta mandacaru_bot está na raiz do projeto."
                    )
                )
                return
        
        # Adicionar ao Python path
        if bot_path not in sys.path:
            sys.path.insert(0, bot_path)
        
        # Configurar variáveis de ambiente
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
        
        # Definir modo debug
        if options['debug']:
            os.environ['BOT_DEBUG'] = 'True'
            self.stdout.write(self.style.WARNING('🔧 Modo debug ativado'))
        
        try:
            # Importar e executar o bot
            self.stdout.write(self.style.SUCCESS('🤖 Iniciando Bot Telegram Mandacaru...'))
            self.stdout.write(f'📁 Diretório do bot: {bot_path}')
            
            # Verificar se arquivo start.py existe
            start_file = os.path.join(bot_path, 'start.py')
            if not os.path.exists(start_file):
                self.stdout.write(
                    self.style.ERROR(f'❌ Arquivo start.py não encontrado em: {start_file}')
                )
                return
            
            # Importar função main
            from start import main
            
            # Executar o bot
            import asyncio
            asyncio.run(main())
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Erro ao importar módulo do bot: {e}\n'
                    f'Verifique se todos os arquivos estão presentes em: {bot_path}'
                )
            )
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n⚠️ Bot interrompido pelo usuário'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao executar bot: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())