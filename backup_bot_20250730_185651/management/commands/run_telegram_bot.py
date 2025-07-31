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

import asyncio
import os
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Executa o Bot Telegram do Mandacaru'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Executa o bot em modo debug',
        )
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Usa webhook ao invés de polling',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Iniciando Bot Telegram Mandacaru...')
        )

        # Adicionar o caminho do bot ao PYTHONPATH
        bot_path = Path(settings.BASE_DIR) / 'mandacaru_bot'
        if str(bot_path) not in sys.path:
            sys.path.insert(0, str(bot_path))

        try:
            # Importar e executar o bot
            from bot_main.main import main
            
            # Configurar modo debug se especificado
            if options['debug']:
                os.environ['BOT_DEBUG'] = 'True'
                self.stdout.write(
                    self.style.WARNING('🔧 Modo debug ativado')
                )

            # Configurar webhook se especificado
            if options['webhook']:
                os.environ['USE_WEBHOOK'] = 'True'
                self.stdout.write(
                    self.style.WARNING('🌐 Modo webhook ativado')
                )

            # Executar o bot
            self.stdout.write('🚀 Bot iniciado. Pressione Ctrl+C para parar.')
            asyncio.run(main())

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('\n🛑 Bot interrompido pelo usuário')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao executar bot: {e}')
            )
            raise
    