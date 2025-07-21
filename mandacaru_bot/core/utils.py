# =====================
# core/utils.py
# =====================

import re
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

class Validators:
    """Classe com métodos de validação"""
    
    @staticmethod
    def validar_data(data_str: str, formato: str = "%d/%m/%Y") -> Optional[date]:
        """
        Valida uma string de data e retorna um objeto date
        """
        try:
            return datetime.strptime(data_str, formato).date()
        except ValueError:
            return None
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida formato de telefone brasileiro"""
        # Remove caracteres não numéricos
        numeros = re.sub(r'\D', '', telefone)
        # Verifica se tem 10 ou 11 dígitos
        return len(numeros) in [10, 11] and numeros.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9'))
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não é uma sequência de números iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial):
            soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Verifica primeiro dígito
        if int(cpf[9]) != calcular_digito(cpf[:9]):
            return False
        
        # Verifica segundo dígito
        if int(cpf[10]) != calcular_digito(cpf[:10]):
            return False
        
        return True
    
    @staticmethod
    def validar_numero_positivo(valor_str: str) -> Optional[float]:
        """Valida e converte string para número positivo"""
        try:
            valor = float(valor_str.replace(',', '.'))
            return valor if valor > 0 else None
        except ValueError:
            return None

class KeyboardBuilder:
    """Classe para construir teclados do Telegram"""
    
    @staticmethod
    def menu_principal() -> ReplyKeyboardMarkup:
        """Constrói o teclado do menu principal"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📋 Checklist"), KeyboardButton(text="⛽ Abastecimento")],
                [KeyboardButton(text="🔧 Ordem de Serviço"), KeyboardButton(text="💰 Financeiro")],
                [KeyboardButton(text="📱 QR Code"), KeyboardButton(text="❓ Ajuda")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    @staticmethod
    def confirmar_cancelar() -> InlineKeyboardMarkup:
        """Teclado simples de confirmação"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Confirmar", callback_data="confirmar"),
                    InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar")
                ]
            ]
        )
    
    @staticmethod
    def sim_nao() -> InlineKeyboardMarkup:
        """Teclado Sim/Não"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Sim", callback_data="sim"),
                    InlineKeyboardButton(text="❌ Não", callback_data="nao")
                ]
            ]
        )
    
    @staticmethod
    def paginacao(pagina_atual: int, total_paginas: int, callback_prefix: str) -> InlineKeyboardMarkup:
        """Constrói teclado de paginação"""
        botoes = []
        
        if pagina_atual > 1:
            botoes.append(InlineKeyboardButton(text="⬅️ Anterior", callback_data=f"{callback_prefix}_{pagina_atual-1}"))
        
        botoes.append(InlineKeyboardButton(text=f"{pagina_atual}/{total_paginas}", callback_data="pagina_info"))
        
        if pagina_atual < total_paginas:
            botoes.append(InlineKeyboardButton(text="Próxima ➡️", callback_data=f"{callback_prefix}_{pagina_atual+1}"))
        
        return InlineKeyboardMarkup(inline_keyboard=[botoes])

class MessageFormatter:
    """Classe para formatação de mensagens"""
    
    @staticmethod
    def formato_data_br(data_obj: date) -> str:
        """Formata data para padrão brasileiro"""
        return data_obj.strftime("%d/%m/%Y")
    
    @staticmethod
    def formato_datetime_br(datetime_obj: datetime) -> str:
        """Formata datetime para padrão brasileiro"""
        return datetime_obj.strftime("%d/%m/%Y às %H:%M")
    
    @staticmethod
    def formato_moeda_br(valor: float) -> str:
        """Formata valor monetário para padrão brasileiro"""
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def truncar_texto(texto: str, limite: int = 100) -> str:
        """Trunca texto se exceder o limite"""
        return texto if len(texto) <= limite else texto[:limite-3] + "..."
    
    @staticmethod
    def status_emoji(status: str) -> str:
        """Retorna emoji baseado no status"""
        emojis = {
            "pendente": "⏳",
            "em_andamento": "🔄", 
            "concluido": "✅",
            "cancelado": "❌",
            "aprovado": "✅",
            "rejeitado": "❌",
            "ativo": "🟢",
            "inativo": "🔴"
        }
        return emojis.get(status.lower(), "⚪")

class DataProcessor:
    """Classe para processamento de dados"""
    
    @staticmethod
    def paginar_lista(lista: List[Any], pagina: int, itens_por_pagina: int = 10) -> Dict[str, Any]:
        """Pagina uma lista de itens"""
        total_itens = len(lista)
        total_paginas = (total_itens + itens_por_pagina - 1) // itens_por_pagina
        
        inicio = (pagina - 1) * itens_por_pagina
        fim = inicio + itens_por_pagina
        
        return {
            "itens": lista[inicio:fim],
            "pagina_atual": pagina,
            "total_paginas": total_paginas,
            "total_itens": total_itens,
            "tem_proxima": pagina < total_paginas,
            "tem_anterior": pagina > 1
        }
    
    @staticmethod
    def filtrar_por_data(lista: List[Dict], campo_data: str, data_inicio: date, data_fim: Optional[date] = None) -> List[Dict]:
        """Filtra lista por intervalo de datas"""
        if data_fim is None:
            data_fim = data_inicio
        
        resultado = []
        for item in lista:
            try:
                data_item = datetime.fromisoformat(item[campo_data]).date()
                if data_inicio <= data_item <= data_fim:
                    resultado.append(item)
            except (KeyError, ValueError):
                continue
        
        return resultado
    
    @staticmethod
    def agrupar_por_campo(lista: List[Dict], campo: str) -> Dict[str, List[Dict]]:
        """Agrupa lista por valor de um campo"""
        grupos = {}
        for item in lista:
            chave = item.get(campo, "Sem categoria")
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(item)
        return grupos

class ErrorMessages:
    """Mensagens de erro padronizadas"""
    
    ERRO_GENERICO = "❌ Ocorreu um erro inesperado. Tente novamente."
    ERRO_CONEXAO = "❌ Erro de conexão. Verifique sua internet e tente novamente."
    ERRO_AUTENTICACAO = "🔒 Você precisa estar autenticado. Digite /start para fazer login."
    ERRO_PERMISSAO = "❌ Você não tem permissão para realizar esta ação."
    ERRO_DADOS_INVALIDOS = "❌ Dados inválidos. Verifique as informações e tente novamente."
    ERRO_NAO_ENCONTRADO = "❌ Item não encontrado."
    ERRO_TIMEOUT = "⏱️ Operação expirou. Tente novamente."
    
    @staticmethod
    def erro_validacao(campo: str) -> str:
        return f"❌ {campo} inválido. Verifique o formato e tente novamente."

class SuccessMessages:
    """Mensagens de sucesso padronizadas"""
    
    OPERACAO_SUCESSO = "✅ Operação realizada com sucesso!"
    DADOS_SALVOS = "✅ Dados salvos com sucesso!"
    DADOS_ATUALIZADOS = "✅ Dados atualizados com sucesso!"
    DADOS_REMOVIDOS = "✅ Dados removidos com sucesso!"
    
    @staticmethod
    def criado_sucesso(item: str) -> str:
        return f"✅ {item} criado com sucesso!"
    
    @staticmethod
    def atualizado_sucesso(item: str) -> str:
        return f"✅ {item} atualizado com sucesso!"