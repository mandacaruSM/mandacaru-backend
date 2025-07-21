# =====================
# core/db.py (melhorado)
# =====================

import httpx
import logging
from typing import List, Dict, Any, Optional
from core.config import API_BASE_URL

# Configurar logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Exceção personalizada para erros da API"""
    pass

async def fazer_requisicao_api(method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Função genérica para fazer requisições à API
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=json_data)
            elif method.upper() == "PATCH":
                response = await client.patch(url, json=json_data)
            elif method.upper() == "PUT":
                response = await client.put(url, json=json_data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Timeout na requisição para {url}")
        raise APIError("Timeout na comunicação com o servidor")
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP {e.response.status_code} na requisição para {url}")
        raise APIError(f"Erro do servidor: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão na requisição para {url}: {e}")
        raise APIError("Erro de conexão com o servidor")
    except Exception as e:
        logger.error(f"Erro inesperado na requisição para {url}: {e}")
        raise APIError("Erro interno do sistema")

async def buscar_operador_por_nome(nome: str) -> List[Dict[str, Any]]:
    """
    Busca operadores pelo nome na API
    """
    try:
        params = {"search": nome}
        data = await fazer_requisicao_api("GET", "/operadores/", params=params)
        return data.get('results', []) if data else []
    except APIError:
        logger.error(f"Erro ao buscar operador por nome: {nome}")
        return []

async def obter_operador_por_id(id_operador: int) -> Optional[Dict[str, Any]]:
    """
    Obtém dados completos de um operador pelo ID
    """
    try:
        data = await fazer_requisicao_api("GET", f"/operadores/{id_operador}/")
        return data
    except APIError:
        logger.error(f"Erro ao obter operador por ID: {id_operador}")
        return None

async def validar_data_nascimento(id_operador: int, data_digitada: str) -> bool:
    """
    Valida a data de nascimento do operador
    data_digitada deve estar no formato DD/MM/AAAA
    """
    try:
        # Converte entrada do usuário para formato da API
        if "/" in data_digitada:
            dia, mes, ano = map(int, data_digitada.split("/"))
            data_usuario = f"{ano:04d}-{mes:02d}-{dia:02d}"
        else:
            # Se já estiver no formato correto
            data_usuario = data_digitada
        
        # Busca dados do operador
        operador = await obter_operador_por_id(id_operador)
        if not operador:
            return False
        
        data_api = operador.get("data_nascimento")
        return data_usuario == data_api
        
    except (ValueError, TypeError):
        logger.error(f"Formato de data inválido: {data_digitada}")
        return False
    except APIError:
        logger.error(f"Erro ao validar data de nascimento para operador {id_operador}")
        return False

async def registrar_chat_id(id_operador: int, chat_id: str) -> bool:
    """
    Registra o chat_id do Telegram no perfil do operador
    """
    try:
        json_data = {"chat_id_telegram": chat_id}
        data = await fazer_requisicao_api("PATCH", f"/operadores/{id_operador}/", json_data=json_data)
        return data is not None
    except APIError:
        logger.error(f"Erro ao registrar chat_id {chat_id} para operador {id_operador}")
        return False

async def buscar_operador_por_chat_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca operador pelo chat_id do Telegram
    """
    try:
        params = {"chat_id_telegram": chat_id}
        data = await fazer_requisicao_api("GET", "/operadores/", params=params)
        results = data.get('results', []) if data else []
        return results[0] if results else None
    except APIError:
        logger.error(f"Erro ao buscar operador por chat_id: {chat_id}")
        return None

async def verificar_status_api() -> bool:
    """
    Verifica se a API está funcionando
    """
    try:
        # Primeiro tenta um endpoint básico como /operadores/
        await fazer_requisicao_api("GET", "/operadores/", params={"limit": 1})
        return True
    except APIError:
        try:
            # Se falhar, tenta a raiz da API
            await fazer_requisicao_api("GET", "/")
            return True
        except APIError:
            return False

# Funções específicas para cada módulo (exemplos)

async def obter_checklists_operador(id_operador: int) -> List[Dict[str, Any]]:
    """
    Obtém checklists do operador
    """
    try:
        params = {"operador": id_operador}
        data = await fazer_requisicao_api("GET", "/checklists/", params=params)
        return data.get('results', []) if data else []
    except APIError:
        logger.error(f"Erro ao obter checklists do operador {id_operador}")
        return []

async def criar_checklist(dados_checklist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cria um novo checklist
    """
    try:
        return await fazer_requisicao_api("POST", "/checklists/", json_data=dados_checklist)
    except APIError:
        logger.error("Erro ao criar checklist")
        return None

async def obter_abastecimentos_operador(id_operador: int) -> List[Dict[str, Any]]:
    """
    Obtém registros de abastecimento do operador
    """
    try:
        params = {"operador": id_operador}
        data = await fazer_requisicao_api("GET", "/abastecimentos/", params=params)
        return data.get('results', []) if data else []
    except APIError:
        logger.error(f"Erro ao obter abastecimentos do operador {id_operador}")
        return []