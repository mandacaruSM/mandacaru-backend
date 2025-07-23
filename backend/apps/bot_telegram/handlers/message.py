# File: backend/apps/bot_telegram/handlers/message.py - VERSÃO INTERATIVA
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from backend.apps.operadores.models import Operador
from asgiref.sync import sync_to_async
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Usar dicionário simples em memória para sessões
_memory_sessions = {}

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de texto principal com mais interação"""
    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()
    
    # Verificar se o usuário está autenticado
    session = _memory_sessions.get(chat_id, {})
    
    if not session.get("autenticado"):
        # Tentar buscar operador por código
        operador = await sync_to_async(
            lambda: Operador.objects.filter(codigo__iexact=text, status="ATIVO", ativo_bot=True).first()
        )()

        if operador:
            # Atualizar último acesso
            await sync_to_async(operador.atualizar_ultimo_acesso)(chat_id=chat_id)
            
            # Salvar sessão
            _memory_sessions[chat_id] = {
                "autenticado": True,
                "operador_id": operador.id,
                "operador": operador,
                "login_time": datetime.now()
            }
            
            # Teclado baseado em permissões
            keyboard = gerar_teclado_principal(operador)
            
            await update.message.reply_text(
                f"✅ **Login realizado com sucesso!**\n\n"
                f"👤 **Operador:** {operador.nome}\n"
                f"💼 **Função:** {operador.funcao}\n"
                f"🏢 **Setor:** {operador.setor}\n"
                f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"🚀 **Agora você pode:**\n"
                f"• Escanear QR de equipamentos\n"
                f"• Realizar checklists NR12\n"
                f"• Registrar abastecimentos\n"
                f"• Reportar anomalias\n\n"
                f"📱 **Use os botões abaixo ou escaneie um QR Code!**",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                "❌ **Código inválido**\n\n"
                "Digite seu código de operador ou escaneie seu QR Code.\n\n"
                "💡 **Exemplo:** OP0001"
            )
        return

    # Usuário autenticado - processar comandos do menu
    operador = session.get('operador')
    
    if text == "👤 Meu Perfil":
        await mostrar_perfil_interativo(update, operador)
        
    elif text == "📊 Relatórios":
        await mostrar_relatorios_interativo(update, operador)
        
    elif text == "🔧 Sistema":
        await mostrar_sistema_interativo(update, operador)
        
    elif text == "❓ Ajuda":
        await mostrar_ajuda_interativa(update)
        
    elif text == "📷 Escanear QR Code":
        await update.message.reply_text(
            "📷 **Escaneamento de QR Code**\n\n"
            "📱 **Opções disponíveis:**\n"
            "• Envie uma **foto** do QR Code\n"
            "• Digite o **código** diretamente\n"
            "• Use um **link** do Telegram\n\n"
            "💡 **Dica:** Mantenha a câmera estável e com boa iluminação",
            parse_mode='Markdown'
        )
        
    elif text.startswith("Checklists") or text.startswith("checklists"):
        await mostrar_checklists_detalhado(update, operador)
        
    elif text.startswith("Abastecimentos") or text.startswith("abastecimentos"):
        await mostrar_abastecimentos_detalhado(update, operador)
        
    elif text.startswith("Anomalias") or text.startswith("anomalias"):
        await mostrar_anomalias_detalhado(update, operador)
        
    elif text.startswith("Equipamentos") or text.startswith("equipamentos"):
        await mostrar_equipamentos_detalhado(update, operador)
        
    else:
        # Comando não reconhecido - mostrar sugestões
        keyboard = gerar_teclado_principal(operador)
        await update.message.reply_text(
            f"🤔 **Comando não reconhecido**\n\n"
            f"Você digitou: `{text}`\n\n"
            f"💡 **Sugestões:**\n"
            f"• Use os botões do menu abaixo\n"
            f"• Escaneie um QR Code\n"
            f"• Digite o código de um equipamento\n"
            f"• Digite 'ajuda' para mais informações",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

async def mostrar_perfil_interativo(update: Update, operador):
    """Mostra perfil do operador com botões interativos"""
    
    # Estatísticas do operador
    hoje = date.today()
    # TODO: Buscar dados reais do banco
    stats = {
        'checklists_hoje': 3,
        'checklists_mes': 45,
        'abastecimentos_mes': 12,
        'anomalias_mes': 2
    }
    
    perfil_texto = (
        f"👤 **MEU PERFIL**\n\n"
        f"📝 **Nome:** {operador.nome}\n"
        f"🆔 **Código:** {operador.codigo}\n"
        f"💼 **Função:** {operador.funcao}\n"
        f"🏢 **Setor:** {operador.setor}\n"
        f"📱 **Chat ID:** {operador.chat_id_telegram or 'N/A'}\n"
        f"📅 **Admissão:** {operador.data_admissao.strftime('%d/%m/%Y') if operador.data_admissao else 'N/A'}\n\n"
        f"📊 **ESTATÍSTICAS DO MÊS:**\n"
        f"• Checklists hoje: {stats['checklists_hoje']}\n"
        f"• Checklists no mês: {stats['checklists_mes']}\n"
        f"• Abastecimentos: {stats['abastecimentos_mes']}\n"
        f"• Anomalias reportadas: {stats['anomalias_mes']}\n\n"
        f"✅ **PERMISSÕES:**\n"
    )
    
    if operador.pode_fazer_checklist:
        perfil_texto += "• ✅ Fazer checklists NR12\n"
    if operador.pode_registrar_abastecimento:
        perfil_texto += "• ⛽ Registrar abastecimentos\n"
    if operador.pode_reportar_anomalia:
        perfil_texto += "• 🚨 Reportar anomalias\n"
    if operador.pode_ver_relatorios:
        perfil_texto += "• 📊 Ver relatórios\n"
    
    # Botões interativos
    keyboard = [
        [InlineKeyboardButton("📊 Ver Estatísticas Detalhadas", callback_data="perfil_stats")],
        [InlineKeyboardButton("🔄 Atualizar Dados", callback_data="perfil_update")],
        [InlineKeyboardButton("📋 Histórico de Atividades", callback_data="perfil_history")],
        [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        perfil_texto,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_relatorios_interativo(update: Update, operador):
    """Mostra menu de relatórios mais interativo"""
    
    # Verificar permissão
    if not operador.pode_ver_relatorios:
        await update.message.reply_text(
            "🚫 **Acesso Negado**\n\n"
            "Você não tem permissão para visualizar relatórios.\n"
            "Entre em contato com seu supervisor.\n\n"
            "💡 **Permissões atuais:**\n"
            f"• Checklists: {'✅' if operador.pode_fazer_checklist else '❌'}\n"
            f"• Abastecimentos: {'✅' if operador.pode_registrar_abastecimento else '❌'}\n"
            f"• Anomalias: {'✅' if operador.pode_reportar_anomalia else '❌'}\n"
            f"• Relatórios: {'❌'}",
            parse_mode='Markdown'
        )
        return
    
    # Menu de relatórios mais detalhado
    keyboard = [
        [
            InlineKeyboardButton("📋 Checklists", callback_data="rel_checklists"),
            InlineKeyboardButton("⛽ Abastecimentos", callback_data="rel_abastecimentos")
        ],
        [
            InlineKeyboardButton("🚨 Anomalias", callback_data="rel_anomalias"),
            InlineKeyboardButton("🔧 Equipamentos", callback_data="rel_equipamentos")
        ],
        [
            InlineKeyboardButton("📈 Resumo Geral", callback_data="rel_resumo"),
            InlineKeyboardButton("📊 Dashboard", callback_data="rel_dashboard")
        ],
        [
            InlineKeyboardButton("📅 Por Período", callback_data="rel_periodo"),
            InlineKeyboardButton("🏢 Por Cliente", callback_data="rel_cliente")
        ],
        [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        f"📊 **CENTRAL DE RELATÓRIOS**\n\n"
        f"👤 **Operador:** {operador.nome}\n"
        f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"🔐 **Nível de acesso:** {'Administrador' if operador.funcao == 'CEO' else 'Operador'}\n\n"
        f"📋 **Relatórios disponíveis:**\n"
        f"Selecione o tipo de relatório que deseja visualizar.\n\n"
        f"💡 **Dica:** Use 'Por Período' para relatórios customizados.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_sistema_interativo(update: Update, operador):
    """Mostra opções do sistema"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Sincronizar Dados", callback_data="sys_sync"),
            InlineKeyboardButton("📊 Status Sistema", callback_data="sys_status")
        ],
        [
            InlineKeyboardButton("🚪 Fazer Logout", callback_data="sys_logout"),
            InlineKeyboardButton("⚙️ Configurações", callback_data="sys_config")
        ],
        [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        f"🔧 **SISTEMA**\n\n"
        f"👤 **Usuário:** {operador.nome}\n"
        f"⏰ **Sessão ativa há:** {_calcular_tempo_sessao(operador)}\n"
        f"📱 **Bot:** Mandacaru ERP v2.0\n"
        f"🔗 **Conexão:** Estável\n\n"
        f"⚙️ **Opções disponíveis:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_checklists_detalhado(update: Update, operador):
    """Mostra informações detalhadas sobre checklists"""
    # TODO: Buscar dados reais do banco
    keyboard = [
        [
            InlineKeyboardButton("📋 Pendentes", callback_data="check_pendentes"),
            InlineKeyboardButton("✅ Concluídos", callback_data="check_concluidos")
        ],
        [
            InlineKeyboardButton("📊 Estatísticas", callback_data="check_stats"),
            InlineKeyboardButton("🔍 Buscar", callback_data="check_buscar")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        f"📋 **CHECKLISTS REALIZADOS**\n\n"
        f"👤 **Operador:** {operador.nome}\n\n"
        f"📊 **Resumo:**\n"
        f"• Hoje: 3 checklists\n"
        f"• Esta semana: 18 checklists\n"
        f"• Este mês: 45 checklists\n\n"
        f"📈 **Status atual:**\n"
        f"• Pendentes: 2\n"
        f"• Em andamento: 1\n"
        f"• Concluídos: 42\n\n"
        f"⚡ **Taxa de conclusão:** 95%",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def gerar_teclado_principal(operador):
    """Gera teclado principal mais rico baseado nas permissões"""
    botoes = []
    
    # Primeira linha - sempre disponível
    botoes.append(["📷 Escanear QR Code"])
    
    # Segunda linha - baseada em permissões
    linha2 = []
    if operador.pode_ver_relatorios:
        linha2.append("📊 Relatórios")
    linha2.append("👤 Meu Perfil")
    
    if linha2:
        botoes.append(linha2)
    
    # Terceira linha - sistema
    botoes.append(["🔧 Sistema", "❓ Ajuda"])
    
    return ReplyKeyboardMarkup(botoes, resize_keyboard=True, one_time_keyboard=False)

def _calcular_tempo_sessao(operador):
    """Calcula tempo de sessão ativa"""
    # TODO: Implementar cálculo real
    return "25 min"

async def mostrar_ajuda_interativa(update: Update):
    """Mostra ajuda mais interativa"""
    keyboard = [
        [
            InlineKeyboardButton("🚀 Primeiros Passos", callback_data="help_start"),
            InlineKeyboardButton("📱 Como Usar", callback_data="help_usage")
        ],
        [
            InlineKeyboardButton("🔧 Solução de Problemas", callback_data="help_troubleshoot"),
            InlineKeyboardButton("📞 Contato", callback_data="help_contact")
        ],
        [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        "❓ **CENTRAL DE AJUDA**\n\n"
        "🤖 **Bot Mandacaru ERP v2.0**\n\n"
        "📚 **Guias disponíveis:**\n"
        "• Como fazer login\n"
        "• Como escanear QR Codes\n"
        "• Como realizar checklists\n"
        "• Como registrar abastecimentos\n"
        "• Como reportar anomalias\n\n"
        "🆘 **Precisa de ajuda específica?**\n"
        "Escolha uma opção abaixo:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Funções auxiliares para relatórios detalhados
async def mostrar_abastecimentos_detalhado(update: Update, operador):
    """Informações detalhadas sobre abastecimentos"""
    keyboard = [
        [InlineKeyboardButton("📊 Ver Detalhes", callback_data="abast_detalhes")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        f"⛽ **ABASTECIMENTOS REGISTRADOS**\n\n"
        f"📊 **Este mês:** 12 abastecimentos\n"
        f"💰 **Valor total:** R$ 2.450,00\n"
        f"📈 **Média por abastecimento:** R$ 204,17\n\n"
        f"🔧 **Equipamentos abastecidos:** 8\n"
        f"📅 **Último registro:** Hoje, 14:30",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_anomalias_detalhado(update: Update, operador):
    """Informações detalhadas sobre anomalias"""
    keyboard = [
        [
            InlineKeyboardButton("🚨 Críticas", callback_data="anom_criticas"),
            InlineKeyboardButton("⚠️ Moderadas", callback_data="anom_moderadas")
        ],
        [
            InlineKeyboardButton("📊 Estatísticas", callback_data="anom_stats"),
            InlineKeyboardButton("📝 Nova Anomalia", callback_data="anom_nova")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        f"🚨 **ANOMALIAS REPORTADAS**\n\n"
        f"📊 **Este mês:** 2 anomalias\n"
        f"🔴 **Críticas:** 0\n"
        f"🟡 **Moderadas:** 1\n"
        f"🟢 **Leves:** 1\n\n"
        f"✅ **Resolvidas:** 1\n"
        f"⏳ **Pendentes:** 1\n\n"
        f"📅 **Última anomalia:** 15/07/2025",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_equipamentos_detalhado(update: Update, operador):
    """Informações detalhadas sobre equipamentos utilizados"""
    keyboard = [
        [
            InlineKeyboardButton("🔧 Mais Utilizados", callback_data="equip_mais_usados"),
            InlineKeyboardButton("📊 Por Cliente", callback_data="equip_por_cliente")
        ],
        [
            InlineKeyboardButton("⏰ Histórico", callback_data="equip_historico"),
            InlineKeyboardButton("🔍 Buscar", callback_data="equip_buscar")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")]
    ]
    
    await update.message.reply_text(
        f"🔧 **EQUIPAMENTOS UTILIZADOS**\n\n"
        f"📊 **Total acessado:** 15 equipamentos\n"
        f"⭐ **Mais utilizado:** Escavadeira Hidráulica\n"
        f"📅 **Último acesso:** Hoje, 15:45\n\n"
        f"🏢 **Por cliente:**\n"
        f"• Cliente A: 8 equipamentos\n"
        f"• Cliente B: 5 equipamentos\n"
        f"• Cliente C: 2 equipamentos\n\n"
        f"🔄 **Status operacional:** 100%",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Handler para registrar no dispatcher
text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)