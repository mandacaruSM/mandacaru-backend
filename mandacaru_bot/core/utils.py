# ===============================================
# ARQUIVO: mandacaru_bot/core/utils.py
# Utilitários e validadores
# SALVAR COMO: mandacaru_bot/core/utils.py
# ===============================================

import re
import logging
from datetime import datetime, date
from typing import Optional, Any, Dict, List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class Validators:
    """Classe com validadores de dados"""
    
    @staticmethod
    def validar_nome(nome: str) -> bool:
        """
        Valida nome do operador
        
        Args:
            nome: Nome a ser validado
            
        Returns:
            True se válido
        """
        if not nome or not isinstance(nome, str):
            return False
        
        nome = nome.strip()
        return len(nome) >= 3 and not any(char.isdigit() for char in nome)
    
    @staticmethod
    def validar_data_nascimento(data_texto: str) -> Optional[date]:
        """
        Valida e converte data de nascimento
        
        Args:
            data_texto: Data em texto (DD/MM/AAAA)
            
        Returns:
            Objeto date se válido, None se inválido
        """
        try:
            # Tentar formato DD/MM/AAAA
            data = datetime.strptime(data_texto.strip(), '%d/%m/%Y').date()
            
            # Validar se não é futura
            if data > date.today():
                return None
            
            # Validar idade razoável (entre 16 e 100 anos)
            idade = (date.today() - data).days // 365
            if idade < 16 or idade > 100:
                return None
            
            return data
            
        except ValueError:
            return None
    
    @staticmethod
    def validar_valor_monetario(valor_texto: str) -> Optional[float]:
        """
        Valida valor monetário
        
        Args:
            valor_texto: Valor em texto
            
        Returns:
            Float se válido, None se inválido
        """
        try:
            valor = float(valor_texto.replace(',', '.'))
            return valor if valor > 0 else None
        except ValueError:
            return None
    
    @staticmethod
    def validar_quantidade(quantidade_texto: str) -> Optional[float]:
        """
        Valida quantidade (litros, etc)
        
        Args:
            quantidade_texto: Quantidade em texto
            
        Returns:
            Float se válido, None se inválido
        """
        try:
            quantidade = float(quantidade_texto.replace(',', '.'))
            return quantidade if quantidade > 0 else None
        except ValueError:
            return None
    
    @staticmethod
    def validar_horimetro(horimetro_texto: str) -> Optional[float]:
        """
        Valida horímetro
        
        Args:
            horimetro_texto: Horímetro em texto
            
        Returns:
            Float se válido, None se inválido
        """
        try:
            horimetro = float(horimetro_texto.replace(',', '.'))
            # Horímetro deve ser positivo e razoável (máximo 100.000h)
            return horimetro if 0 <= horimetro <= 100000 else None
        except ValueError:
            return None
    
    @staticmethod
    def validar_uuid(uuid_texto: str) -> bool:
        """
        Valida formato UUID
        
        Args:
            uuid_texto: UUID em texto
            
        Returns:
            True se válido
        """
        pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        return bool(re.match(pattern, uuid_texto.lower()))

class Formatters:
    """Classe com formatadores de dados"""
    
    @staticmethod
    def formatar_moeda(valor: float) -> str:
        """
        Formata valor monetário
        
        Args:
            valor: Valor numérico
            
        Returns:
            Valor formatado (R$ 1.234,56)
        """
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def formatar_data(data: date) -> str:
        """
        Formata data para exibição
        
        Args:
            data: Objeto date
            
        Returns:
            Data formatada (DD/MM/AAAA)
        """
        return data.strftime('%d/%m/%Y')
    
    @staticmethod
    def formatar_datetime(dt: datetime) -> str:
        """
        Formata datetime para exibição
        
        Args:
            dt: Objeto datetime
            
        Returns:
            Datetime formatado (DD/MM/AAAA HH:MM)
        """
        return dt.strftime('%d/%m/%Y %H:%M')
    
    @staticmethod
    def formatar_horimetro(horas: float) -> str:
        """
        Formata horímetro
        
        Args:
            horas: Horas numéricas
            
        Returns:
            Horímetro formatado (1.234,5h)
        """
        return f"{horas:,.1f}h".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def formatar_status(status: str) -> str:
        """
        Formata status para exibição
        
        Args:
            status: Status em texto
            
        Returns:
            Status formatado com emoji
        """
        status_map = {
            'DISPONIVEL': '✅ Disponível',
            'EM_USO': '🔄 Em Uso',
            'MANUTENCAO': '🔧 Manutenção',
            'INATIVO': '❌ Inativo',
            'PENDENTE': '⏳ Pendente',
            'CONCLUIDO': '✅ Concluído',
            'CANCELADO': '❌ Cancelado',
            'ABERTA': '🔓 Aberta',
            'FECHADA': '🔒 Fechada'
        }
        return status_map.get(status.upper(), status)

class KeyboardBuilder:
    """Classe para construir teclados inline"""
    
    @staticmethod
    def confirmar_cancelar() -> InlineKeyboardMarkup:
        """Cria teclado de confirmação"""
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Confirmar", callback_data="confirmar"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def sim_nao() -> InlineKeyboardMarkup:
        """Cria teclado sim/não"""
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Sim", callback_data="sim"),
                InlineKeyboardButton(text="❌ Não", callback_data="nao")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def voltar_menu() -> InlineKeyboardMarkup:
        """Cria botão para voltar ao menu"""
        keyboard = [
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

class MessageUtils:
    """Utilitários para mensagens"""
    
    @staticmethod
    def truncar_texto(texto: str, max_length: int = 4000) -> str:
        """
        Trunca texto para não exceder limite do Telegram
        
        Args:
            texto: Texto a truncar
            max_length: Comprimento máximo
            
        Returns:
            Texto truncado
        """
        if len(texto) <= max_length:
            return texto
        
        return texto[:max_length - 3] + "..."
    
    @staticmethod
    def escapar_markdown(texto: str) -> str:
        """
        Escapa caracteres especiais do Markdown
        
        Args:
            texto: Texto a escapar
            
        Returns:
            Texto escapado
        """
        caracteres_especiais = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in caracteres_especiais:
            texto = texto.replace(char, f'\\{char}')
        return texto
    
    @staticmethod
    def criar_lista_numerada(itens: List[str], max_itens: int = 10) -> str:
        """
        Cria lista numerada
        
        Args:
            itens: Lista de itens
            max_itens: Máximo de itens a mostrar
            
        Returns:
            Lista formatada
        """
        resultado = []
        for i, item in enumerate(itens[:max_itens], 1):
            resultado.append(f"{i}. {item}")
        
        if len(itens) > max_itens:
            resultado.append(f"... e mais {len(itens) - max_itens} itens")
        
        return "\n".join(resultado)

# Exportar classes principais
__all__ = [
    'Validators',
    'Formatters', 
    'KeyboardBuilder',
    'MessageUtils'
]