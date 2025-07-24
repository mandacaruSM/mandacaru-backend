# File: backend/apps/bot_telegram/handlers/callback.py - VERSÃO CORRIGIDA
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime, date
from asgiref.sync import sync_to_async

# Importar sessões do módulo utils
from ..utils.sessions import get_session, save_session, clear_session, get_memory_sessions

logger = logging.getLogger(__name__)

async def handle_help_login(query):
    """Mostra ajuda para login"""
    await query.edit_message_text(
        "❓ **AJUDA PARA LOGIN**\n\n"
        "🔐 **Como fazer login:**\n"
        "1. Escaneie o QR Code do seu cartão\n"
        "2. OU digite seu código (ex: OP0001)\n\n"
        "📱 **Problemas com QR Code:**\n"
        "• Certifique-se que está bem visível\n"
        "• Evite reflexos e sombras\n"
        "• Mantenha a câmera estável\n\n"
        "🆘 **Precisa de ajuda?**\n"
        "Contate o suporte técnico.",
        parse_mode='Markdown'
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - AJUDA
# ==========================================

async def ajuda_primeiros_passos(query):
    """Mostra guia de primeiros passos"""
    keyboard = [
        [InlineKeyboardButton("🔐 Ajuda para Login", callback_data="help_login")],
        [InlineKeyboardButton("📷 Como Escanear QR", callback_data="help_qr")],
        [InlineKeyboardButton("📋 Primeiro Checklist", callback_data="help_checklist")],
        [InlineKeyboardButton("🔙 Voltar à Ajuda", callback_data="show_help")]
    ]
    
    await query.edit_message_text(
        "🚀 **PRIMEIROS PASSOS**\n\n"
        "👋 **Bem-vindo ao Mandacaru ERP!**\n\n"
        "📝 **Passos para começar:**\n"
        "1. Faça login com seu cartão QR ou código\n"
        "2. Escaneie o QR de um equipamento\n"
        "3. Escolha a ação desejada\n"
        "4. Siga as instruções na tela\n\n"
        "🎯 **Dicas importantes:**\n"
        "• Mantenha o cartão sempre consigo\n"
        "• Use boa iluminação para QR Codes\n"
        "• Salve os dados frequentemente\n"
        "• Em caso de dúvida, use a ajuda\n\n"
        "📚 **Selecione um tópico para mais detalhes:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ajuda_como_usar(query):
    """Mostra como usar o sistema"""
    keyboard = [
        [InlineKeyboardButton("📋 Fazer Checklist", callback_data="help_how_checklist")],
        [InlineKeyboardButton("⛽ Registrar Abastecimento", callback_data="help_how_abast")],
        [InlineKeyboardButton("🚨 Reportar Anomalia", callback_data="help_how_anomalia")],
        [InlineKeyboardButton("📊 Ver Relatórios", callback_data="help_how_relatorios")],
        [InlineKeyboardButton("🔙 Voltar à Ajuda", callback_data="show_help")]
    ]
    
    await query.edit_message_text(
        "📱 **COMO USAR O SISTEMA**\n\n"
        "🎮 **Navegação básica:**\n"
        "• Use os botões para navegar\n"
        "• Toque em 'Voltar' para retornar\n"
        "• Menu principal sempre disponível\n\n"
        "📷 **Escaneando QR Codes:**\n"
        "• Aponte a câmera para o QR\n"
        "• Aguarde o reconhecimento automático\n"
        "• Mantenha distância adequada\n\n"
        "💾 **Salvando dados:**\n"
        "• Dados são salvos automaticamente\n"
        "• Confirme antes de finalizar\n"
        "• Use sincronização quando offline\n\n"
        "🔧 **Funções principais:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ajuda_solucao_problemas(query):
    """Mostra soluções para problemas comuns"""
    keyboard = [
        [InlineKeyboardButton("📷 QR Code não funciona", callback_data="help_qr_problem")],
        [InlineKeyboardButton("🔐 Problemas de login", callback_data="help_login_problem")],
        [InlineKeyboardButton("📱 App está lento", callback_data="help_slow_problem")],
        [InlineKeyboardButton("💾 Dados não salvam", callback_data="help_save_problem")],
        [InlineKeyboardButton("🔙 Voltar à Ajuda", callback_data="show_help")]
    ]
    
    await query.edit_message_text(
        "🔧 **SOLUÇÃO DE PROBLEMAS**\n\n"
        "❗ **Problemas mais comuns:**\n\n"
        "📷 **QR Code não lê:**\n"
        "• Limpe a câmera\n"
        "• Melhore a iluminação\n"
        "• Aproxime ou afaste o celular\n"
        "• Verifique se o QR não está danificado\n\n"
        "🔐 **Não consegue fazer login:**\n"
        "• Verifique seu código de operador\n"
        "• Tente escanear o QR do cartão\n"
        "• Contate o supervisor se persistir\n\n"
        "📱 **App está lento:**\n"
        "• Feche outros aplicativos\n"
        "• Verifique a conexão com internet\n"
        "• Reinicie o aplicativo\n\n"
        "💡 **Selecione um problema específico:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ajuda_contato(query):
    """Mostra informações de contato"""
    keyboard = [
        [InlineKeyboardButton("📞 Ligar para Suporte", callback_data="help_call_support")],
        [InlineKeyboardButton("💬 Chat com TI", callback_data="help_chat_ti")],
        [InlineKeyboardButton("📧 Enviar Email", callback_data="help_email_support")],
        [InlineKeyboardButton("🔙 Voltar à Ajuda", callback_data="show_help")]
    ]
    
    await query.edit_message_text(
        "📞 **CONTATO E SUPORTE**\n\n"
        "🆘 **Precisa de ajuda técnica?**\n\n"
        "📱 **Suporte Técnico:**\n"
        "• Telefone: (11) 99999-9999\n"
        "• Horário: Segunda a Sexta, 8h às 18h\n"
        "• Emergências: 24h disponível\n\n"
        "💻 **Equipe de TI:**\n"
        "• Email: ti@mandacaru.com.br\n"
        "• Chat interno: @suporte_ti\n"
        "• Resposta em até 2 horas\n\n"
        "🏢 **Supervisão:**\n"
        "• Contate seu supervisor direto\n"
        "• Ou use o ramal 2000\n\n"
        "📋 **Ao reportar problemas, informe:**\n"
        "• Seu código de operador\n"
        "• Descrição do problema\n"
        "• Horário que ocorreu\n"
        "• Prints da tela (se possível)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - SISTEMA
# ==========================================

async def mostrar_status_sistema(query, operador):
    """Mostra status detalhado do sistema"""
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar Status", callback_data="sys_refresh")],
        [InlineKeyboardButton("🧹 Limpar Cache", callback_data="sys_clear_cache")],
        [InlineKeyboardButton("🔙 Voltar ao Sistema", callback_data="show_system")]
    ]
    
    await query.edit_message_text(
        f"📊 **STATUS DO SISTEMA**\n\n"
        f"👤 **Operador:** {operador.nome}\n"
        f"🕐 **Última atualização:** {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"🌐 **Conectividade:**\n"
        f"• Servidor: 🟢 Online\n"
        f"• API: 🟢 Funcionando\n"
        f"• Banco de dados: 🟢 Disponível\n"
        f"• Sincronização: 🟢 Ativa\n\n"
        f"📱 **Status local:**\n"
        f"• Cache: 15.2 MB\n"
        f"• Dados pendentes: 0\n"
        f"• Última sync: {datetime.now().strftime('%H:%M')}\n\n"
        f"🔋 **Performance:**\n"
        f"• Latência: 45ms\n"
        f"• Tempo de resposta: Bom\n"
        f"• Uso de memória: Normal",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_configuracoes(query, operador):
    """Mostra configurações do sistema"""
    keyboard = [
        [InlineKeyboardButton("🔔 Notificações", callback_data="config_notifications")],
        [InlineKeyboardButton("🎨 Tema", callback_data="config_theme")],
        [InlineKeyboardButton("🌐 Idioma", callback_data="config_language")],
        [InlineKeyboardButton("🔐 Privacidade", callback_data="config_privacy")],
        [InlineKeyboardButton("🔙 Voltar ao Sistema", callback_data="show_system")]
    ]
    
    await query.edit_message_text(
        f"⚙️ **CONFIGURAÇÕES**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"🔧 **Configurações atuais:**\n\n"
        f"🔔 **Notificações:**\n"
        f"• Lembrete de checklists: ✅ Ativo\n"
        f"• Anomalias críticas: ✅ Ativo\n"
        f"• Relatórios semanais: ❌ Inativo\n\n"
        f"🎨 **Interface:**\n"
        f"• Tema: Padrão\n"
        f"• Tamanho da fonte: Médio\n"
        f"• Modo escuro: ❌ Desligado\n\n"
        f"🌐 **Sistema:**\n"
        f"• Idioma: Português (BR)\n"
        f"• Fuso horário: GMT-3\n"
        f"• Sync automática: ✅ Ativa\n\n"
        f"💡 **Selecione uma opção para personalizar:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cancelar_logout(query, operador):
    """Cancela o logout e volta ao menu"""
    keyboard = [
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="menu_principal")],
        [InlineKeyboardButton("🔧 Sistema", callback_data="show_system")]
    ]
    
    await query.edit_message_text(
        f"✅ **LOGOUT CANCELADO**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"🔐 **Sessão mantida ativa**\n\n"
        f"💼 Você continua logado no sistema e pode prosseguir com suas atividades normalmente.\n\n"
        f"🕐 **Tempo de sessão:** Renovado\n"
        f"🔒 **Status:** Autenticado\n\n"
        f"🚀 **O que deseja fazer agora?**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - CHECKLISTS COMPLEMENTARES
# ==========================================

async def checklists_concluidos(query, operador):
    """Mostra checklists concluídos"""
    keyboard = [
        [InlineKeyboardButton("📄 Ver Detalhes #045", callback_data="view_check_045")],
        [InlineKeyboardButton("📄 Ver Detalhes #044", callback_data="view_check_044")],
        [InlineKeyboardButton("📊 Estatísticas", callback_data="check_stats")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_checklists")]
    ]
    
    await query.edit_message_text(
        f"✅ **CHECKLISTS CONCLUÍDOS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📋 **Concluídos hoje:**\n\n"
        f"✅ **#045 - Escavadeira Hidráulica**\n"
        f"🕐 Concluído: 14:30\n"
        f"🏢 Cliente: Construtora ABC\n"
        f"⭐ Resultado: 28/30 itens OK\n\n"
        f"✅ **#044 - Caminhão Basculante**\n"
        f"🕐 Concluído: 10:15\n"
        f"🏢 Cliente: Obras XYZ\n"
        f"⭐ Resultado: 25/25 itens OK\n\n"
        f"📊 **Resumo do dia:**\n"
        f"• Total concluídos: 2\n"
        f"• Taxa de conformidade: 95%\n"
        f"• Tempo médio: 12 minutos",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def checklists_estatisticas(query, operador):
    """Mostra estatísticas de checklists"""
    keyboard = [
        [InlineKeyboardButton("📈 Gráfico Mensal", callback_data="check_grafico_mes")],
        [InlineKeyboardButton("📊 Comparar Períodos", callback_data="check_comparar")],
        [InlineKeyboardButton("🏆 Ranking da Equipe", callback_data="check_ranking")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_checklists")]
    ]
    
    await query.edit_message_text(
        f"📊 **ESTATÍSTICAS DE CHECKLISTS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📅 **Este mês ({datetime.now().strftime('%B/%Y')}):**\n"
        f"• Total realizados: 45\n"
        f"• Meta: 50 (90% atingido)\n"
        f"• Média diária: 2.1\n"
        f"• Taxa de conformidade: 95%\n\n"
        f"📈 **Tendências:**\n"
        f"• Comparado ao mês anterior: +15%\n"
        f"• Melhoria na qualidade: +8%\n"
        f"• Tempo médio: -2 minutos\n\n"
        f"🏆 **Sua posição:**\n"
        f"• Ranking na equipe: 3º lugar\n"
        f"• Melhor categoria: Eficiência\n"
        f"• Pontos: 847 (de 1000)\n\n"
        f"🎯 **Próxima meta:** 50 checklists",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def checklists_buscar(query, operador):
    """Interface para buscar checklists específicos"""
    keyboard = [
        [InlineKeyboardButton("📅 Por Data", callback_data="buscar_check_data")],
        [InlineKeyboardButton("🔧 Por Equipamento", callback_data="buscar_check_equip")],
        [InlineKeyboardButton("🏢 Por Cliente", callback_data="buscar_check_cliente")],
        [InlineKeyboardButton("📋 Por Número", callback_data="buscar_check_numero")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_checklists")]
    ]
    
    await query.edit_message_text(
        f"🔍 **BUSCAR CHECKLISTS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📋 **Opções de busca disponíveis:**\n\n"
        f"📅 **Por Data:**\n"
        f"• Buscar por dia específico\n"
        f"• Filtrar por período\n\n"
        f"🔧 **Por Equipamento:**\n"
        f"• Histórico de um equipamento\n"
        f"• Comparar diferentes máquinas\n\n"
        f"🏢 **Por Cliente:**\n"
        f"• Todos os checklists de um cliente\n"
        f"• Análise de conformidade\n\n"
        f"📋 **Por Número:**\n"
        f"• Localizar checklist específico\n"
        f"• Ver detalhes completos\n\n"
        f"🔍 **Selecione o tipo de busca:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - ABASTECIMENTOS
# ==========================================

async def abastecimentos_detalhes(query, operador):
    """Mostra detalhes dos abastecimentos"""
    keyboard = [
        [InlineKeyboardButton("⛽ Registrar Novo", callback_data="abast_novo")],
        [InlineKeyboardButton("📊 Estatísticas", callback_data="abast_stats")],
        [InlineKeyboardButton("📈 Consumo Médio", callback_data="abast_consumo")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"⛽ **DETALHES DE ABASTECIMENTOS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📊 **Resumo do mês:**\n"
        f"• Total de abastecimentos: 23\n"
        f"• Volume total: 1.250 litros\n"
        f"• Custo total: R$ 7.125,00\n"
        f"• Preço médio/litro: R$ 5,70\n\n"
        f"🚛 **Por equipamento:**\n"
        f"• Escavadeiras: 8 abastecimentos\n"
        f"• Caminhões: 12 abastecimentos\n"
        f"• Tratores: 3 abastecimentos\n\n"
        f"📈 **Eficiência:**\n"
        f"• Consumo médio: 54 L/dia\n"
        f"• Economia vs meta: +8%\n"
        f"• Melhor rendimento: Trator #005\n\n"
        f"💡 **Próximos vencimentos:**\n"
        f"• Escavadeira #001: 2 dias\n"
        f"• Caminhão #003: 5 dias",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - ANOMALIAS
# ==========================================

async def anomalias_criticas(query, operador):
    """Mostra anomalias críticas"""
    keyboard = [
        [InlineKeyboardButton("🚨 Ver Anomalia #A001", callback_data="view_anom_A001")],
        [InlineKeyboardButton("⚠️ Reportar Nova", callback_data="anom_nova")],
        [InlineKeyboardButton("📊 Estatísticas", callback_data="anom_stats")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_anomalias")]
    ]
    
    await query.edit_message_text(
        f"🚨 **ANOMALIAS CRÍTICAS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"⚠️ **ATENÇÃO: 1 anomalia crítica ativa**\n\n"
        f"🚨 **#A001 - CRÍTICA**\n"
        f"📍 Equipamento: Escavadeira #EQ003\n"
        f"⚡ Problema: Vazamento hidráulico\n"
        f"🕐 Reportado: Hoje, 13:45\n"
        f"👤 Por: {operador.nome}\n"
        f"📋 Status: ⏳ Aguardando manutenção\n\n"
        f"🔧 **Ação necessária:**\n"
        f"• PARAR operação imediatamente\n"
        f"• Isolar área de risco\n"
        f"• Aguardar equipe de manutenção\n\n"
        f"📞 **Contatos:**\n"
        f"• Manutenção: (11) 99999-1234\n"
        f"• Supervisão: (11) 99999-5678\n\n"
        f"⏰ **Prazo máximo:** 2 horas",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def anomalias_moderadas(query, operador):
    """Mostra anomalias moderadas"""
    keyboard = [
        [InlineKeyboardButton("⚠️ Ver Todas (5)", callback_data="view_all_moderate")],
        [InlineKeyboardButton("📋 Filtrar por Tipo", callback_data="filter_anom_type")],
        [InlineKeyboardButton("📊 Estatísticas", callback_data="anom_stats")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_anomalias")]
    ]
    
    await query.edit_message_text(
        f"⚠️ **ANOMALIAS MODERADAS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📊 **5 anomalias moderadas ativas:**\n\n"
        f"⚠️ **#A002 - MODERADA**\n"
        f"🔧 Ruído excessivo no motor\n"
        f"📍 Caminhão #EQ007\n"
        f"🕐 Reportado: Ontem, 16:20\n\n"
        f"⚠️ **#A003 - MODERADA**\n"
        f"🛠️ Desgaste nos pneus\n"
        f"📍 Trator #EQ012\n"
        f"🕐 Reportado: Hoje, 08:15\n\n"
        f"⚠️ **#A004 - MODERADA**\n"
        f"💡 Luz de advertência acesa\n"
        f"📍 Betoneira #EQ009\n"
        f"🕐 Reportado: Hoje, 11:30\n\n"
        f"📈 **Estatísticas:**\n"
        f"• Total este mês: 12\n"
        f"• Resolvidas: 7\n"
        f"• Tempo médio resolução: 3 dias",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def anomalias_estatisticas(query, operador):
    """Mostra estatísticas de anomalias"""
    keyboard = [
        [InlineKeyboardButton("📈 Gráfico Mensal", callback_data="anom_grafico")],
        [InlineKeyboardButton("🔧 Por Equipamento", callback_data="anom_por_equip")],
        [InlineKeyboardButton("📊 Por Categoria", callback_data="anom_por_categoria")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_anomalias")]
    ]
    
    await query.edit_message_text(
        f"📊 **ESTATÍSTICAS DE ANOMALIAS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📅 **Este mês ({datetime.now().strftime('%B/%Y')}):**\n"
        f"• Total reportadas: 18\n"
        f"• Críticas: 1 (6%)\n"
        f"• Moderadas: 5 (28%)\n"
        f"• Leves: 12 (66%)\n\n"
        f"✅ **Status de resolução:**\n"
        f"• Resolvidas: 12 (67%)\n"
        f"• Em andamento: 5 (28%)\n"
        f"• Pendentes: 1 (5%)\n\n"
        f"⏱️ **Tempo médio de resolução:**\n"
        f"• Críticas: 4 horas\n"
        f"• Moderadas: 2 dias\n"
        f"• Leves: 1 semana\n\n"
        f"📈 **Tendência:** -20% vs mês anterior\n"
        f"🏆 **Sua contribuição:** 8 anomalias reportadas",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def nova_anomalia(query, operador):
    """Interface para reportar nova anomalia"""
    keyboard = [
        [InlineKeyboardButton("📷 Anexar Foto", callback_data="anom_foto")],
        [InlineKeyboardButton("🎤 Gravar Áudio", callback_data="anom_audio")],
        [InlineKeyboardButton("📝 Descrição Texto", callback_data="anom_texto")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_anomalias")]
    ]
    
    await query.edit_message_text(
        f"⚠️ **REPORTAR NOVA ANOMALIA**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📋 **Passos para reportar:**\n\n"
        f"1️⃣ **Identifique o equipamento**\n"
        f"• Escaneie o QR Code do equipamento\n"
        f"• Ou informe o código manualmente\n\n"
        f"2️⃣ **Classifique a gravidade**\n"
        f"• 🚨 Crítica: Para operação imediata\n"
        f"• ⚠️ Moderada: Afeta performance\n"
        f"• 💡 Leve: Observação preventiva\n\n"
        f"3️⃣ **Descreva o problema**\n"
        f"• Seja específico e detalhado\n"
        f"• Anexe fotos se possível\n"
        f"• Grave áudio se necessário\n\n"
        f"📸 **Como você quer reportar?**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - EQUIPAMENTOS
# ==========================================

async def equipamentos_mais_usados(query, operador):
    """Mostra equipamentos mais utilizados"""
    keyboard = [
        [InlineKeyboardButton("🔧 Ver Detalhes #EQ001", callback_data="equip_details_001")],
        [InlineKeyboardButton("🔧 Ver Detalhes #EQ005", callback_data="equip_details_005")],
        [InlineKeyboardButton("📊 Ranking Completo", callback_data="equip_ranking")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_equipamentos")]
    ]
    
    await query.edit_message_text(
        f"🏆 **EQUIPAMENTOS MAIS UTILIZADOS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📊 **Top 5 este mês:**\n\n"
        f"🥇 **#EQ001 - Escavadeira Hidráulica**\n"
        f"⏰ Tempo operação: 180 horas\n"
        f"🏢 Cliente: Construtora ABC\n"
        f"📋 Checklists: 15\n"
        f"⛽ Abastecimentos: 8\n\n"
        f"🥈 **#EQ005 - Caminhão Basculante**\n"
        f"⏰ Tempo operação: 165 horas\n"
        f"🏢 Cliente: Obras XYZ\n"
        f"📋 Checklists: 12\n"
        f"⛽ Abastecimentos: 6\n\n"
        f"🥉 **#EQ012 - Trator Agrícola**\n"
        f"⏰ Tempo operação: 145 horas\n"
        f"🏢 Cliente: Fazenda Verde\n"
        f"📋 Checklists: 10\n"
        f"⛽ Abastecimentos: 5\n\n"
        f"📈 **Tendência:** +22% vs mês anterior",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def equipamentos_por_cliente(query, operador):
    """Mostra equipamentos agrupados por cliente"""
    keyboard = [
        [InlineKeyboardButton("🏢 Construtora ABC (8)", callback_data="cliente_abc")],
        [InlineKeyboardButton("🏢 Obras XYZ (5)", callback_data="cliente_xyz")],
        [InlineKeyboardButton("🏢 Fazenda Verde (3)", callback_data="cliente_verde")],
        [InlineKeyboardButton("📊 Relatório Detalhado", callback_data="equip_rel_detalhado")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_equipamentos")]
    ]
    
    await query.edit_message_text(
        f"🏢 **EQUIPAMENTOS POR CLIENTE**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📊 **Distribuição atual:**\n\n"
        f"🏗️ **Construtora ABC**\n"
        f"• 8 equipamentos ativos\n"
        f"• 3 escavadeiras, 3 caminhões, 2 betoneiras\n"
        f"• 95% de disponibilidade\n"
        f"• Contrato até: Dez/2025\n\n"
        f"🏗️ **Obras XYZ**\n"
        f"• 5 equipamentos ativos\n"
        f"• 2 escavadeiras, 2 caminhões, 1 rolo\n"
        f"• 88% de disponibilidade\n"
        f"• Contrato até: Jun/2025\n\n"
        f"🌱 **Fazenda Verde**\n"
        f"• 3 equipamentos ativos\n"
        f"• 2 tratores, 1 colheitadeira\n"
        f"• 92% de disponibilidade\n"
        f"• Contrato até: Mar/2025\n\n"
        f"📈 **Total:** 16 equipamentos em operação",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def equipamentos_historico(query, operador):
    """Mostra histórico de equipamentos"""
    keyboard = [
        [InlineKeyboardButton("📅 Esta Semana", callback_data="hist_equip_semana")],
        [InlineKeyboardButton("📅 Este Mês", callback_data="hist_equip_mes")],
        [InlineKeyboardButton("📅 Último Trimestre", callback_data="hist_equip_trimestre")],
        [InlineKeyboardButton("📊 Comparar Períodos", callback_data="hist_equip_comparar")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_equipamentos")]
    ]
    
    await query.edit_message_text(
        f"📋 **HISTÓRICO DE EQUIPAMENTOS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📅 **Atividades recentes:**\n\n"
        f"🕐 **Hoje:**\n"
        f"• 12 checklists realizados\n"
        f"• 4 abastecimentos registrados\n"
        f"• 1 anomalia reportada\n"
        f"• 16 equipamentos operando\n\n"
        f"📊 **Esta semana:**\n"
        f"• 68 checklists realizados\n"
        f"• 23 abastecimentos registrados\n"
        f"• 5 anomalias reportadas\n"
        f"• 2 manutenções preventivas\n\n"
        f"📈 **Performance:**\n"
        f"• Disponibilidade média: 94%\n"
        f"• Tempo de inatividade: 18 horas\n"
        f"• Eficiência operacional: +15%\n\n"
        f"🔍 **Selecione o período para análise:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def equipamentos_buscar(query, operador):
    """Interface para buscar equipamentos"""
    keyboard = [
        [InlineKeyboardButton("🔢 Por Código", callback_data="buscar_equip_codigo")],
        [InlineKeyboardButton("🏷️ Por Tipo", callback_data="buscar_equip_tipo")],
        [InlineKeyboardButton("🏢 Por Cliente", callback_data="buscar_equip_cliente")],
        [InlineKeyboardButton("📍 Por Localização", callback_data="buscar_equip_local")],
        [InlineKeyboardButton("📊 Filtros Avançados", callback_data="buscar_equip_filtros")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="rel_equipamentos")]
    ]
    
    await query.edit_message_text(
        f"🔍 **BUSCAR EQUIPAMENTOS**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📋 **Opções de busca:**\n\n"
        f"🔢 **Por Código:**\n"
        f"• Digite o código do equipamento\n"
        f"• Ex: EQ001, EQ005, etc.\n\n"
        f"🏷️ **Por Tipo:**\n"
        f"• Escavadeiras, Caminhões, Tratores\n"
        f"• Betoneiras, Rolos, etc.\n\n"
        f"🏢 **Por Cliente:**\n"
        f"• Todos equipamentos de um cliente\n"
        f"• Análise de utilização\n\n"
        f"📍 **Por Localização:**\n"
        f"• Equipamentos em uma obra\n"
        f"• Filtrar por proximidade\n\n"
        f"📊 **Total cadastrado:** 45 equipamentos\n"
        f"✅ **Ativos:** 16 equipamentos\n\n"
        f"🔍 **Como você quer buscar?**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# FUNÇÕES DOS CALLBACKS - RELATÓRIOS COMPLEMENTARES
# ==========================================

async def relatorio_abastecimentos_detalhado(query, operador):
    """Relatório detalhado de abastecimentos"""
    keyboard = [
        [InlineKeyboardButton("⛽ Por Combustível", callback_data="abast_por_combustivel")],
        [InlineKeyboardButton("🚛 Por Equipamento", callback_data="abast_por_equipamento")],
        [InlineKeyboardButton("💰 Análise de Custos", callback_data="abast_custos")],
        [InlineKeyboardButton("📈 Gráfico de Consumo", callback_data="abast_grafico")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"⛽ **RELATÓRIO DE ABASTECIMENTOS**\n\n"
        f"👤 **{operador.nome}**\n"
        f"📅 **Período:** {datetime.now().strftime('%B/%Y')}\n\n"
        f"📊 **Resumo Geral:**\n"
        f"• Total de abastecimentos: 78\n"
        f"• Volume total: 4.250 litros\n"
        f"• Custo total: R$ 24.225,00\n"
        f"• Preço médio/litro: R$ 5,70\n\n"
        f"⛽ **Por tipo de combustível:**\n"
        f"• Diesel: 3.850L (91%)\n"
        f"• Gasolina: 400L (9%)\n\n"
        f"📈 **Eficiência:**\n"
        f"• Consumo médio: 137L/dia\n"
        f"• Economia vs orçado: +12%\n"
        f"• Melhor rendimento: Trator #012\n\n"
        f"💡 **Recomendações:**\n"
        f"• Agrupar abastecimentos para economia\n"
        f"• Monitorar consumo da Escavadeira #003",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def relatorio_anomalias_detalhado(query, operador):
    """Relatório detalhado de anomalias"""
    keyboard = [
        [InlineKeyboardButton("🚨 Críticas", callback_data="rel_anom_criticas")],
        [InlineKeyboardButton("⚠️ Moderadas", callback_data="rel_anom_moderadas")],
        [InlineKeyboardButton("💡 Preventivas", callback_data="rel_anom_preventivas")],
        [InlineKeyboardButton("📊 Análise de Causas", callback_data="rel_anom_causas")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"🚨 **RELATÓRIO DE ANOMALIAS**\n\n"
        f"👤 **{operador.nome}**\n"
        f"📅 **Período:** {datetime.now().strftime('%B/%Y')}\n\n"
        f"📊 **Resumo Geral:**\n"
        f"• Total de anomalias: 24\n"
        f"• Críticas: 2 (8%)\n"
        f"• Moderadas: 8 (33%)\n"
        f"• Leves: 14 (59%)\n\n"
        f"✅ **Status de resolução:**\n"
        f"• Resolvidas: 19 (79%)\n"
        f"• Em andamento: 4 (17%)\n"
        f"• Pendentes: 1 (4%)\n\n"
        f"⏱️ **Tempo médio resolução:**\n"
        f"• Críticas: 3,5 horas\n"
        f"• Moderadas: 1,8 dias\n"
        f"• Leves: 4,2 dias\n\n"
        f"📈 **Tendência:** -15% vs mês anterior\n"
        f"🏆 **Equipamento mais confiável:** Trator #012",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def relatorio_equipamentos_detalhado(query, operador):
    """Relatório detalhado de equipamentos"""
    keyboard = [
        [InlineKeyboardButton("📊 Disponibilidade", callback_data="rel_equip_disponibilidade")],
        [InlineKeyboardButton("🔧 Manutenções", callback_data="rel_equip_manutencoes")],
        [InlineKeyboardButton("💰 Custos Operacionais", callback_data="rel_equip_custos")],
        [InlineKeyboardButton("📈 Performance", callback_data="rel_equip_performance")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"🔧 **RELATÓRIO DE EQUIPAMENTOS**\n\n"
        f"👤 **{operador.nome}**\n"
        f"📅 **Período:** {datetime.now().strftime('%B/%Y')}\n\n"
        f"📊 **Frota Ativa:**\n"
        f"• Total de equipamentos: 16\n"
        f"• Em operação: 15 (94%)\n"
        f"• Em manutenção: 1 (6%)\n"
        f"• Disponibilidade média: 96%\n\n"
        f"⏰ **Horas de operação:**\n"
        f"• Total acumulado: 2.340 horas\n"
        f"• Média por equipamento: 146h\n"
        f"• Mais utilizado: Escavadeira #001 (180h)\n\n"
        f"🔧 **Manutenções:**\n"
        f"• Preventivas realizadas: 8\n"
        f"• Corretivas necessárias: 3\n"
        f"• Próximos vencimentos: 5\n\n"
        f"💰 **Custos do mês:** R$ 45.780,00\n"
        f"📈 **Eficiência:** +18% vs meta",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def relatorio_resumo_geral(query, operador):
    """Relatório resumo geral das operações"""
    keyboard = [
        [InlineKeyboardButton("📊 Dashboard Executivo", callback_data="rel_dashboard")],
        [InlineKeyboardButton("📈 Análise de Tendências", callback_data="rel_tendencias")],
        [InlineKeyboardButton("💰 Análise Financeira", callback_data="rel_financeiro")],
        [InlineKeyboardButton("📄 Exportar PDF", callback_data="rel_export_pdf")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"📊 **RESUMO GERAL DAS OPERAÇÕES**\n\n"
        f"👤 **{operador.nome}**\n"
        f"📅 **Período:** {datetime.now().strftime('%B/%Y')}\n\n"
        f"🎯 **KPIs Principais:**\n"
        f"• Checklists realizados: 145 (97% da meta)\n"
        f"• Disponibilidade da frota: 96%\n"
        f"• Anomalias críticas: 2 (Meta: <5)\n"
        f"• Eficiência operacional: 94%\n\n"
        f"📈 **Performance vs mês anterior:**\n"
        f"• Checklists: +15%\n"
        f"• Disponibilidade: +3%\n"
        f"• Redução de anomalias: -20%\n"
        f"• Economia de combustível: +8%\n\n"
        f"🏆 **Destaques:**\n"
        f"• Zero acidentes de trabalho\n"
        f"• 100% conformidade NR12\n"
        f"• Redução de custos de 12%\n"
        f"• Cliente mais satisfeito: Construtora ABC\n\n"
        f"⚠️ **Pontos de atenção:**\n"
        f"• Escavadeira #003 com alto consumo\n"
        f"• 5 equipamentos próximos da revisão",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def relatorio_por_periodo(query, operador):
    """Interface para relatórios por período"""
    keyboard = [
        [InlineKeyboardButton("📅 Última Semana", callback_data="rel_semana")],
        [InlineKeyboardButton("📅 Último Mês", callback_data="rel_mes")],
        [InlineKeyboardButton("📅 Último Trimestre", callback_data="rel_trimestre")],
        [InlineKeyboardButton("📅 Período Personalizado", callback_data="rel_custom")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"📅 **RELATÓRIOS POR PERÍODO**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"🗓️ **Períodos disponíveis:**\n\n"
        f"📅 **Última Semana:**\n"
        f"• 7 dias de dados\n"
        f"• Análise de tendências diárias\n"
        f"• Comparação com semana anterior\n\n"
        f"📅 **Último Mês:**\n"
        f"• 30 dias de dados\n"
        f"• Relatório mensal completo\n"
        f"• KPIs e métricas principais\n\n"
        f"📅 **Último Trimestre:**\n"
        f"• 90 dias de dados\n"
        f"• Análise de sazonalidade\n"
        f"• Tendências de longo prazo\n\n"
        f"📅 **Personalizado:**\n"
        f"• Defina suas próprias datas\n"
        f"• Comparações específicas\n"
        f"• Análises direcionadas\n\n"
        f"🔍 **Selecione o período desejado:**",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def relatorio_por_cliente(query, operador):
    """Relatórios específicos por cliente"""
    keyboard = [
        [InlineKeyboardButton("🏗️ Construtora ABC", callback_data="rel_cliente_abc")],
        [InlineKeyboardButton("🏗️ Obras XYZ", callback_data="rel_cliente_xyz")],
        [InlineKeyboardButton("🌱 Fazenda Verde", callback_data="rel_cliente_verde")],
        [InlineKeyboardButton("📊 Comparativo Clientes", callback_data="rel_comparativo")],
        [InlineKeyboardButton("🔙 Voltar aos Relatórios", callback_data="show_reports")]
    ]
    
    await query.edit_message_text(
        f"🏢 **RELATÓRIOS POR CLIENTE**\n\n"
        f"👤 **{operador.nome}**\n\n"
        f"📊 **Clientes ativos:**\n\n"
        f"🏗️ **Construtora ABC**\n"
        f"• 8 equipamentos\n"
        f"• 95% disponibilidade\n"
        f"• R$ 28.500 faturamento/mês\n"
        f"• Satisfação: ⭐⭐⭐⭐⭐\n\n"
        f"🏗️ **Obras XYZ**\n"
        f"• 5 equipamentos\n"
        f"• 88% disponibilidade\n"
        f"• R$ 18.750 faturamento/mês\n"
        f"• Satisfação: ⭐⭐⭐⭐\n\n"
        f"🌱 **Fazenda Verde**\n"
        f"• 3 equipamentos\n"
        f"• 92% disponibilidade\n"
        f"• R$ 12.300 faturamento/mês\n"
        f"• Satisfação: ⭐⭐⭐⭐⭐\n\n"
        f"💰 **Faturamento total:** R$ 59.550/mês\n"
        f"📈 **Crescimento médio:** +12% ao mês",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================================
# CALLBACK HANDLER PRINCIPAL
# ==========================================

# Adicionar callback para help_login que estava referenciado mas não implementado
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa callbacks de botões inline de forma interativa"""
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat.id)
    session = get_session(chat_id) or {}
    
    if not session.get('autenticado') and query.data not in ['help_login', 'help_start', 'help_usage', 'help_troubleshoot', 'help_contact']:
        await query.edit_message_text(
            "❌ **Sessão expirada**\n\n"
            "Faça login novamente digitando seu código de operador ou escaneando seu QR Code.",
            parse_mode='Markdown'
        )
        return

    data = query.data
    operador = session.get('operador')
    
    logger.info(f"Callback recebido: {data} do operador {operador.codigo if operador else 'não autenticado'}")

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
    elif data == "help_login":
        await handle_help_login(query)
    
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
        )'help_start', 'help_usage', 'help_troubleshoot', 'help_contact']:
        await query.edit_message_text(
            "❌ **Sessão expirada**\n\n"
            "Faça login novamente digitando seu código de operador ou escaneando seu QR Code.",
            parse_mode='Markdown'
        )
        return

    data = query.data
    operador = session.get('operador')
    
    logger.info(f"Callback recebido: {data} do operador {operador.codigo if operador else 'não autenticado'}")

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
    elif data == "help_login":
        await handle_help_login(query)
    
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
        f"🚀 **O que deseja fazer?**",
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
        f"📈 **Dados atualizados:**\n"
        f"• Checklists: Sincronizados\n"
        f"• Abastecimentos: Sincronizados\n"
        f"• Anomalias: Sincronizadas\n"
        f"• Configurações: Atualizadas\n\n"
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
        f"💡 **Dica:** Use filtros para análises específicas.\n"
        f"Escolha uma opção abaixo:",
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