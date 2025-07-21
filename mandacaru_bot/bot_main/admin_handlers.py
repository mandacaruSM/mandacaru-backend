# =============================
# bot_main/admin_handlers.py
# =============================

from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from core.middleware import admin_required, log_user_action
from core.session import obter_estatisticas_sessoes, limpar_sessoes_expiradas, sessions
from core.db import verificar_status_api
from core.templates import MessageTemplates, ReportTemplates
from core.config import ADMIN_IDS
import psutil
import asyncio
from datetime import datetime

@admin_required
async def admin_menu_handler(message: Message, operador=None):
    """Menu principal de administração"""
    await log_user_action(message, "ADMIN_MENU_ACCESSED")
    
    menu_text = """
🔧 **Painel Administrativo**

Comandos disponíveis:

📊 **Monitoramento:**
• /status - Status do sistema
• /stats - Estatísticas de uso  
• /sessions - Sessões ativas

🔧 **Manutenção:**
• /cleanup - Limpar sessões antigas
• /restart - Reiniciar bot (desenvolvimento)
• /broadcast - Enviar mensagem para todos

📋 **Relatórios:**
• /report_users - Relatório de usuários
• /report_usage - Relatório de uso
• /logs - Visualizar logs recentes

⚙️ **Sistema:**
• /health - Verificar saúde do sistema
• /config - Configurações atuais
    """
    
    await message.answer(menu_text.strip())

@admin_required
async def status_handler(message: Message, operador=None):
    """Mostra status detalhado do sistema"""
    await log_user_action(message, "SYSTEM_STATUS_CHECKED")
    
    try:
        # Verifica API
        api_status = await verificar_status_api()
        
        # Estatísticas de sessão
        stats = obter_estatisticas_sessoes()
        
        # Informações do sistema
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
        
        status_text = f"""
🖥️ **Status do Sistema**

🌐 **API:** {'🟢 Online' if api_status else '🔴 Offline'}
👥 **Sessões Ativas:** {stats['total_sessoes']}
🔐 **Usuários Autenticados:** {stats['usuarios_autenticados']}

💾 **Memória:** {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
🔥 **CPU:** {cpu_percent}%
⏰ **Uptime:** {uptime_str}

🕐 **Última verificação:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """.strip()
        
        await message.answer(status_text)
        
    except Exception as e:
        await message.answer(f"❌ Erro ao obter status: {str(e)}")

@admin_required  
async def stats_handler(message: Message, operador=None):
    """Estatísticas detalhadas de uso"""
    await log_user_action(message, "USAGE_STATS_CHECKED")
    
    try:
        stats = obter_estatisticas_sessoes()
        
        # Calcular estatísticas de módulos (simulado)
        modulo_stats = {
            'checklist': len([s for s in sessions.values() if 'CHECKLIST' in s.get('estado', '')]),
            'abastecimento': len([s for s in sessions.values() if 'ABASTECIMENTO' in s.get('estado', '')]),
            'os': len([s for s in sessions.values() if 'OS' in s.get('estado', '')]),
            'financeiro': len([s for s in sessions.values() if 'FINANCEIRO' in s.get('estado', '')])
        }
        
        stats_text = f"""
📊 **Estatísticas de Uso**

👥 **Usuários:**
• Total de sessões: {stats['total_sessoes']}
• Autenticados: {stats['usuarios_autenticados']}
• Aguardando login: {stats['aguardando_autenticacao']}

📱 **Módulos Ativos:**
• 📋 Checklist: {modulo_stats['checklist']} usuários
• ⛽ Abastecimento: {modulo_stats['abastecimento']} usuários
• 🔧 OS: {modulo_stats['os']} usuários
• 💰 Financeiro: {modulo_stats['financeiro']} usuários

🕐 **Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """.strip()
        
        await message.answer(stats_text)
        
    except Exception as e:
        await message.answer(f"❌ Erro ao obter estatísticas: {str(e)}")

@admin_required
async def sessions_handler(message: Message, operador=None):
    """Lista sessões ativas"""
    await log_user_action(message, "ACTIVE_SESSIONS_VIEWED")
    
    if not sessions:
        await message.answer("📭 Nenhuma sessão ativa no momento.")
        return
    
    sessions_text = "📱 **Sessões Ativas:**\n\n"
    
    for chat_id, sessao in list(sessions.items())[:10]:  # Limita a 10
        operador_nome = sessao.get('operador', {}).get('nome', 'Não autenticado')
        estado = sessao.get('estado', 'Desconhecido')
        ultimo_acesso = sessao.get('ultimo_acesso', datetime.now())
        
        if isinstance(ultimo_acesso, datetime):
            tempo_str = ultimo_acesso.strftime('%H:%M:%S')
        else:
            tempo_str = 'N/A'
        
        sessions_text += f"👤 **{operador_nome}**\n"
        sessions_text += f"🆔 Chat: {chat_id}\n"
        sessions_text += f"📊 Estado: {estado}\n"
        sessions_text += f"🕐 Último acesso: {tempo_str}\n\n"
    
    if len(sessions) > 10:
        sessions_text += f"... e mais {len(sessions) - 10} sessões.\n"
    
    await message.answer(sessions_text)

@admin_required
async def cleanup_handler(message: Message, operador=None):
    """Limpa sessões antigas"""
    await log_user_action(message, "SESSIONS_CLEANUP_EXECUTED")
    
    try:
        sessoes_removidas = limpar_sessoes_expiradas(24)
        
        if sessoes_removidas > 0:
            await message.answer(f"🧹 Limpeza concluída! {sessoes_removidas} sessões antigas foram removidas.")
        else:
            await message.answer("✨ Sistema já está limpo! Nenhuma sessão antiga encontrada.")
            
    except Exception as e:
        await message.answer(f"❌ Erro na limpeza: {str(e)}")

@admin_required
async def health_handler(message: Message, operador=None):
    """Verificação completa de saúde do sistema"""
    await log_user_action(message, "SYSTEM_HEALTH_CHECKED")
    
    await message.answer("🔍 Verificando saúde do sistema...")
    
    try:
        checks = []
        
        # Verificar API
        api_ok = await verificar_status_api()
        checks.append(("🌐 API", "✅ OK" if api_ok else "❌ FALHA"))
        
        # Verificar memória
        memory = psutil.virtual_memory()
        memory_ok = memory.percent < 90
        checks.append(("💾 Memória", f"✅ {memory.percent:.1f}%" if memory_ok else f"⚠️ {memory.percent:.1f}%"))
        
        # Verificar CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_ok = cpu_percent < 80
        checks.append(("🔥 CPU", f"✅ {cpu_percent:.1f}%" if cpu_ok else f"⚠️ {cpu_percent:.1f}%"))
        
        # Verificar sessões
        stats = obter_estatisticas_sessoes()
        sessions_ok = stats['total_sessoes'] < 1000  # Limite arbitrário
        checks.append(("👥 Sessões", f"✅ {stats['total_sessoes']}" if sessions_ok else f"⚠️ {stats['total_sessoes']}"))
        
        health_text = "🏥 **Verificação de Saúde**\n\n"
        all_ok = True
        
        for check_name, check_result in checks:
            health_text += f"{check_name}: {check_result}\n"
            if "❌" in check_result or "⚠️" in check_result:
                all_ok = False
        
        health_text += f"\n🎯 **Status Geral:** {'✅ Sistema Saudável' if all_ok else '⚠️ Atenção Necessária'}"
        
        await message.answer(health_text)
        
    except Exception as e:
        await message.answer(f"❌ Erro na verificação: {str(e)}")

@admin_required
async def broadcast_handler(message: Message, operador=None):
    """Inicia processo de broadcast"""
    await log_user_action(message, "BROADCAST_INITIATED")
    
    chat_id = str(message.chat.id)
    
    # Salvar estado para próxima mensagem
    from core.session import atualizar_sessao
    atualizar_sessao(chat_id, "estado", "AGUARDANDO_BROADCAST")
    
    await message.answer(
        "📢 **Envio de Mensagem em Massa**\n\n"
        "Digite a mensagem que deseja enviar para todos os usuários autenticados:\n\n"
        "⚠️ *Cuidado: Esta ação enviará a mensagem para todos os usuários conectados.*"
    )

@admin_required
async def processar_broadcast(message: Message, operador=None):
    """Processa e envia broadcast"""
    chat_id = str(message.chat.id)
    from core.session import obter_sessao, atualizar_sessao
    
    sessao = obter_sessao(chat_id)
    if sessao.get("estado") != "AGUARDANDO_BROADCAST":
        return
    
    broadcast_text = message.text.strip()
    
    # Confirmar envio
    from core.utils import KeyboardBuilder
    keyboard = KeyboardBuilder.confirmar_cancelar()
    
    await message.answer(
        f"📢 **Confirmar Broadcast**\n\n"
        f"Mensagem a ser enviada:\n\n"
        f"*{broadcast_text}*\n\n"
        f"👥 Será enviado para {len([s for s in sessions.values() if s.get('operador')])} usuários.\n\n"
        f"Confirmar envio?",
        reply_markup=keyboard
    )
    
    # Salvar mensagem para callback
    atualizar_sessao(chat_id, "broadcast_message", broadcast_text)

async def confirmar_broadcast_callback(callback_query):
    """Callback para confirmar broadcast"""
    if callback_query.data == "confirmar":
        await callback_query.answer("Enviando mensagem...")
        
        chat_id = str(callback_query.message.chat.id)
        from core.session import obter_sessao, atualizar_sessao
        from bot_main.main import bot
        
        sessao = obter_sessao(chat_id)
        broadcast_text = sessao.get("broadcast_message")
        
        if not broadcast_text:
            await callback_query.message.edit_text("❌ Erro: Mensagem não encontrada.")
            return
        
        enviados = 0
        erros = 0
        
        # Enviar para todos os usuários autenticados
        for session_chat_id, session_data in sessions.items():
            operador = session_data.get('operador')
            if operador:
                try:
                    await bot.send_message(
                        chat_id=int(session_chat_id),
                        text=f"📢 **Mensagem da Administração**\n\n{broadcast_text}"
                    )
                    enviados += 1
                    await asyncio.sleep(0.1)  # Evitar spam
                except:
                    erros += 1
        
        await callback_query.message.edit_text(
            f"✅ **Broadcast Concluído**\n\n"
            f"📤 Enviados: {enviados}\n"
            f"❌ Erros: {erros}"
        )
        
        atualizar_sessao(chat_id, "estado", "AUTENTICADO")
        
    else:
        await callback_query.answer("Broadcast cancelado")
        await callback_query.message.edit_text("❌ Broadcast cancelado.")

def register_admin_handlers(dp: Dispatcher):
    """Registra handlers administrativos"""
    
    # Verificar se usuário é admin
    def admin_filter(message):
        return message.from_user.id in ADMIN_IDS
    
    # Função auxiliar para verificar estado da sessão
    def check_broadcast_state(message):
        chat_id = str(message.chat.id)
        sessao = obter_sessao(chat_id)
        return sessao.get("estado") == "AGUARDANDO_BROADCAST"
    
    # Comandos principais
    dp.message.register(admin_menu_handler, Command("admin"), admin_filter)
    dp.message.register(status_handler, Command("status"), admin_filter)
    dp.message.register(stats_handler, Command("stats"), admin_filter)
    dp.message.register(sessions_handler, Command("sessions"), admin_filter)
    dp.message.register(cleanup_handler, Command("cleanup"), admin_filter)
    dp.message.register(health_handler, Command("health"), admin_filter)
    dp.message.register(broadcast_handler, Command("broadcast"), admin_filter)
    
    # Estado de broadcast
    dp.message.register(
        processar_broadcast,
        F.text & ~F.text.startswith('/'),
        admin_filter,
        check_broadcast_state
    )
    
    # Callbacks
    dp.callback_query.register(
        confirmar_broadcast_callback,
        F.data.in_(["confirmar", "cancelar"])
    )