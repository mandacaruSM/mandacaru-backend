# =============================
# mandacaru_bot/core/db.py (VERSÃO CORRIGIDA)
# Adicione estas funções ao seu arquivo existente
# =============================

import httpx
import logging
from typing import List, Dict, Any, Optional
from .config import API_BASE_URL, API_TIMEOUT
from core.config import API_BASE_URL, API_TIMEOUT
from datetime import date

logger = logging.getLogger(__name__)

async def buscar_equipamento_por_chat_id(chat_id: str) -> dict:
    """Busca o equipamento vinculado a um chat_id"""
    try:
        url = f"{API_BASE_URL}/api/equipamentos/chat/{chat_id}/"
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"[ERRO] buscar_equipamento_por_chat_id: {e}")
    return None

async def get_checklist_do_dia(equipamento_id: int) -> dict:
    """Busca o checklist do dia para o equipamento"""
    try:
        url = f"{API_BASE_URL}/api/nr12/checklists/?equipamento_id={equipamento_id}&data_checklist={date.today()}"
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    return data[0]  # retorna o primeiro checklist do dia
    except Exception as e:
        print(f"[ERRO] get_checklist_do_dia: {e}")
    return None


async def buscar_operador_por_nome(nome: str) -> List[Dict[str, Any]]:
    """
    Busca operador por nome na API Django
    
    Args:
        nome: Nome do operador para buscar
        
    Returns:
        Lista de operadores encontrados
    """
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'search': nome}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Erro ao buscar operador: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar operador por nome: {e}")
        return []

async def validar_data_nascimento(operador_id: int, data_nascimento: str) -> bool:
    """
    Valida data de nascimento do operador
    
    Args:
        operador_id: ID do operador
        data_nascimento: Data no formato YYYY-MM-DD ou DD/MM/YYYY
        
    Returns:
        bool: True se data estiver correta
    """
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                operador = response.json()
                data_nascimento_db = operador.get('data_nascimento')
                
                if data_nascimento_db:
                    # Normalizar formatos de data
                    data_normalizada = normalizar_data(data_nascimento)
                    data_db_normalizada = normalizar_data(data_nascimento_db)
                    
                    return data_normalizada == data_db_normalizada
                    
        return False
        
    except Exception as e:
        logger.error(f"Erro ao validar data de nascimento: {e}")
        return False

async def registrar_chat_id(operador_id: int, chat_id: str) -> bool:
    """
    Registra/atualiza chat_id do Telegram para o operador
    
    Args:
        operador_id: ID do operador
        chat_id: ID do chat do Telegram
        
    Returns:
        bool: True se registrado com sucesso
    """
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/"
        data = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.patch(url, json=data)
            
            if response.status_code == 200:
                logger.info(f"Chat ID registrado para operador {operador_id}")
                return True
            else:
                logger.error(f"Erro ao registrar chat ID: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro ao registrar chat ID: {e}")
        return False

async def verificar_status_api() -> bool:
    """
    Verifica se a API Django está respondendo
    
    Returns:
        bool: True se API estiver funcionando
    """
    try:
        url = f"{API_BASE_URL}/operadores/"
        
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
            return response.status_code in [200, 401, 403]  # códigos aceitáveis
            
    except Exception as e:
        logger.error(f"API não está respondendo: {e}")
        return False

async def obter_operador_completo(operador_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtém dados completos do operador
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Dados completos do operador ou None
    """
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter operador: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao obter operador completo: {e}")
        return None

async def listar_checklists_pendentes(operador_id: int) -> List[Dict[str, Any]]:
    """
    Lista checklists pendentes para o operador
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Lista de checklists pendentes
    """
    try:
        url = f"{API_BASE_URL}/checklists/"
        params = {
            'responsavel_id': operador_id,
            'status': 'pendente'
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Erro ao listar checklists: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao listar checklists pendentes: {e}")
        return []

async def obter_checklists_operador(operador_id: int) -> List[Dict[str, Any]]:
    """
    Obtém checklists do operador
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Lista de checklists
    """
    try:
        url = f"{API_BASE_URL}/checklists/"
        params = {'operador_id': operador_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Erro ao obter checklists: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao obter checklists do operador: {e}")
        return []

async def iniciar_checklist(checklist_id: int, operador_id: int) -> Optional[Dict[str, Any]]:
    """
    Inicia um checklist
    
    Args:
        checklist_id: ID do checklist
        operador_id: ID do operador
        
    Returns:
        Dados do checklist iniciado ou None
    """
    try:
        url = f"{API_BASE_URL}/checklists/{checklist_id}/iniciar/"
        data = {'operador_id': operador_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao iniciar checklist: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao iniciar checklist: {e}")
        return None

async def salvar_resposta_checklist(checklist_id: int, item_id: int, resposta: Dict[str, Any]) -> bool:
    """
    Salva resposta de um item do checklist
    
    Args:
        checklist_id: ID do checklist
        item_id: ID do item
        resposta: Dados da resposta
        
    Returns:
        bool: True se salvo com sucesso
    """
    try:
        url = f"{API_BASE_URL}/checklists/{checklist_id}/itens/{item_id}/responder/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=resposta)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Erro ao salvar resposta: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro ao salvar resposta do checklist: {e}")
        return False

def normalizar_data(data_str: str) -> str:
    """
    Normaliza formato de data para YYYY-MM-DD
    
    Args:
        data_str: Data em formato string
        
    Returns:
        Data normalizada no formato YYYY-MM-DD
    """
    if not data_str:
        return ""
    
    data_str = data_str.strip()
    
    # Se já está no formato YYYY-MM-DD
    if len(data_str) == 10 and data_str[4] == '-' and data_str[7] == '-':
        return data_str
    
    # Se está no formato DD/MM/YYYY
    if len(data_str) == 10 and '/' in data_str:
        partes = data_str.split('/')
        if len(partes) == 3:
            dia, mes, ano = partes
            return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
    
    # Se está no formato DD-MM-YYYY
    if len(data_str) == 10 and data_str[2] == '-' and data_str[5] == '-':
        partes = data_str.split('-')
        if len(partes) == 3:
            dia, mes, ano = partes
            return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
    
    return data_str

# =============================
# FUNÇÕES ESPECÍFICAS PARA CADA MÓDULO
# =============================

async def obter_equipamentos_operador(operador_id: int) -> List[Dict[str, Any]]:
    """
    Obtém equipamentos associados ao operador
    """
    try:
        url = f"{API_BASE_URL}/equipamentos/"
        params = {'operador_id': operador_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                return []
                
    except Exception as e:
        logger.error(f"Erro ao obter equipamentos do operador: {e}")
        return []

async def listar_ordens_servico(operador_id: int, status: str = None) -> List[Dict[str, Any]]:
    """
    Lista ordens de serviço do operador
    """
    try:
        url = f"{API_BASE_URL}/ordens-servico/"
        params = {'solicitante_id': operador_id}
        
        if status:
            params['status'] = status
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                return []
                
    except Exception as e:
        logger.error(f"Erro ao listar ordens de serviço: {e}")
        return []

async def criar_ordem_servico(dados_os: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cria nova ordem de serviço
    """
    try:
        url = f"{API_BASE_URL}/ordens-servico/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=dados_os)
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Erro ao criar OS: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao criar ordem de serviço: {e}")
        return None

async def listar_abastecimentos(operador_id: int) -> List[Dict[str, Any]]:
    """
    Lista abastecimentos do operador
    """
    try:
        url = f"{API_BASE_URL}/abastecimentos/"
        params = {'operador_id': operador_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                return []
                
    except Exception as e:
        logger.error(f"Erro ao listar abastecimentos: {e}")
        return []

async def registrar_abastecimento(dados_abastecimento: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Registra novo abastecimento
    """
    try:
        url = f"{API_BASE_URL}/abastecimentos/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=dados_abastecimento)
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Erro ao registrar abastecimento: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao registrar abastecimento: {e}")
        return None
    
async def obter_checklists_operador(operador_id: int) -> List[Dict[str, Any]]:
    """
    Obtém checklists do operador
    """
    try:
        url = f"{API_BASE_URL}/checklists/"
        params = {'operador_id': operador_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Erro ao obter checklists: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao obter checklists do operador: {e}")
        return []
    
async def criar_checklist(dados_checklist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cria novo checklist
    
    Args:
        dados_checklist: Dados para criação do checklist
        
    Returns:
        Dados do checklist criado ou None
    """
    try:
        url = f"{API_BASE_URL}/checklists/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=dados_checklist)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Erro ao criar checklist: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao criar checklist: {e}")
        return None

async def obter_checklists_operador(operador_id: int) -> List[Dict[str, Any]]:
    """
    Obtém checklists do operador
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Lista de checklists
    """
    try:
        url = f"{API_BASE_URL}/checklists/"
        params = {'operador_id': operador_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Erro ao obter checklists: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao obter checklists do operador: {e}")
        return []

async def finalizar_checklist(checklist_id: int, dados_finalizacao: Dict[str, Any]) -> bool:
    """
    Finaliza um checklist
    
    Args:
        checklist_id: ID do checklist
        dados_finalizacao: Dados para finalização
        
    Returns:
        bool: True se finalizado com sucesso
    """
    try:
        url = f"{API_BASE_URL}/checklists/{checklist_id}/finalizar/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=dados_finalizacao)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Erro ao finalizar checklist: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro ao finalizar checklist: {e}")
        return False

async def atualizar_item_checklist(item_id: int, dados_item: Dict[str, Any]) -> bool:
    """
    Atualiza item do checklist
    
    Args:
        item_id: ID do item
        dados_item: Dados do item
        
    Returns:
        bool: True se atualizado com sucesso
    """
    try:
        url = f"{API_BASE_URL}/checklist-items/{item_id}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.patch(url, json=dados_item)
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Erro ao atualizar item: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro ao atualizar item do checklist: {e}")
        return False

# =============================================================
# Novas funções para suporte ao módulo de equipamentos
# =============================================================

async def buscar_equipamentos(
    nome: Optional[str] = None,
    status_operacional: Optional[str] = None,
    categoria_id: Optional[int] = None,
    operador_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Busca equipamentos na API aplicando filtros opcionais.

    Args:
        nome: texto para busca (mapeado para o parâmetro ``search`` da API)
        status_operacional: filtra pelo status operacional (ex. 'DISPONIVEL')
        categoria_id: ID da categoria do equipamento
        operador_id: ID do operador associado

    Returns:
        Lista de equipamentos ou lista vazia em caso de erro
    """
    try:
        url = f"{API_BASE_URL}/equipamentos/"
        params: Dict[str, Any] = {}
        if nome:
            params["search"] = nome
        if status_operacional:
            params["status_operacional"] = status_operacional
        if categoria_id is not None:
            params["categoria"] = categoria_id
        if operador_id is not None:
            params["operador_id"] = operador_id

        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", []) if isinstance(data, dict) else data
            logger.error(f"Erro ao buscar equipamentos (status {response.status_code}): {response.text}")
        return []
    except Exception as e:
        logger.error(f"Erro ao buscar equipamentos: {e}")
        return []

async def obter_equipamento_por_id(equipamento_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtém detalhes de um equipamento pelo ID.

    Args:
        equipamento_id: identificador do equipamento

    Returns:
        Dicionário com os dados do equipamento ou None se não encontrado/erro
    """
    try:
        url = f"{API_BASE_URL}/equipamentos/{equipamento_id}/"
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Equipamento {equipamento_id} não encontrado (status {response.status_code})")
        return None
    except Exception as e:
        logger.error(f"Erro ao obter equipamento por ID: {e}")
        return None
    
async def buscar_equipamento_por_uuid(uuid_equipamento: str) -> dict:
    """Busca equipamento pelo UUID"""
    try:
        url = f"{API_BASE_URL}/equipamentos/por-uuid/{uuid_equipamento}/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Erro ao buscar equipamento UUID {uuid_equipamento}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro na requisição de equipamento UUID {uuid_equipamento}: {e}")
        return None

async def buscar_acoes_equipamento(equipamento_id: int, operador_id: int) -> dict:
    """Busca ações disponíveis para equipamento e operador"""
    try:
        url = f"{API_BASE_URL}/bot/equipamento/{equipamento_id}/"
        dados = {'operador_id': operador_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=dados, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('acoes_disponiveis', {})
            else:
                logger.error(f"Erro ao buscar ações do equipamento {equipamento_id}: {response.status_code}")
                return {}
                
    except Exception as e:
        logger.error(f"Erro na requisição de ações do equipamento {equipamento_id}: {e}")
        return {}

async def buscar_equipamento_por_uuid(uuid_equipamento: str) -> dict:
    """Busca equipamento pelo UUID"""
    try:
        url = f"{API_BASE_URL}/equipamentos/por-uuid/{uuid_equipamento}/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Erro ao buscar equipamento UUID {uuid_equipamento}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro na requisição de equipamento UUID {uuid_equipamento}: {e}")
        return None

# ===============================================
# ADICIONAR NO FINAL DO ARQUIVO: mandacaru_bot/core/db.py
# ===============================================

async def buscar_equipamento_por_uuid(uuid_equipamento: str) -> dict:
    """Busca equipamento pelo UUID"""
    try:
        url = f"{API_BASE_URL}/equipamentos/por-uuid/{uuid_equipamento}/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Erro ao buscar equipamento UUID {uuid_equipamento}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro na requisição de equipamento UUID {uuid_equipamento}: {e}")
        return None

async def buscar_operador_por_chat_id(chat_id: str) -> dict:
    """Busca operador pelo chat_id do Telegram"""
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    operador = data['results'][0]
                    logger.info(f"Operador encontrado por chat_id: {operador.get('nome')}")
                    return operador
                else:
                    logger.info(f"Nenhum operador encontrado com chat_id: {chat_id}")
                    return None
            else:
                logger.error(f"Erro ao buscar operador por chat_id {chat_id}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro na requisição de operador por chat_id {chat_id}: {e}")
        return None
    
# ===============================================
# ADICIONAR NO FINAL DE: mandacaru_bot/core/db.py
# ===============================================

async def atualizar_chat_id_operador(operador_id: int, chat_id: str) -> bool:
    """Atualiza chat_id do operador no banco"""
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/"
        data = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=data, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                logger.info(f"Chat ID atualizado para operador {operador_id}: {chat_id}")
                return True
            else:
                logger.error(f"Erro ao atualizar chat ID operador {operador_id}: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro na requisição de atualização chat ID: {e}")
        return False

async def buscar_operador_por_chat_id(chat_id: str) -> dict:
    """Busca operador pelo chat_id do Telegram"""
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    operador = data['results'][0]
                    logger.info(f"Operador encontrado por chat_id: {operador.get('nome')}")
                    return operador
                else:
                    logger.info(f"Nenhum operador encontrado com chat_id: {chat_id}")
                    return None
            else:
                logger.error(f"Erro ao buscar operador por chat_id {chat_id}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro na requisição de operador por chat_id {chat_id}: {e}")
        return None
    
async def buscar_operador_por_chat_id(chat_id: str) -> dict:
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    return data['results'][0]
            return None
    except Exception as e:
        logger.error(f"Erro buscar operador por chat_id: {e}")
        return None

async def buscar_equipamento_por_uuid(uuid_equipamento: str) -> dict:
    try:
        url = f"{API_BASE_URL}/equipamentos/por-uuid/{uuid_equipamento}/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        logger.error(f"Erro buscar equipamento UUID: {e}")
        return None

async def atualizar_chat_id_operador(operador_id: int, chat_id: str) -> bool:
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/"
        data = {'chat_id_telegram': chat_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=data, timeout=API_TIMEOUT)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro atualizar chat_id: {e}")
        return False
    
# ===============================================
# ADICIONAR NO FINAL DO ARQUIVO: core/db.py
# Novas funções para integração NR12
# ===============================================

async def buscar_equipamento_por_uuid(uuid_equipamento: str) -> dict:
    """
    ✨ NOVA: Busca equipamento pelo UUID
    Integra com a API do sistema
    """
    try:
        url = f"{API_BASE_URL}/equipamentos/por-uuid/{uuid_equipamento}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                equipamento = response.json()
                logger.info(f"Equipamento encontrado: {equipamento.get('nome')}")
                return equipamento
            else:
                logger.warning(f"Equipamento UUID {uuid_equipamento} não encontrado: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao buscar equipamento por UUID {uuid_equipamento}: {e}")
        return None

async def buscar_equipamento_por_id(equipamento_id: int) -> dict:
    """
    ✨ NOVA: Busca equipamento pelo ID
    """
    try:
        url = f"{API_BASE_URL}/equipamentos/{equipamento_id}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                equipamento = response.json()
                logger.info(f"Equipamento encontrado: {equipamento.get('nome')}")
                return equipamento
            else:
                logger.warning(f"Equipamento ID {equipamento_id} não encontrado: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao buscar equipamento por ID {equipamento_id}: {e}")
        return None

async def listar_equipamentos_operador(operador_id: int) -> list:
    """
    📋 NOVA: Lista equipamentos autorizados para o operador
    """
    try:
        url = f"{API_BASE_URL}/operadores/{operador_id}/equipamentos/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                equipamentos = data.get('results', data) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(equipamentos)} equipamentos para operador {operador_id}")
                return equipamentos
            else:
                logger.warning(f"Erro ao buscar equipamentos do operador {operador_id}: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao listar equipamentos do operador {operador_id}: {e}")
        return []

async def buscar_checklists_operador(operador_id: int, limite: int = 10) -> list:
    """
    📋 NOVA: Busca checklists do operador
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/"
        params = {
            'operador_id': operador_id,
            'ordering': '-data_checklist',
            'limit': limite
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', data) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(checklists)} checklists para operador {operador_id}")
                return checklists
            else:
                logger.warning(f"Erro ao buscar checklists do operador {operador_id}: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar checklists do operador {operador_id}: {e}")
        return []

async def buscar_checklist_por_id(checklist_id: int) -> dict:
    """
    📋 NOVA: Busca detalhes completos de um checklist
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklist-detalhes/{checklist_id}/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    checklist = data.get('checklist')
                    logger.info(f"Checklist {checklist_id} encontrado")
                    return checklist
                else:
                    logger.warning(f"Checklist {checklist_id} não encontrado na API")
                    return None
            else:
                logger.warning(f"Erro ao buscar checklist {checklist_id}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao buscar checklist {checklist_id}: {e}")
        return None

async def verificar_checklist_em_andamento(operador_id: int) -> dict:
    """
    🔍 NOVA: Verifica se operador tem checklist em andamento
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/"
        params = {
            'operador_id': operador_id,
            'status': 'EM_ANDAMENTO,INICIADO',
            'data_checklist': datetime.now().date().isoformat()
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', data) if isinstance(data, dict) else data
                
                if checklists:
                    checklist_em_andamento = checklists[0]
                    logger.info(f"Checklist em andamento encontrado: {checklist_em_andamento.get('id')}")
                    return checklist_em_andamento
                else:
                    logger.info(f"Nenhum checklist em andamento para operador {operador_id}")
                    return None
            else:
                logger.warning(f"Erro ao verificar checklist em andamento: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao verificar checklist em andamento: {e}")
        return None

async def buscar_todos_checklists(limite: int = 50) -> list:
    """
    🐛 NOVA: Função debug para buscar todos os checklists
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/"
        params = {
            'ordering': '-data_checklist',
            'limit': limite
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', data) if isinstance(data, dict) else data
                logger.info(f"Debug: Encontrados {len(checklists)} checklists total")
                return checklists
            else:
                logger.warning(f"Erro ao buscar todos os checklists: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar todos os checklists: {e}")
        return []

# ===============================================
# FUNÇÃO AUXILIAR PARA FORMATAR DADOS
# ===============================================

def formatar_checklist_para_bot(checklist: dict) -> str:
    """
    📝 NOVA: Formata dados do checklist para exibição no bot
    """
    try:
        # Extrair dados essenciais
        checklist_id = checklist.get('id', 'N/A')
        turno = checklist.get('turno', 'N/A')
        status = checklist.get('status', 'N/A')
        data_checklist = checklist.get('data_checklist', 'N/A')
        
        # Dados do equipamento
        equipamento = checklist.get('equipamento', {})
        if isinstance(equipamento, dict):
            nome_equipamento = equipamento.get('nome', 'N/A')
        else:
            nome_equipamento = str(equipamento)
        
        # Traduzir status
        status_texto = {
            'INICIADO': '🟡 Iniciado',
            'EM_ANDAMENTO': '🔄 Em Andamento', 
            'CONCLUIDO': '✅ Concluído',
            'PENDENTE': '⏳ Pendente',
            'CANCELADO': '❌ Cancelado'
        }.get(status, f'❓ {status}')
        
        # Montar texto formatado
        texto = f"📋 **Checklist #{checklist_id}**\n"
        texto += f"🚜 {nome_equipamento}\n"
        texto += f"🕐 {turno} - {data_checklist}\n"
        texto += f"📊 {status_texto}"
        
        return texto
        
    except Exception as e:
        logger.error(f"Erro ao formatar checklist: {e}")
        return f"📋 Checklist #{checklist.get('id', 'N/A')} - Erro na formatação"