# ===============================================
# ARQUIVO: mandacaru_bot/core/templates.py
# Templates de mensagens do bot
# ===============================================

from datetime import datetime
from typing import Dict, Any, List

class MessageTemplates:
    """Templates padronizados para mensagens do bot"""
    
    # ===============================================
    # TEMPLATES DE BOAS-VINDAS E INÍCIO
    # ===============================================
    
    @staticmethod
    def welcome_message() -> str:
        return """🤖 **Mandacaru Bot**

Seja bem-vindo ao sistema de automação da Mandacaru!

Para começar, preciso validar sua identidade.

📝 **Digite seu nome completo:**"""
    
    @staticmethod
    def auth_birth_date_request() -> str:
        return """🎂 **Validação de Segurança**

Para confirmar sua identidade, digite sua data de nascimento:

📅 **Formato:** DD/MM/AAAA
📝 **Exemplo:** 15/03/1990"""
    
    @staticmethod
    def auth_success(operador_nome: str) -> str:
        return f"""✅ **Autenticação Realizada**

Bem-vindo, **{operador_nome}**!

Você agora tem acesso a todas as funcionalidades do sistema."""
    
    @staticmethod
    def auth_failed() -> str:
        return """❌ **Falha na Autenticação**

Os dados informados não conferem ou você não tem permissão para usar o bot.

🔄 Digite /start para tentar novamente."""
    
    @staticmethod
    def operator_not_found() -> str:
        return """⚠️ **Operador Não Encontrado**

Não foi possível localizar um operador com esse nome.

📝 Verifique se digitou o nome corretamente
🔄 Digite /start para tentar novamente"""
    
    # ===============================================
    # TEMPLATES DE MENU
    # ===============================================
    
    @staticmethod
    def main_menu(operador_nome: str) -> str:
        return f"""🏠 **Menu Principal**

Olá, **{operador_nome}**!

Escolha uma das opções abaixo:"""
    
    @staticmethod
    def equipment_menu(equipamento_nome: str) -> str:
        return f"""🚜 **Equipamento Selecionado**

**{equipamento_nome}**

Selecione a ação desejada:"""
    
    # ===============================================
    # TEMPLATES DE CHECKLIST
    # ===============================================
    
    @staticmethod
    def checklist_list_header() -> str:
        return """📋 **Checklists Disponíveis**

Selecione um checklist para executar:"""
    
    @staticmethod
    def checklist_item_question(item_num: int, total: int, item_text: str) -> str:
        return f"""📋 **Checklist - Item {item_num}/{total}**

**{item_text}**

Como está este item?"""
    
    @staticmethod
    def checklist_completed(equipamento: str, total_items: int, aprovados: int) -> str:
        status_emoji = "✅" if aprovados == total_items else "⚠️"
        
        return f"""{status_emoji} **Checklist Finalizado**

**Equipamento:** {equipamento}
**Total de itens:** {total_items}
**Aprovados:** {aprovados}
**Reprovados:** {total_items - aprovados}

O checklist foi salvo no sistema."""
    
    @staticmethod
    def checklist_observation_request() -> str:
        return """📝 **Observação Adicional**

Deseja adicionar alguma observação sobre este item?

💡 Digite a observação ou clique em "Pular" para continuar."""
    
    # ===============================================
    # TEMPLATES DE ERRO E STATUS
    # ===============================================
    
    @staticmethod
    def error_generic() -> str:
        return """❌ **Erro Interno**

Ocorreu um erro no sistema. Tente novamente em alguns instantes.

Se o problema persistir, contate o administrador."""
    
    @staticmethod
    def error_api_connection() -> str:
        return """🔌 **Erro de Conexão**

Não foi possível conectar com o servidor.

Verifique sua conexão e tente novamente."""
    
    @staticmethod
    def unauthorized_access() -> str:
        return """🚫 **Acesso Não Autorizado**

Você precisa fazer login primeiro.

Digite /start para começar."""
    
    @staticmethod
    def feature_under_development() -> str:
        return """🚧 **Funcionalidade em Desenvolvimento**

Esta funcionalidade ainda está sendo desenvolvida.

Em breve estará disponível!"""
    
    # ===============================================
    # TEMPLATES DE SUCESSO
    # ===============================================
    
    @staticmethod
    def success_template(title: str, message: str) -> str:
        return f"""✅ **{title}**

{message}"""
    
    @staticmethod
    def info_template(title: str, message: str) -> str:
        return f"""ℹ️ **{title}**

{message}"""
    
    @staticmethod
    def warning_template(title: str, message: str) -> str:
        return f"""⚠️ **{title}**

{message}"""
    
    # ===============================================
    # TEMPLATES ADMINISTRATIVOS
    # ===============================================
    
    @staticmethod
    def admin_menu() -> str:
        return """⚙️ **Menu Administrativo**

Funcionalidades de administração:"""
    
    @staticmethod
    def system_status(stats: Dict[str, Any]) -> str:
        return f"""📊 **Status do Sistema**

**Sessões Ativas:** {stats.get('total_sessions', 0)}
**Usuários Autenticados:** {stats.get('authenticated_users', 0)}
**API Status:** {"✅ Online" if stats.get('api_status') else "❌ Offline"}
**Última Atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
    
    # ===============================================
    # TEMPLATES DE HELP
    # ===============================================
    
    @staticmethod
    def help_message() -> str:
        return """❓ **Central de Ajuda**

**Comandos Disponíveis:**
• `/start` - Iniciar/Reiniciar bot
• `/menu` - Voltar ao menu principal
• `/help` - Mostrar esta ajuda

**Como usar:**
1. Faça login com seu nome e data de nascimento
2. Escaneie o QR Code do equipamento
3. Execute os checklists necessários

**Suporte:**
Em caso de dúvidas, contate o administrador do sistema."""
    
    # ===============================================
    # FORMATADORES ESPECÍFICOS
    # ===============================================
    
    @staticmethod
    def format_equipment_list(equipamentos: List[Dict[str, Any]]) -> str:
        """Formata lista de equipamentos"""
        if not equipamentos:
            return "Nenhum equipamento disponível."
        
        texto = "🚜 **Equipamentos Disponíveis:**\n\n"
        
        for i, eq in enumerate(equipamentos[:10], 1):
            nome = eq.get('nome', 'Sem nome')
            status = eq.get('status_operacional', 'N/A')
            horimetro = eq.get('horimetro_atual', 0)
            
            texto += f"{i}. **{nome}**\n"
            texto += f"   Status: {status}\n"
            texto += f"   Horímetro: {horimetro}h\n\n"
        
        return texto
    
    @staticmethod
    def format_checklist_summary(checklist: Dict[str, Any]) -> str:
        """Formata resumo do checklist"""
        equipamento = checklist.get('equipamento_nome', 'N/A')
        data = checklist.get('data_checklist', 'N/A')
        status = checklist.get('status', 'N/A')
        
        return f"""📋 **Resumo do Checklist**

**Equipamento:** {equipamento}
**Data:** {data}
**Status:** {status}"""
    
    @staticmethod
    def format_time_ago(timestamp_str: str) -> str:
        """Formata tempo relativo"""
        try:
            from datetime import datetime
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timestamp.tzinfo)
            diff = now - timestamp
            
            if diff.days > 0:
                return f"{diff.days} dia(s) atrás"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} hora(s) atrás"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60} minuto(s) atrás"
            else:
                return "Agora há pouco"
        except:
            return "N/A"