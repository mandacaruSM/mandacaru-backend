# ===============================================
# ARQUIVO: backend/apps/core/management/commands/run_telegram_bot.py
# Comando Django para executar o bot
# ===============================================

import os
import sys
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = 'Executa o Bot Telegram do Mandacaru'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Executa o bot em modo debug',
        )
    
    def handle(self, *args, **options):
        """Executa o bot Telegram"""
        
        # Encontrar diretório do bot
        project_root = Path(settings.BASE_DIR)
        bot_path = project_root / 'mandacaru_bot'
        
        if not bot_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Diretório do bot não encontrado: {bot_path}\n'
                    "Verifique se a pasta mandacaru_bot está na raiz do projeto."
                )
            )
            return
        
        # Adicionar ao Python path
        if str(bot_path) not in sys.path:
            sys.path.insert(0, str(bot_path))
        
        # Configurar variáveis de ambiente
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            os.environ['DJANGO_SETTINGS_MODULE'] = settings.SETTINGS_MODULE if hasattr(settings, 'SETTINGS_MODULE') else 'backend.settings'
        
        # Definir modo debug
        if options['debug']:
            os.environ['BOT_DEBUG'] = 'True'
            self.stdout.write(self.style.WARNING('🔧 Modo debug ativado'))
        
        try:
            # Importar e executar o bot
            self.stdout.write(self.style.SUCCESS('🤖 Iniciando Bot Telegram Mandacaru...'))
            self.stdout.write(f'📁 Diretório do bot: {bot_path}')
            
            # Verificar se arquivo start.py existe
            start_file = bot_path / 'start.py'
            if not start_file.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Arquivo start.py não encontrado em: {start_file}')
                )
                return
            
            # Importar função main do start.py
            from start import main
            
            # Executar o bot
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