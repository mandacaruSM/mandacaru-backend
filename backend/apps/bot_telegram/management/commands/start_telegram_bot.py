# ================================================================
# ARQUIVO: backend/apps/bot_telegram/management/commands/start_telegram_bot.py
# Comando atualizado com suporte completo a QR
# ================================================================

from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging
from datetime import datetime

# Importações dos modelos
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12

# Importações do bot
from backend.apps.bot_telegram.handlers.message import text_handler
from backend.apps.bot_telegram.handlers.callback import callback_handler
from backend.apps.bot_telegram.handlers.qr import handle_qr_photo
from backend.apps.bot_telegram.utils.sessions import get_session, save_session, clear_session

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicia o Bot Telegram do Mandacaru ERP com suporte a QR Code'

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
        
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🤖 INICIANDO BOT MANDACARU ERP'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Verificar configurações
        if not self._verificar_configuracoes():
            return
        
        # Configurar logging
        if options['debug']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        # Executar bot
        try:
            if options['webhook']:
                self._executar_webhook(options['port'])
            else:
                self._executar_polling()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\\n⚠️ Bot interrompido pelo usuário'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao executar bot: {e}'))
            raise

    def _verificar_configuracoes(self):
        
        
        self.stdout.write('🔍 Verificando configurações...')
        
        # Token do bot
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_BOT_TOKEN não configurado!'))
            self.stdout.write('   Configure no arquivo .env')
            return False
        
        self.stdout.write(f'✅ Token configurado: ...{token[-10:]}')
        
        # Verificar modelos
        try:
            total_operadores = Operador.objects.filter(status='ATIVO').count()
            total_equipamentos = Equipamento.objects.filter(ativo_nr12=True).count()
            
            self.stdout.write(f'✅ Operadores ativos: {total_operadores}')
            self.stdout.write(f'✅ Equipamentos NR12: {total_equipamentos}')
            
            if total_operadores == 0:
                self.stdout.write(self.style.WARNING('⚠️ Nenhum operador ativo encontrado'))
                self.stdout.write('   Execute: python manage.py criar_operadores_demo')
            
            if total_equipamentos == 0:
                self.stdout.write(self.style.WARNING('⚠️ Nenhum equipamento NR12 encontrado'))
                self.stdout.write('   Execute: python manage.py setup_nr12')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar modelos: {e}'))
            return False
        
        # Verificar dependências
        try:
            import cv2
            import pyzbar
            self.stdout.write('✅ Bibliotecas de QR Code instaladas')
        except ImportError as e:
            self.stdout.write(self.style.WARNING('⚠️ Bibliotecas de QR Code não instaladas'))
            self.stdout.write('   Execute: pip install pyzbar opencv-python')
        
        return True

    def _executar_polling(self):
        
        
        self.stdout.write(self.style.SUCCESS('\\n🚀 Iniciando bot em modo POLLING...'))
        
        # Criar aplicação
        app = self._criar_aplicacao()
        
        # Informações
        self.stdout.write(self.style.SUCCESS('\\n✅ Bot iniciado com sucesso!'))
        self.stdout.write('\\n📱 FUNCIONALIDADES DISPONÍVEIS:')
        self.stdout.write('   • Leitura de QR Code (fotos)')
        self.stdout.write('   • Login de operadores')
        self.stdout.write('   • Checklist NR12')
        self.stdout.write('   • Registro de abastecimentos')
        self.stdout.write('   • Reporte de anomalias')
        self.stdout.write('\\n💡 Pressione Ctrl+C para parar\\n')
        
        # Executar
        app.run_polling(allowed_updates=['message', 'callback_query'])

    def _executar_webhook(self, port):
    
        
        webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
        if not webhook_url:
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_WEBHOOK_URL não configurado!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\\n🚀 Iniciando bot em modo WEBHOOK...'))
        self.stdout.write(f'   URL: {webhook_url}')
        self.stdout.write(f'   Porta: {port}')
        
        # Criar aplicação
        app = self._criar_aplicacao()
        
        # Executar
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=f"/{settings.TELEGRAM_BOT_TOKEN}",
            webhook_url=f"{webhook_url}/{settings.TELEGRAM_BOT_TOKEN}",
            allowed_updates=['message', 'callback_query']
        )

    def _criar_aplicacao(self):
        """Cria aplicação do bot com handlers atualizados"""
        # Criar aplicação
        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Comandos principais
        app.add_handler(CommandHandler('start', self._cmd_start))
        app.add_handler(CommandHandler('help', self._cmd_help))
        app.add_handler(CommandHandler('status', self._cmd_status))
        app.add_handler(CommandHandler('logout', self._cmd_logout))
        app.add_handler(CommandHandler('admin', self._cmd_admin))
        
        # Handlers de conteúdo com prioridade
        app.add_handler(MessageHandler(filters.PHOTO, handle_qr_photo), group=0)
        app.add_handler(text_handler, group=1)  # Usar o handler atualizado
        app.add_handler(callback_handler)       # Usar o handler atualizado
        
        # Error handler
        app.add_handler(self._error_handler)
        
        return app

    # ========================================
    # COMANDOS DO BOT
    # ========================================
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        
        user_name = update.effective_user.first_name
        chat_id = str(update.effective_chat.id)
        session = get_session(chat_id)
        
        if session and session.get('autenticado'):
            # Usuário já autenticado
            operador_nome = session.get('operador_nome', 'Operador')
            await update.message.reply_text(
                f"👋 Olá novamente, {operador_nome}!\\n\\n"
                f"📷 Escaneie o QR Code de um equipamento para continuar.\\n\\n"
                f"Ou use:\\n"
                f"/status - Ver seu status\\n"
                f"/logout - Sair do sistema\\n"
                f"/help - Ajuda"
            )
        else:
            # Novo usuário
            await update.message.reply_text(
                f"👋 Bem-vindo ao Mandacaru ERP, {user_name}!\\n\\n"
                f"🤖 Sou o assistente virtual que vai ajudá-lo com:\\n"
                f"• Checklists NR12\\n"
                f"• Registro de abastecimentos\\n"
                f"• Reporte de anomalias\\n"
                f"• Consulta de históricos\\n\\n"
                f"📷 **Para começar:**\\n"
                f"Envie uma foto do QR Code do seu cartão de operador.\\n\\n"
                f"💡 Não tem o QR Code? Entre em contato com seu supervisor."
            )

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        
        await update.message.reply_text(
            "📚 **AJUDA - Bot Mandacaru ERP**\\n\\n"
            "🔹 **Como usar:**\\n"
            "1. Escaneie o QR do seu cartão (login)\\n"
            "2. Escaneie o QR de um equipamento\\n"
            "3. Escolha a ação desejada\\n\\n"
            "🔹 **Comandos disponíveis:**\\n"
            "/start - Iniciar bot\\n"
            "/status - Ver seu status\\n"
            "/logout - Sair do sistema\\n"
            "/help - Esta mensagem\\n\\n"
            "🔹 **Dicas para QR Code:**\\n"
            "• Boa iluminação\\n"
            "• Câmera estável\\n"
            "• QR Code limpo\\n"
            "• Distância adequada\\n\\n"
            "❓ Problemas? Contate seu supervisor."
        )

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    
        
        chat_id = str(update.effective_chat.id)
        session = get_session(chat_id)
        
        if not session or not session.get('autenticado'):
            await update.message.reply_text(
                "❌ Você não está autenticado.\\n\\n"
                "📷 Escaneie o QR Code do seu cartão para fazer login."
            )
            return
        
        # Buscar dados do operador
        try:
            from asgiref.sync import sync_to_async
            
            operador_id = session.get('operador_id')
            operador = await sync_to_async(Operador.objects.get)(id=operador_id)
            
            # Estatísticas
            hoje = datetime.now().date()
            checklists_hoje = await sync_to_async(
                ChecklistNR12.objects.filter(
                    operador=operador,
                    data_checklist=hoje
                ).count
            )()
            
            await update.message.reply_text(
                f"📊 **SEU STATUS**\\n\\n"
                f"👤 Nome: {operador.nome}\\n"
                f"💼 Função: {operador.funcao}\\n"
                f"🏢 Setor: {operador.setor}\\n"
                f"📅 Admissão: {operador.data_admissao.strftime('%d/%m/%Y')}\\n\\n"
                f"📈 **Hoje:**\\n"
                f"✅ Checklists realizados: {checklists_hoje}\\n\\n"
                f"🔐 Sessão ativa desde: {session.get('ultimo_acesso', 'N/A')}"
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar status: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar seus dados.\\n"
                "Tente novamente mais tarde."
            )

    async def _cmd_logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    
        
        chat_id = str(update.effective_chat.id)
        session = get_session(chat_id)
        
        if session and session.get('autenticado'):
            nome = session.get('operador_nome', 'Operador')
            clear_session(chat_id)
            
            await update.message.reply_text(
                f"👋 Logout realizado com sucesso!\\n\\n"
                f"Até logo, {nome}!\\n\\n"
                f"Para usar novamente, escaneie seu QR Code."
            )
        else:
            await update.message.reply_text(
                "❌ Você não está autenticado."
            )

    async def _cmd_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    
        
        user_id = str(update.effective_user.id)
        admin_ids = getattr(settings, 'ADMIN_IDS', [])
        
        if user_id not in admin_ids:
            await update.message.reply_text(
                "❌ Acesso negado.\\n"
                "Este comando é apenas para administradores."
            )
            return
        
        # Menu administrativo
        keyboard = [
            [InlineKeyboardButton("📊 Estatísticas", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Operadores Online", callback_data="admin_users")],
            [InlineKeyboardButton("🔄 Limpar Cache", callback_data="admin_clear_cache")],
            [InlineKeyboardButton("📋 Logs Recentes", callback_data="admin_logs")],
            [InlineKeyboardButton("🔧 Status Sistema", callback_data="admin_system")],
            [InlineKeyboardButton("❌ Fechar", callback_data="admin_close")]
        ]
        
        await update.message.reply_text(
            "🔧 **PAINEL ADMINISTRATIVO**\\n\\n"
            "Selecione uma opção:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
    
        
        logger.error(f"Erro no update {update}: {context.error}")
        
        # Tentar notificar o usuário
        if update and hasattr(update, 'effective_message'):
            try:
                await update.effective_message.reply_text(
                    "❌ Ocorreu um erro ao processar sua solicitação.\\n"
                    "Por favor, tente novamente.\\n\\n"
                    "Se o problema persistir, contate o suporte."
                )
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de erro: {e}")
        
        # Notificar admins em erros críticos
        if isinstance(context.error, Exception):
            error_message = f"🚨 ERRO NO BOT:\\n{type(context.error).__name__}: {str(context.error)}"
            admin_ids = getattr(settings, 'ADMIN_IDS', [])
            
            for admin_id in admin_ids:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=error_message
                    )
                except:
                    pass

    # ========================================
    # CALLBACKS ADMINISTRATIVOS
    # ========================================
    
    async def _handle_admin_callback(self, query, data):
    
        
        from asgiref.sync import sync_to_async
        from backend.apps.bot_telegram.utils.sessions import _memory_sessions
        
        try:
            if data == "admin_stats":
                # Estatísticas gerais
                total_operadores = await sync_to_async(Operador.objects.filter(status='ATIVO').count)()
                total_equipamentos = await sync_to_async(Equipamento.objects.filter(ativo_nr12=True).count)()
                
                hoje = datetime.now().date()
                checklists_hoje = await sync_to_async(
                    ChecklistNR12.objects.filter(data_checklist=hoje).count
                )()
                checklists_concluidos = await sync_to_async(
                    ChecklistNR12.objects.filter(
                        data_checklist=hoje,
                        status='CONCLUIDO'
                    ).count
                )()
                
                # Sessões ativas
                sessoes_ativas = len([s for s in _memory_sessions.values() 
                                    if s.get('autenticado')])
                
                await query.edit_message_text(
                    f"📊 **ESTATÍSTICAS DO SISTEMA**\\n\\n"
                    f"👥 Operadores ativos: {total_operadores}\\n"
                    f"🔧 Equipamentos NR12: {total_equipamentos}\\n\\n"
                    f"📅 **HOJE ({hoje.strftime('%d/%m/%Y')}):**\\n"
                    f"📋 Checklists criados: {checklists_hoje}\\n"
                    f"✅ Checklists concluídos: {checklists_concluidos}\\n"
                    f"📱 Usuários online: {sessoes_ativas}\\n\\n"
                    f"🕐 Atualizado: {datetime.now().strftime('%H:%M:%S')}"
                )
                
            elif data == "admin_users":
                # Usuários online
                usuarios_online = []
                for chat_id, session in _memory_sessions.items():
                    if session.get('autenticado'):
                        usuarios_online.append(
                            f"• {session.get('operador_nome', 'N/A')} "
                            f"({session.get('operador_codigo', 'N/A')})"
                        )
                
                if usuarios_online:
                    lista = "\\n".join(usuarios_online[:20])  # Limitar a 20
                    texto = f"👥 **USUÁRIOS ONLINE ({len(usuarios_online)}):**\\n\\n{lista}"
                    if len(usuarios_online) > 20:
                        texto += f"\\n\\n... e mais {len(usuarios_online) - 20} usuários"
                else:
                    texto = "👥 Nenhum usuário online no momento."
                
                await query.edit_message_text(texto)
                
            elif data == "admin_clear_cache":
                # Limpar cache/sessões
                sessoes_limpas = len(_memory_sessions)
                _memory_sessions.clear()
                
                await query.edit_message_text(
                    f"🔄 **CACHE LIMPO**\\n\\n"
                    f"✅ {sessoes_limpas} sessões removidas\\n"
                    f"✅ Memória liberada\\n\\n"
                    f"⚠️ Todos os usuários precisarão fazer login novamente."
                )
                
            elif data == "admin_logs":
                # Logs recentes (simulado)
                await query.edit_message_text(
                    "📋 **LOGS RECENTES**\\n\\n"
                    "Para logs completos, verifique:\\n"
                    "• Arquivo: `logs/bot.log`\\n"
                    "• Console do servidor\\n"
                    "• Django Admin\\n\\n"
                    "Use: `tail -f logs/bot.log`"
                )
                
            elif data == "admin_system":
                # Status do sistema
                import psutil
                import platform
                
                # Informações do sistema
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Uptime do bot (simulado)
                uptime = datetime.now() - datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                
                await query.edit_message_text(
                    f"🔧 **STATUS DO SISTEMA**\\n\\n"
                    f"🖥️ **Servidor:**\\n"
                    f"• OS: {platform.system()} {platform.release()}\\n"
                    f"• Python: {platform.python_version()}\\n"
                    f"• Django: {settings.VERSION if hasattr(settings, 'VERSION') else 'N/A'}\\n\\n"
                    f"📊 **Recursos:**\\n"
                    f"• CPU: {cpu_percent}%\\n"
                    f"• RAM: {memory.percent}% ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)\\n"
                    f"• Disco: {disk.percent}% usado\\n\\n"
                    f"⏱️ **Uptime:** {str(uptime).split('.')[0]}"
                )
                
            elif data == "admin_close":
                await query.edit_message_text("✅ Painel administrativo fechado.")
                
        except Exception as e:
            logger.error(f"Erro no callback admin: {e}")
            await query.edit_message_text(
                f"❌ Erro ao processar comando administrativo:\\n{str(e)}"
            )

    # ========================================
    # MÉTODOS AUXILIARES
    # ========================================
    
    def _formatar_tempo(self, segundos):
        
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60
        
        if horas > 0:
            return f"{horas}h {minutos}m"
        elif minutos > 0:
            return f"{minutos}m {segundos}s"
        else:
            return f"{segundos}s"
    
    def _verificar_horario_trabalho(self):
    
        agora = datetime.now()
        hora = agora.hour
        dia_semana = agora.weekday()  # 0=Segunda, 6=Domingo
        
        # Segunda a Sexta, 6h às 22h
        if dia_semana < 5:  # Dias úteis
            return 6 <= hora < 22
        # Sábado, 6h às 18h
        elif dia_semana == 5:
            return 6 <= hora < 18
        # Domingo - fechado
        else:
            return False


# ================================================================
# EXEMPLO DE USO E TESTES
# ================================================================



    
    import sys
    import os
    
    # Adicionar o diretório raiz ao path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    import django
    django.setup()
    
    # Executar comando
    from django.core.management import execute_from_command_line
    #execute_from_command_line(['manage.py', 'start_telegram_bot', '--debug'])
