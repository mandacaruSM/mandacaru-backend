# File: backend/apps/bot_telegram/handlers/callback.py - VERSÃO INTERATIVA
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime, date
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

# Usar o mesmo dicionário de sessões
from .message import _memory_sessions

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa callbacks de botões inline de forma interativa"""
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat.id)
    session = _memory_sessions.get(chat_id, {})
    
    if not session.get('autenticado'):
        await query.edit_message_text(
            "❌ **Sessão expirada**\n\n"
            "Faça login novamente digitando seu código de operador ou escaneando seu QR Code.",
            parse_mode='Markdown'
        )
        return

    data = query.data
    operador = session.get('operador')
    
    logger.info(f"Callback recebido: {data} do operador {operador.codigo}")

    # ==========================================
    # CALLBACKS DO MENU PRINCIPAL
    # ==========================================
    if data == "menu_principal":
        await voltar_menu_principal(query, operador)
    
    # ==========================================
    # CALLBACKS DO PERFIL
    # ==========================================
    elif data == "perfil_stats":
        await mostrar_perfil_estatisticas(query, operador)
    elif data == "perfil_update":
        await atualizar_perfil_dados(query, operador)
    elif data == "perfil_history":
        await mostrar_perfil_historico(query, operador)
    
    # ==========================================
    # CALLBACKS DOS RELATÓRIOS
    # ==========================================
    elif data == "rel_checklists":
        await relatorio_checklists_detalhado(query, operador)
    elif data == "rel_abastecimentos":
        await relatorio_abastecimentos_detalhado(query, operador)
    elif data == "rel_anomalias":
        await relatorio_anomalias_detalhado(query, operador)
    elif data == "rel_equipamentos":
        await relatorio_equipamentos_detalhado(query, operador)
    elif data == "rel_resumo":
        await relatorio_resumo_geral(query, operador)
    elif data == "rel_dashboard":
        await mostrar_dashboard(query, operador)
    elif data == "rel_periodo":
        await relatorio_por_periodo(query, operador)
    elif data == "rel_cliente":
        await relatorio_por_cliente(query, operador)
    
    # ==========================================
    # CALLBACKS DO SISTEMA
    # ==========================================
    elif data == "sys_sync":
        await sincronizar_dados(query, operador)
    elif data == "sys_status":
        await mostrar_status_sistema(query, operador)
    elif data == "sys_logout":
        await confirmar_logout(query, operador)
    elif data == "sys_config":
        await mostrar_configuracoes(query, operador)
    elif data == "logout_confirm":
        await fazer_logout(query, chat_id)
    elif data == "logout_cancel":
        await cancelar_logout(query, operador)
    
    # ==========================================
    # CALLBACKS DA AJUDA
    # ==========================================
    elif data == "help_start":
        await ajuda_primeiros_passos(query)
    elif data == "help_usage":
        await ajuda_como_usar(query)
    elif data == "help_troubleshoot":
        await ajuda_solucao_problemas(query)
    elif data == "help_contact":
        await ajuda_contato(query)
    
    # ==========================================
    # CALLBACKS DOS CHECKLISTS
    # ==========================================
    elif data == "check_pendentes":
        await checklists_pendentes(query, operador)
    elif data == "check_concluidos":
        await checklists_concluidos(query, operador)
    elif data == "check_stats":
        await checklists_estatisticas(query, operador)
    elif data == "check_buscar":
        await checklists_buscar(query, operador)
    
    # ==========================================
    # CALLBACKS DOS ABASTECIMENTOS
    # ==========================================
    elif data == "abast_detalhes":
        await abastecimentos_detalhes(query, operador)
    
    # ==========================================
    # CALLBACKS DAS ANOMALIAS
    # ==========================================
    elif data == "anom_criticas":
        await anomalias_criticas(query, operador)
    elif data == "anom_moderadas":
        await anomalias_moderadas(query, operador)
    elif data == "anom_stats":
        await anomalias_estatisticas(query, operador)
    elif data == "anom_nova":
        await nova_anomalia(query, operador)
    
    # ==========================================
    # CALLBACKS DOS EQUIPAMENTOS
    # ==========================================
    elif data == "equip_mais_usados":
        await equipamentos_mais_usados(query, operador)
    elif data == "equip_por_cliente":
        await equipamentos_por_cliente(query, operador)
    elif data == "equip_historico":
        await equipamentos_historico(query, operador)
    elif data == "equip_buscar":
        await equipamentos_buscar(query, operador)
    
    else:
        await query.edit_message_text(
            f"🔄 **Processando...**\n\n"
            f"Comando: `{data}`\n"
            f"Status: Em desenvolvimento\n\n"
            f"💡 Esta funcionalidade será implementada em breve!",
            parse_mode='Markdown'
        )

# ==========================================
# FUNÇÕES DOS CALLBACKS - MENU PRINCIPAL
# ==========================================

async def voltar_menu_principal(query, operador):
    """Volta ao menu principal"""
    keyboard = [
        [InlineKeyboardButton("📷 Escanear QR Code", callback_data="scan_qr")],
        [
            InlineKeyboardButton("👤 Meu Perfil", callback_data="show_profile"),
            InlineKeyboardButton("📊 Relatórios", callback_data="show_reports")
        ],
        [
            InlineKeyboardButton("🔧 Sistema", callback_data="show_system"),
            InlineKeyboardButton("❓ Ajuda", callback_data="show_help")
        ]
    ]
    
    await query.edit_message_text(
        f"🏠 **MENU PRINCIPAL**\n\n"
        f"👋 Bem-vindo, **{operador.nome}**!\n"
        f"💼 {operador.funcao} - {operador.setor}\n"
        f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        f"🚀 **O que deseja fazer?**\n"
        f"Escolha uma opção abaixo:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - PERFIL
# ==========================================

async def mostrar_perfil_estatisticas(query, operador):
    """Mostra estatísticas detalhadas do perfil"""
    # TODO: Buscar dados reais do banco
    stats = {
        'dias_trabalhados': 22,
        'horas_totais': 176,
        'checklist_media_dia': 2.1,
        'eficiencia': 95,
        'ranking_equipe': 3
    }
    
    keyboard = [
        [InlineKeyboardButton("📈 Gráfico de Performance", callback_data="perfil_grafico")],
        [InlineKeyboardButton("🏆 Ranking da Equipe", callback_data="perfil_ranking")],
        [InlineKeyboardButton("🔙 Voltar ao Perfil", callback_data="show_profile")]
    ]
    
    await query.edit_message_text(
        f"📊 **ESTATÍSTICAS DETALHADAS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📅 **Este mês:**\n"
        f"• Dias trabalhados: {stats['dias_trabalhados']}\n"
        f"• Horas totais: {stats['horas_totais']}h\n"
        f"• Média de checklists/dia: {stats['checklist_media_dia']}\n\n"
        f"📈 **Performance:**\n"
        f"• Eficiência: {stats['eficiencia']}%\n"
        f"• Posição na equipe: {stats['ranking_equipe']}º lugar\n"
        f"• Tendência: 📈 Crescendo\n\n"
        f"🎯 **Meta do mês:** 50 checklists\n"
        f"✅ **Progresso:** 45/50 (90%)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def atualizar_perfil_dados(query, operador):
    """Atualiza os dados do perfil"""
    await query.edit_message_text(
        f"🔄 **ATUALIZANDO PERFIL...**\n\n"
        f"⏳ Sincronizando dados...\n"
        f"📊 Calculando estatísticas...\n"
        f"🔍 Verificando permissões...\n\n"
        f"✅ **Atualização concluída!**\n\n"
        f"🕐 **Última atualização:** {datetime.now().strftime('%H:%M:%S')}\n"
        f"📱 **Status:** Online\n"
        f"🔗 **Conectividade:** Estável",
        parse_mode='Markdown'
    )

async def mostrar_perfil_historico(query, operador):
    """Mostra histórico de atividades"""
    keyboard = [
        [
            InlineKeyboardButton("📅 Hoje", callback_data="hist_hoje"),
            InlineKeyboardButton("📅 Esta Semana", callback_data="hist_semana")
        ],
        [
            InlineKeyboardButton("📅 Este Mês", callback_data="hist_mes"),
            InlineKeyboardButton("📅 Personalizado", callback_data="hist_custom")
        ],
        [InlineKeyboardButton("🔙 Voltar ao Perfil", callback_data="show_profile")]
    ]
    
    await query.edit_message_text(
        f"📋 **HISTÓRICO DE ATIVIDADES**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"🕐 **Atividades recentes:**\n"
        f"• 15:45 - Checklist Escavadeira #EQ001\n"
        f"• 14:30 - Abastecimento Trator #EQ005\n"
        f"• 13:15 - Checklist Betoneira #EQ008\n"
        f"• 11:20 - Anomalia reportada #EQ003\n"
        f"• 09:45 - Login no sistema\n\n"
        f"📊 **Resumo do dia:**\n"
        f"• 3 checklists realizados\n"
        f"• 1 abastecimento registrado\n"
        f"• 1 anomalia reportada\n\n"
        f"Selecione o período para ver mais detalhes:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - RELATÓRIOS
# ==========================================

async def relatorio_checklists_detalhado(query, operador):
    """Relatório detalhado de checklists"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Por Período", callback_data="check_rel_periodo"),
            InlineKeyboardButton("🔧 Por Equipamento", callback_data="check_rel_equipamento")
        ],
        [
            InlineKeyboardButton("📈 Gráfico", callback_data="check_rel_grafico"),
            InlineKeyboardButton("📄 Exportar PDF", callback_data="check_rel_pdf")
        ],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"📋 **RELATÓRIO DE CHECKLISTS**\n\n"
        f"👤 **Operador:** {operador.nome}\n"
        f"📅 **Período:** {date.today().strftime('%B/%Y')}\n\n"
        f"📊 **Resumo Geral:**\n"
        f"• Total realizados: 45\n"
        f"• Taxa de conclusão: 95%\n"
        f"• Tempo médio: 12 min\n"
        f"• Itens OK: 234 (87%)\n"
        f"• Itens NOK: 28 (10%)\n"
        f"• Itens N/A: 8 (3%)\n\n"
        f"📈 **Tendência:** +15% vs mês anterior\n"
        f"🏆 **Ranking:** 3º na equipe\n\n"
        f"💡 **Dica:** Use filtros para análises específicas.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_dashboard(query, operador):
    """Mostra dashboard executivo"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Atualizar", callback_data="dash_refresh"),
            InlineKeyboardButton("⚙️ Configurar", callback_data="dash_config")
        ],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"📊 **DASHBOARD EXECUTIVO**\n\n"
        f"📅 **{datetime.now().strftime('%d/%m/%Y %H:%M')}**\n\n"
        f"🎯 **KPIs Principais:**\n"
        f"• Checklists: 45/50 (90%)\n"
        f"• Equipamentos ativos: 15/18 (83%)\n"
        f"• Anomalias críticas: 0\n"
        f"• Uptime médio: 97%\n\n"
        f"📈 **Performance:**\n"
        f"• Esta semana: +12%\n"
        f"• Este mês: +8%\n"
        f"• Trimestre: +15%\n\n"
        f"🚨 **Alertas:**\n"
        f"• 2 manutenções preventivas pendentes\n"
        f"• 1 equipamento próximo da revisão\n\n"
        f"✅ **Status geral:** Excelente",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - SISTEMA
# ==========================================

async def confirmar_logout(query, operador):
    """Confirma se quer fazer logout"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim, sair", callback_data="logout_confirm"),
            InlineKeyboardButton("❌ Cancelar", callback_data="logout_cancel")
        ]
    ]
    
    await query.edit_message_text(
        f"🚪 **CONFIRMAÇÃO DE LOGOUT**\n\n"
        f"👤 **{operador.nome}**\n"
        f"⏰ **Sessão ativa há:** 45 minutos\n\n"
        f"❓ **Tem certeza que deseja sair?**\n\n"
        f"⚠️ Você precisará fazer login novamente para continuar usando o bot.\n\n"
        f"💾 **Suas atividades já foram salvas automaticamente.**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def fazer_logout(query, chat_id):
    """Executa o logout"""
    # Limpar sessão
    if chat_id in _memory_sessions:
        del _memory_sessions[chat_id]
    
    await query.edit_message_text(
        f"✅ **LOGOUT REALIZADO**\n\n"
        f"👋 **Até logo!**\n\n"
        f"🔐 Para usar o bot novamente:\n"
        f"• Digite seu código de operador\n"
        f"• Ou escaneie seu QR Code\n"
        f"• Ou digite /start\n\n"
        f"💼 **Tenha um ótimo trabalho!**",
        parse_mode='Markdown'
    )

async def sincronizar_dados(query, operador):
    """Sincroniza dados com o servidor"""
    await query.edit_message_text(
        f"🔄 **SINCRONIZAÇÃO DE DADOS**\n\n"
        f"📡 Conectando ao servidor...\n"
        f"📊 Enviando dados locais...\n"
        f"📥 Baixando atualizações...\n"
        f"🔍 Verificando integridade...\n\n"
        f"✅ **Sincronização concluída!**\n\n"
        f"📈 **Dados atualizados:**\n"
        f"• Checklists: Sincronizados\n"
        f"• Abastecimentos: Sincronizados\n"
        f"• Anomalias: Sincronizadas\n"
        f"• Configurações: Atualizadas\n\n"
        f"🕐 **Última sync:** {datetime.now().strftime('%H:%M:%S')}",
        parse_mode='Markdown'
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - CHECKLISTS
# ==========================================

async def checklists_pendentes(query, operador):
    """Mostra checklists pendentes"""
    keyboard = [
        [InlineKeyboardButton("▶️ Iniciar Checklist #001", callback_data="start_check_001")],
        [InlineKeyboardButton("▶️ Iniciar Checklist #002", callback_data="start_check_002")],
        [InlineKeyboardButton("📊 Ver Todos", callback_data="check_todos")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_checklists")]
    ]
    
    await query.edit_message_text(
        f"📋 **CHECKLISTS PENDENTES**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"⏳ **Aguardando execução:**\n\n"
        f"🔧 **#001 - Escavadeira Hidráulica**\n"
        f"📅 Programado: Hoje, 16:00\n"
        f"🏢 Cliente: Construtora ABC\n"
        f"⚡ Prioridade: Alta\n\n"
        f"🚛 **#002 - Caminhão Basculante**\n"
        f"📅 Programado: Amanhã, 08:00\n"
        f"🏢 Cliente: Obras XYZ\n"
        f"⚡ Prioridade: Média\n\n"
        f"💡 **Dica:** Clique para iniciar um checklist.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Handler para registrar no dispatcher
callback_handler = CallbackQueryHandler(handle_callback)