# =====================
# management/commands/run_telegram_bot.py
# Comando Django para executar o bot Telegram
# =====================

"""
Para usar este comando, coloque este arquivo em:
your_django_app/management/commands/run_telegram_bot.py

Depois execute:
python manage.py run_telegram_bot
"""

# backend/apps/core/management/commands/run_telegram_bot.py

import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Executa o bot do Telegram integrado ao Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Executa em modo debug com logs detalhados',
        )

    def handle(self, *args, **options):
        # Adicionar o diretório do bot ao Python path
        bot_path = os.path.join(settings.BASE_DIR, 'mandacaru_bot')
        if bot_path not in sys.path:
            sys.path.insert(0, bot_path)
        
        # Configurar variáveis de ambiente se necessário
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
        
        # Definir modo debug
        if options['debug']:
            os.environ['BOT_DEBUG'] = 'True'
        
        try:
            # Importar e executar o bot
            self.stdout.write(self.style.SUCCESS('🤖 Iniciando Bot Telegram Mandacaru...'))
            
            from mandacaru_bot.start import main
            
            # Executar o bot
            import asyncio
            asyncio.run(main())
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Erro ao importar módulo do bot: {e}\n'
                    f'Verifique se a pasta mandacaru_bot está em: {bot_path}'
                )
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n⚠️ Bot interrompido pelo usuário'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao executar bot: {e}'))
            sys.exit(1)