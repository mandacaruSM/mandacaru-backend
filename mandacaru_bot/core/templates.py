# ===============================================
# ARQUIVO: mandacaru_bot/core/templates.py
# Templates de mensagens padronizadas
# SALVAR COMO: mandacaru_bot/core/templates.py
# ===============================================

from typing import Dict, Any
from datetime import datetime
from .utils import Formatters

class MessageTemplates:
    """Templates de mensagens padronizadas"""
    
    @staticmethod
    def welcome_template() -> str:
        """Template de boas-vindas"""
        return """🤖 **Bem-vindo ao Bot Mandacaru!**

🏢 Sistema de gestão empresarial integrado

🎯 **Funcionalidades disponíveis:**
• 📋 Checklist NR12
• ⛽ Controle de abastecimento  
• 🔧 Ordens de serviço
• 📱 Acesso via QR Code
• 💰 Relatórios financeiros

🔐 **Para começar, vamos fazer seu login...**"""
    
    @staticmethod
    def login_success_template(operador: Dict[str, Any]) -> str:
        """Template de login bem-sucedido"""
        return f"""✅ **Login realizado com sucesso!**

👤 **Operador:** {operador.get('nome', 'N/A')}
💼 **Função:** {operador.get('funcao', 'N/A')}
📅 **Data:** {datetime.now().strftime('%d/%m/%Y')}
🕐 **Horário:** {datetime.now().strftime('%H:%M')}

🎯 **Escolha uma opção no menu abaixo:**"""
    
    @staticmethod
    def error_template(titulo: str, descricao: str) -> str:
        """Template de erro"""
        return f"""❌ **{titulo}**

{descricao}

🔄 Tente novamente ou entre em contato com o suporte se o problema persistir."""
    
    @staticmethod
    def success_template(titulo: str, descricao: str) -> str:
        """Template de sucesso"""
        return f"""✅ **{titulo}**

{descricao}

📅 **Registrado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}"""
    
    @staticmethod
    def equipamento_info_template(equipamento: Dict[str, Any]) -> str:
        """Template de informações do equipamento"""
        nome = equipamento.get('nome', 'N/A')
        status = Formatters.formatar_status(equipamento.get('status_operacional', 'N/A'))
        horimetro = Formatters.formatar_horimetro(equipamento.get('horimetro_atual', 0))
        modelo = equipamento.get('modelo', 'N/A')
        
        return f"""🚜 **{nome}**

📊 **Status:** {status}
⏱️ **Horímetro:** {horimetro}
🏷️ **Modelo:** {modelo}
🆔 **ID:** {equipamento.get('id', 'N/A')}"""
    
    @staticmethod
    def abastecimento_template(abastecimento: Dict[str, Any]) -> str:
        """Template de abastecimento"""
        quantidade = abastecimento.get('quantidade_litros', 0)
        valor = abastecimento.get('valor_total', 0)
        preco_litro = valor / quantidade if quantidade > 0 else 0
        
        return f"""⛽ **Abastecimento Registrado**

📊 **Quantidade:** {quantidade:.1f} litros
💰 **Valor Total:** {Formatters.formatar_moeda(valor)}
💲 **Preço/Litro:** {Formatters.formatar_moeda(preco_litro)}
🚜 **Equipamento:** {abastecimento.get('equipamento_nome', 'N/A')}
👤 **Operador:** {abastecimento.get('operador_nome', 'N/A')}"""
    
    @staticmethod
    def ordem_servico_template(os: Dict[str, Any]) -> str:
        """Template de ordem de serviço"""
        return f"""🔧 **Ordem de Serviço #{os.get('id', 'N/A')}**

📊 **Status:** {Formatters.formatar_status(os.get('status', 'ABERTA'))}
🔧 **Tipo:** {os.get('tipo_problema', 'N/A')}
📝 **Descrição:** {os.get('descricao', 'N/A')}
🚜 **Equipamento:** {os.get('equipamento_nome', 'N/A')}
👤 **Solicitante:** {os.get('operador_nome', 'N/A')}"""
    
    @staticmethod
    def lista_vazia_template(tipo: str) -> str:
        """Template para listas vazias"""
        emoji_map = {
            'checklists': '📋',
            'equipamentos': '🚜',
            'abastecimentos': '⛽',
            'ordens_servico': '🔧'
        }
        
        emoji = emoji_map.get(tipo, '📄')
        
        return f"""{emoji} **Nenhum item encontrado**

Não há {tipo} disponíveis no momento.

🔄 Tente novamente mais tarde ou verifique os filtros aplicados."""
    
    @staticmethod
    def ajuda_template() -> str:
        """Template de ajuda"""
        return """❓ **Central de Ajuda**

🤖 **Como usar o bot:**
1. Faça login com /start
2. Use os botões do menu
3. Escaneie QR codes dos equipamentos

📱 **Comandos disponíveis:**
• /start - Fazer login
• /admin - Painel administrativo (apenas admins)

🎯 **Principais funcionalidades:**
• 📋 Checklist NR12 obrigatório
• ⛽ Registro de abastecimentos
• 🔧 Abertura de ordens de serviço
• 📊 Consulta de relatórios

📱 **QR Codes:**
Cada equipamento possui um QR code único. Ao escaneá-lo, você acessa diretamente as funções específicas daquele equipamento.

🆘 **Precisa de ajuda?**
Entre em contato com o suporte técnico:
📞 (11) 99999-9999
📧 suporte@mandacaru.com"""

class AdminTemplates:
    """Templates específicos para administradores"""
    
    @staticmethod
    def painel_admin_template(stats: Dict[str, Any]) -> str:
        """Template do painel administrativo"""
        return f"""🔑 **Painel Administrativo**

📊 **Estatísticas do Sistema:**
👥 Usuários ativos: {stats.get('usuarios_ativos', 0)}
📋 Checklists hoje: {stats.get('checklists_hoje', 0)}
⛽ Abastecimentos hoje: {stats.get('abastecimentos_hoje', 0)}
🔧 OS abertas: {stats.get('os_abertas', 0)}

🕐 **Última atualização:** {datetime.now().strftime('%H:%M')}"""
    
    @staticmethod
    def broadcast_template() -> str:
        """Template para broadcast"""
        return """📢 **Enviar Mensagem em Massa**

Digite a mensagem que deseja enviar para todos os usuários ativos do sistema.

⚠️ **Atenção:** A mensagem será enviada imediatamente para todos os operadores logados.

✏️ **Digite sua mensagem:**"""

# Exportar classes principais
__all__ = [
    'MessageTemplates',
    'AdminTemplates'
]