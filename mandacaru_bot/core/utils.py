# ===============================================
# ARQUIVO: mandacaru_bot/core/utils.py
# Funções utilitárias do bot
# ===============================================

import re
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from .config import ADMIN_IDS, MAX_MESSAGE_LENGTH

logger = logging.getLogger(__name__)

# ===============================================
# VALIDADORES
# ===============================================

class Validators:
    """Classe com validadores diversos"""
    
    @staticmethod
    def validar_data(data_str: str) -> Optional[date]:
        """Valida e converte string de data no formato DD/MM/AAAA"""
        try:
            return datetime.strptime(data_str.strip(), '%d/%m/%Y').date()
        except ValueError:
            return None
    
    @staticmethod
    def validar_nome(nome: str) -> bool:
        """Valida se o nome tem formato válido"""
        if not nome or len(nome.strip()) < 3:
            return False
        
        # Verificar se contém pelo menos duas palavras
        palavras = nome.strip().split()
        return len(palavras) >= 2
    
    @staticmethod
    def validar_horimetro(valor: str) -> Optional[float]:
        """Valida e converte valor de horímetro"""
        try:
            valor_limpo = valor.replace(',', '.').strip()
            horimetro = float(valor_limpo)
            return horimetro if horimetro >= 0 else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validar_quantidade(valor: str) -> Optional[float]:
        """Valida e converte quantidade (combustível, etc.)"""
        try:
            valor_limpo = valor.replace(',', '.').strip()
            quantidade = float(valor_limpo)
            return quantidade if quantidade > 0 else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """Verifica se o usuário é administrador"""
        return user_id in ADMIN_IDS

# ===============================================
# FORMATADORES
# ===============================================

class Formatters:
    """Classe com formatadores diversos"""
    
    @staticmethod
    def formatar_data(data: date) -> str:
        """Formata data para exibição (DD/MM/AAAA)"""
        return data.strftime('%d/%m/%Y')
    
    @staticmethod
    def formatar_data_hora(data_hora: datetime) -> str:
        """Formata data e hora para exibição"""
        return data_hora.strftime('%d/%m/%Y %H:%M')
    
    @staticmethod
    def formatar_horimetro(horimetro: float) -> str:
        """Formata horímetro para exibição"""
        return f"{horimetro:,.1f}h".replace(',', '.')
    
    @staticmethod
    def formatar_quantidade(quantidade: float, unidade: str = "L") -> str:
        """Formata quantidade com unidade"""
        return f"{quantidade:,.1f} {unidade}".replace(',', '.')
    
    @staticmethod
    def formatar_valor_monetario(valor: float) -> str:
        """Formata valor monetário"""
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def truncar_texto(texto: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
        """Trunca texto se necessário"""
        if len(texto) <= max_length:
            return texto
        return texto[:max_length-3] + "..."
    
    @staticmethod
    def capitalizar_nome(nome: str) -> str:
        """Capitaliza nome próprio corretamente"""
        palavras_menores = ['da', 'de', 'do', 'das', 'dos', 'e', 'em', 'na', 'no']
        palavras = nome.lower().split()
        
        resultado = []
        for i, palavra in enumerate(palavras):
            if i == 0 or palavra not in palavras_menores:
                resultado.append(palavra.capitalize())
            else:
                resultado.append(palavra)
        
        return ' '.join(resultado)

# ===============================================
# PROCESSADORES DE TEXTO
# ===============================================

class TextProcessors:
    """Processadores de texto e mensagens"""
    
    @staticmethod
    def extrair_uuid_qr(texto: str) -> Optional[str]:
        """Extrai UUID de QR code do texto"""
        # Procurar por padrão UUID
        padrao_uuid = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        match = re.search(padrao_uuid, texto.lower())
        return match.group(0) if match else None
    
    @staticmethod
    def limpar_texto(texto: str) -> str:
        """Remove caracteres especiais e normaliza texto"""
        # Remove quebras de linha excessivas
        texto = re.sub(r'\n\s*\n', '\n\n', texto)
        
        # Remove espaços no início e fim
        texto = texto.strip()
        
        return texto
    
    @staticmethod
    def extrair_comando_start(texto: str) -> Optional[str]:
        """Extrai parâmetro do comando /start"""
        match = re.match(r'/start\s+(.+)', texto.strip())
        return match.group(1).strip() if match else None
    
    @staticmethod
    def dividir_mensagem_longa(texto: str, max_length: int = MAX_MESSAGE_LENGTH) -> List[str]:
        """Divide mensagem longa em partes menores"""
        if len(texto) <= max_length:
            return [texto]
        
        partes = []
        linhas = texto.split('\n')
        parte_atual = ""
        
        for linha in linhas:
            # Se a linha sozinha já é maior que o limite
            if len(linha) > max_length:
                # Adicionar parte atual se não estiver vazia
                if parte_atual:
                    partes.append(parte_atual.strip())
                    parte_atual = ""
                
                # Dividir a linha grande em pedaços menores
                for i in range(0, len(linha), max_length - 10):
                    partes.append(linha[i:i + max_length - 10])
                continue
            
            # Se adicionar esta linha ultrapassar o limite
            if len(parte_atual) + len(linha) + 1 > max_length:
                partes.append(parte_atual.strip())
                parte_atual = linha
            else:
                if parte_atual:
                    parte_atual += '\n' + linha
                else:
                    parte_atual = linha
        
        # Adicionar última parte
        if parte_atual:
            partes.append(parte_atual.strip())
        
        return partes

# ===============================================
# GERADOR DE KEYBOARDS
# ===============================================

class KeyboardBuilder:
    """Construtor de teclados inline para o Telegram"""
    
    @staticmethod
    def criar_keyboard_lista(
        items: List[Dict[str, Any]], 
        prefix: str, 
        key_field: str = 'id',
        label_field: str = 'nome',
        cols: int = 1
    ) -> List[List[Dict[str, str]]]:
        """Cria keyboard para lista de itens"""
        keyboard = []
        
        for i, item in enumerate(items):
            if i % cols == 0:
                keyboard.append([])
            
            callback_data = f"{prefix}_{item[key_field]}"
            text = item[label_field]
            
            keyboard[-1].append({
                'text': text,
                'callback_data': callback_data
            })
        
        return keyboard
    
    @staticmethod
    def criar_keyboard_confirmacao(prefix: str = "confirm") -> List[List[Dict[str, str]]]:
        """Cria keyboard de confirmação Sim/Não"""
        return [
            [
                {'text': '✅ Sim', 'callback_data': f'{prefix}_yes'},
                {'text': '❌ Não', 'callback_data': f'{prefix}_no'}
            ]
        ]
    
    @staticmethod
    def criar_keyboard_checklist() -> List[List[Dict[str, str]]]:
        """Cria keyboard para respostas de checklist"""
        return [
            [
                {'text': '✅ Aprovado', 'callback_data': 'checklist_approved'},
                {'text': '❌ Reprovado', 'callback_data': 'checklist_rejected'}
            ],
            [
                {'text': '📝 Observação', 'callback_data': 'checklist_observation'}
            ]
        ]
    
    @staticmethod
    def criar_keyboard_navegacao(
        has_prev: bool = False, 
        has_next: bool = False,
        show_menu: bool = True
    ) -> List[List[Dict[str, str]]]:
        """Cria keyboard de navegação"""
        keyboard = []
        
        # Linha de navegação anterior/próximo
        if has_prev or has_next:
            nav_row = []
            if has_prev:
                nav_row.append({'text': '◀️ Anterior', 'callback_data': 'nav_prev'})
            if has_next:
                nav_row.append({'text': '▶️ Próximo', 'callback_data': 'nav_next'})
            keyboard.append(nav_row)
        
        # Linha do menu
        if show_menu:
            keyboard.append([{'text': '🏠 Menu Principal', 'callback_data': 'main_menu'}])
        
        return keyboard

# ===============================================
# UTILITÁRIOS DE SISTEMA
# ===============================================

class SystemUtils:
    """Utilitários do sistema"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Obtém uso de memória do sistema"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            }
        except ImportError:
            return {'error': 'psutil não instalado'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Obtém informações do sistema"""
        try:
            import psutil
            import platform
            
            return {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if platform.system() != 'Windows' else 0
            }
        except ImportError:
            return {'error': 'psutil não disponível'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def log_user_action(user_id: int, action: str, details: str = None):
        """Registra ação do usuário nos logs"""
        log_msg = f"👤 User {user_id} - {action}"
        if details:
            log_msg += f" - {details}"
        
        logger.info(log_msg)

# ===============================================
# CACHE SIMPLES EM MEMÓRIA
# ===============================================

class SimpleCache:
    """Cache simples em memória para dados temporários"""
    
    _cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def set(cls, key: str, value: Any, ttl_minutes: int = 30):
        """Armazena valor no cache"""
        expiry = datetime.now().timestamp() + (ttl_minutes * 60)
        cls._cache[key] = {
            'value': value,
            'expiry': expiry
        }
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key not in cls._cache:
            return None
        
        cached = cls._cache[key]
        
        # Verificar se expirou
        if datetime.now().timestamp() > cached['expiry']:
            del cls._cache[key]
            return None
        
        return cached['value']
    
    @classmethod
    def delete(cls, key: str):
        """Remove item do cache"""
        if key in cls._cache:
            del cls._cache[key]
    
    @classmethod
    def clear(cls):
        """Limpa todo o cache"""
        cls._cache.clear()
    
    @classmethod
    def cleanup_expired(cls) -> int:
        """Remove itens expirados e retorna quantos foram removidos"""
        now = datetime.now().timestamp()
        expired_keys = [
            key for key, data in cls._cache.items() 
            if now > data['expiry']
        ]
        
        for key in expired_keys:
            del cls._cache[key]
        
        return len(expired_keys)