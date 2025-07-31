# =====================
# core/templates.py
# =====================

from typing import Dict, Any, Optional
from datetime import datetime
from core.utils import MessageFormatter

class MessageTemplates:
    """Templates de mensagens padronizadas"""
    
    @staticmethod
    def welcome_message(nome: str) -> str:
        """Mensagem de boas-vindas após login"""
        return f"""
🎉 **Bem-vindo ao Sistema Mandacaru!**

Olá, **{nome}**! 👋

Seu acesso foi liberado com sucesso. Use o menu abaixo para navegar pelos módulos disponíveis:

📋 **Checklist** - Verificações e inspeções
⛽ **Abastecimento** - Controle de combustível  
🔧 **Ordem de Serviço** - Solicitações de manutenção
💰 **Financeiro** - Consultas e relatórios
📱 **QR Code** - Geração de códigos
❓ **Ajuda** - Suporte e informações

💡 *Dica: Use o menu sempre que precisar navegar entre os módulos.*
        """.strip()
    
    @staticmethod
    def error_template(titulo: str, descricao: str, codigo_erro: Optional[str] = None) -> str:
        """Template para mensagens de erro"""
        message = f"❌ **{titulo}**\n\n{descricao}"
        if codigo_erro:
            message += f"\n\n🔍 *Código: {codigo_erro}*"
        return message
    
    @staticmethod
    def success_template(titulo: str, descricao: str, dados_extras: Optional[Dict] = None) -> str:
        """Template para mensagens de sucesso"""
        message = f"✅ **{titulo}**\n\n{descricao}"
        
        if dados_extras:
            message += "\n\n📊 **Detalhes:**"
            for chave, valor in dados_extras.items():
                message += f"\n• {chave}: {valor}"
        
        return message
    
    @staticmethod
    def info_template(titulo: str, items: Dict[str, Any]) -> str:
        """Template para exibição de informações"""
        message = f"ℹ️ **{titulo}**\n"
        
        for chave, valor in items.items():
            message += f"\n📌 **{chave}:** {valor}"
        
        return message
    
    @staticmethod
    def checklist_summary(checklist: Dict[str, Any]) -> str:
        """Template para resumo de checklist"""
        data_criacao = checklist.get('data_criacao', 'N/A')
        if data_criacao != 'N/A':
            try:
                data_formatada = MessageFormatter.formato_datetime_br(
                    datetime.fromisoformat(data_criacao)
                )
            except:
                data_formatada = data_criacao
        else:
            data_formatada = 'N/A'
        
        return f"""
📋 **Checklist #{checklist.get('id', 'N/A')}**

🏷️ **Tipo:** {checklist.get('tipo', 'N/A').title()}
📝 **Descrição:** {checklist.get('descricao', 'N/A')}
📊 **Status:** {MessageFormatter.status_emoji(checklist.get('status', ''))} {checklist.get('status', 'N/A').title()}
📅 **Criado em:** {data_formatada}
👤 **Operador:** {checklist.get('operador_nome', 'N/A')}
        """.strip()
    
    @staticmethod
    def os_summary(ordem_servico: Dict[str, Any]) -> str:
        """Template para resumo de ordem de serviço"""
        prioridade_emoji = {
            'baixa': '🟢',
            'media': '🟡', 
            'alta': '🟠',
            'critica': '🔴'
        }
        
        return f"""
🔧 **OS #{ordem_servico.get('id', 'N/A')}**

📋 **Título:** {ordem_servico.get('titulo', 'N/A')}
📝 **Descrição:** {MessageFormatter.truncar_texto(ordem_servico.get('descricao', 'N/A'), 100)}
{prioridade_emoji.get(ordem_servico.get('prioridade', '').lower(), '⚪')} **Prioridade:** {ordem_servico.get('prioridade', 'N/A').title()}
📊 **Status:** {MessageFormatter.status_emoji(ordem_servico.get('status', ''))} {ordem_servico.get('status', 'N/A').title()}
👤 **Solicitante:** {ordem_servico.get('solicitante_nome', 'N/A')}
        """.strip()
    
    @staticmethod
    def abastecimento_summary(abastecimento: Dict[str, Any]) -> str:
        """Template para resumo de abastecimento"""
        valor = abastecimento.get('valor_total', 0)
        valor_formatado = MessageFormatter.formato_moeda_br(float(valor)) if valor else 'N/A'
        
        return f"""
⛽ **Abastecimento #{abastecimento.get('id', 'N/A')}**

🚗 **Veículo:** {abastecimento.get('veiculo', 'N/A')}
⛽ **Combustível:** {abastecimento.get('tipo_combustivel', 'N/A')}
📊 **Litros:** {abastecimento.get('litros', 'N/A')}L
💰 **Valor:** {valor_formatado}
📅 **Data:** {abastecimento.get('data_abastecimento', 'N/A')}
📍 **Posto:** {abastecimento.get('posto', 'N/A')}
        """.strip()
    
    @staticmethod
    def help_menu() -> str:
        """Menu de ajuda completo"""
        return """
❓ **Central de Ajuda - Bot Mandacaru**

🔧 **Como usar o bot:**
1️⃣ Faça login com /start
2️⃣ Use o menu para navegar
3️⃣ Siga as instruções em tela

📋 **Módulos disponíveis:**

**📋 Checklist**
• Criar novos checklists
• Visualizar histórico
• Gerar relatórios

**⛽ Abastecimento**  
• Registrar abastecimentos
• Controlar consumo
• Acompanhar custos

**🔧 Ordem de Serviço**
• Criar solicitações
• Acompanhar status
• Histórico de manutenções

**💰 Financeiro**
• Consultar relatórios
• Acompanhar gastos
• Análises financeiras

**📱 QR Code**
• Gerar códigos
• Acessar informações

🆘 **Precisa de ajuda?**
Entre em contato com a equipe técnica ou use os comandos:
• /start - Fazer login
• /help - Esta ajuda
• /status - Status do sistema
        """.strip()
    
    @staticmethod
    def pagination_info(pagina_atual: int, total_paginas: int, total_itens: int) -> str:
        """Informações de paginação"""
        return f"📄 Página {pagina_atual} de {total_paginas} • Total: {total_itens} itens"
    
    @staticmethod
    def loading_message(acao: str) -> str:
        """Mensagem de carregamento"""
        return f"⏳ {acao}... Aguarde um momento."
    
    @staticmethod
    def confirmation_required(acao: str, detalhes: Optional[str] = None) -> str:
        """Template para confirmação de ação"""
        message = f"⚠️ **Confirmação necessária**\n\nVocê tem certeza que deseja {acao}?"
        if detalhes:
            message += f"\n\n📝 **Detalhes:** {detalhes}"
        message += "\n\n⚡ *Esta ação não pode ser desfeita.*"
        return message

class NotificationTemplates:
    """Templates para notificações"""
    
    @staticmethod
    def checklist_vencendo(checklist: Dict[str, Any], dias_restantes: int) -> str:
        """Notificação de checklist vencendo"""
        return f"""
⚠️ **Checklist Vencendo**

📋 **{checklist.get('tipo', 'Checklist').title()} #{checklist.get('id', 'N/A')}**
⏰ Vence em **{dias_restantes} dia(s)**

📝 {checklist.get('descricao', 'Sem descrição')}

🚨 Não esqueça de completar antes do prazo!
        """.strip()
    
    @staticmethod
    def os_atualizada(os: Dict[str, Any], novo_status: str) -> str:
        """Notificação de OS atualizada"""
        return f"""
🔔 **Ordem de Serviço Atualizada**

🔧 **OS #{os.get('id', 'N/A')}** - {os.get('titulo', 'Sem título')}
📊 **Novo status:** {MessageFormatter.status_emoji(novo_status)} {novo_status.title()}

✉️ Verifique os detalhes no sistema.
        """.strip()
    
    @staticmethod
    def sistema_manutencao(inicio: datetime, fim: datetime) -> str:
        """Notificação de manutenção do sistema"""
        inicio_str = MessageFormatter.formato_datetime_br(inicio)
        fim_str = MessageFormatter.formato_datetime_br(fim)
        
        return f"""
🔧 **Manutenção Programada**

⏰ **Início:** {inicio_str}
⏰ **Fim:** {fim_str}

Durante este período, o sistema pode ficar indisponível.

💡 *Planeje suas atividades com antecedência.*
        """.strip()

class ReportTemplates:
    """Templates para relatórios"""
    
    @staticmethod
    def checklist_report_header(periodo: str, total: int) -> str:
        """Cabeçalho do relatório de checklist"""
        return f"""
📊 **Relatório de Checklists**
📅 **Período:** {periodo}
📋 **Total:** {total} checklist(s)

━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
    
    @staticmethod
    def financial_summary(dados: Dict[str, Any]) -> str:
        """Resumo financeiro"""
        total_gastos = MessageFormatter.formato_moeda_br(dados.get('total_gastos', 0))
        media_mensal = MessageFormatter.formato_moeda_br(dados.get('media_mensal', 0))
        
        return f"""
💰 **Resumo Financeiro**

💳 **Total de Gastos:** {total_gastos}
📊 **Média Mensal:** {media_mensal}
📈 **Variação:** {dados.get('variacao_percentual', 0)}%

🏆 **Maior Gasto:** {dados.get('maior_gasto_categoria', 'N/A')}
💡 **Economia:** {dados.get('economia_sugerida', 'N/A')}
        """.strip()