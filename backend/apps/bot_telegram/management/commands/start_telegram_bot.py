# ================================================================
# ARQUIVO: backend/apps/bot_telegram/management/commands/start_telegram_bot.py
# Comando atualizado e unificado para iniciar o bot
# ================================================================

from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Inicia o Bot Telegram do Mandacaru ERP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Usar webhook em vez de polling'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8443,
            help='Porta para o webhook (padrão: 8443)'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Modo debug com logs detalhados'
        )

    def handle(self, *args, **options):
        """Inicia o bot Telegram"""
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🤖 INICIANDO BOT MANDACARU ERP v2.0'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Verificar configurações essenciais
        if not self._verificar_configuracoes():
            return
        
        # Configurar logging se debug
        if options['debug']:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Executar bot
        if options['webhook']:
            self._executar_webhook(options['port'])
        else:
            self._executar_polling()

    def _verificar_configuracoes(self):
        """Verifica configurações essenciais"""
        try:
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            
            if not bot_token:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ TELEGRAM_BOT_TOKEN não configurado!\n'
                        'Configure no settings.py ou variável de ambiente.'
                    )
                )
                return False
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Bot Token: ...{bot_token[-10:]}\n'
                    f'✅ Configurações verificadas'
                )
            )
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na verificação: {e}')
            )
            return False

    def _executar_polling(self):
        """Executa bot em modo polling (desenvolvimento)"""
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🚀 Iniciando bot em modo POLLING...\n'
                    f'   Pressione Ctrl+C para parar\n'
                )
            )
            
            # Criar e configurar aplicação
            app = self._criar_aplicacao()
            
            # Executar
            app.run_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⏹️  Bot interrompido pelo usuário')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na execução: {e}')
            )

    def _executar_webhook(self, port):
        """Executa bot em modo webhook (produção)"""
        webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
        
        if not webhook_url:
            self.stdout.write(
                self.style.ERROR(
                    '❌ TELEGRAM_WEBHOOK_URL não configurado para modo webhook!'
                )
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🚀 Iniciando bot em modo WEBHOOK...\n'
                f'   URL: {webhook_url}\n'
                f'   Porta: {port}'
            )
        )
        
        # Criar aplicação
        app = self._criar_aplicacao()
        
        # Executar
        bot_token = settings.TELEGRAM_BOT_TOKEN
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=f"/{bot_token}",
            webhook_url=f"{webhook_url}/{bot_token}",
            allowed_updates=['message', 'callback_query']
        )

    def _criar_aplicacao(self):
        """Cria aplicação do bot com todos os handlers"""
        try:
            # Importar handlers
            from backend.apps.bot_telegram.handlers.message import text_handler
            from backend.apps.bot_telegram.handlers.callback import callback_handler
            from backend.apps.bot_telegram.handlers.qr import handle_qr_photo
            from backend.apps.bot_telegram.commands.start import start_handler
            from backend.apps.bot_telegram.commands.help import help_handler
            from backend.apps.bot_telegram.commands.status import status_handler
            from backend.apps.bot_telegram.commands.logout import logout_handler
            
            # Criar aplicação
            app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            
            # ==========================================
            # COMANDOS
            # ==========================================
            app.add_handler(start_handler)
            app.add_handler(help_handler)
            app.add_handler(status_handler)
            app.add_handler(logout_handler)
            
            # ==========================================
            # HANDLERS DE CONTEÚDO
            # ==========================================
            
            # QR Code (fotos) - PRIORIDADE ALTA
            app.add_handler(MessageHandler(filters.PHOTO, handle_qr_photo), group=0)
            
            # Mensagens de texto - PRIORIDADE NORMAL
            app.add_handler(text_handler, group=1)
            
            # Callbacks de botões inline
            app.add_handler(callback_handler)
            
            # ==========================================
            # HANDLER DE ERRO
            # ==========================================
            app.add_error_handler(self._error_handler)
            
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Aplicação configurada:\n'
                    '   • Comandos: /start, /help, /status, /logout\n'
                    '   • Handlers: Text, Photo, Callback\n'
                    '   • QR Code: Habilitado\n'
                    '   • Error Handler: Configurado'
                )
            )
            
            return app
            
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Erro ao importar handlers: {e}\n'
                    'Verifique se todos os arquivos estão no lugar correto:'
                )
            )
            raise
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar aplicação: {e}')
            )
            raise

    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handler de erros global"""
        try:
            logger.error(f"Erro no bot: {context.error}")
            
            # Log detalhes do update se disponível
            if update and hasattr(update, 'effective_message'):
                logger.error(f"Update: {update}")
            
            # Tentar notificar o usuário se possível
            if update and hasattr(update, 'effective_message') and update.effective_message:
                try:
                    await update.effective_message.reply_text(
                        "❌ **Erro interno do sistema**\n\n"
                        "Ocorreu um erro inesperado. Tente novamente.\n\n"
                        "Se o problema persistir:\n"
                        "• Use `/start` para reiniciar\n"
                        "• Contate o suporte técnico"
                    )
                except Exception:
                    # Se nem conseguir enviar mensagem, apenas log
                    logger.error("Não foi possível notificar usuário sobre erro")
            
        except Exception as e:
            logger.error(f"Erro no error handler: {e}")

    def _mostrar_status_final(self):
        """Mostra status final do bot"""
        self.stdout.write(
            self.style.SUCCESS(
                '\n' + '=' * 60 + '\n'
                '🎉 BOT MANDACARU ERP INICIADO COM SUCESSO!\n'
                '=' * 60 + '\n'
                '📱 O bot está pronto para receber mensagens\n'
                '🔧 Funcionalidades disponíveis:\n'
                '   • Login por código ou QR Code\n'
                '   • Checklists NR12 completos\n'
                '   • Reconhecimento de equipamentos\n'
                '   • Interface interativa\n\n'
                '💡 Para testar:\n'
                '   1. Abra o Telegram\n'
                '   2. Inicie conversa com o bot\n'
                '   3. Digite: OP0001\n'
                '   4. Digite: EQ0001\n'
                '   5. Clique em "Fazer Checklist"\n\n'
                '⏹️  Para parar: Pressione Ctrl+C\n'
                '=' * 60
            )
        )