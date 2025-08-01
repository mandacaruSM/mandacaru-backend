# ===============================================
# ARQUIVO CORRIGIDO: mandacaru_bot/core/db.py
# Funções de integração com API do backend Django
# ===============================================

import httpx
import logging
from typing import Dict, Any, List, Optional  # CORREÇÃO: Adicionar importação do typing
from datetime import datetime, date
from .config import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

# ===============================================
# CLASSE DE EXCEÇÃO PERSONALIZADA
# ===============================================

class APIError(Exception):
    """Exceção personalizada para erros de API"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# ===============================================
# FUNÇÕES DE BASE
# ===============================================

async def fazer_requisicao_api(
    method: str, 
    endpoint: str, 
    data: Dict[str, Any] = None, 
    params: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Faz requisição para a API do backend Django
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE)
        endpoint: Endpoint da API (ex: /operadores/)
        data: Dados para envio (POST/PUT)
        params: Parâmetros de query string
        
    Returns:
        Resposta da API ou None se erro
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = await client.delete(url, params=params)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Recurso não encontrado: {url}")
                return None
            else:
                logger.error(f"Erro na API: {response.status_code} - {response.text}")
                raise APIError(f"Erro na API: {response.status_code}", response.status_code)
                
    except httpx.TimeoutException:
        logger.error(f"Timeout na requisição para {url}")
        raise APIError("Timeout na conexão com a API")
    except Exception as e:
        logger.error(f"Erro na requisição API: {e}")
        raise APIError(f"Erro de conexão: {str(e)}")

async def verificar_status_api() -> bool:
    """
    Verifica se a API está respondendo
    
    Returns:
        True se API está online, False caso contrário
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE_URL}/health/")
            return response.status_code == 200
    except:
        return False

# ===============================================
# FUNÇÕES DE OPERADORES
# ===============================================

async def buscar_operador_por_nome(nome: str) -> List[Dict[str, Any]]:
    """
    Busca operador por nome na API
    
    Args:
        nome: Nome do operador para busca
        
    Returns:
        Lista de operadores encontrados
    """
    try:
        params = {"search": nome.strip()}
        data = await fazer_requisicao_api("GET", "/operadores/", params=params)
        
        if data and 'results' in data:
            resultados = data['results']
            logger.info(f"Encontrados {len(resultados)} operadores para '{nome}'")
            return resultados
        
        return []
        
    except APIError as e:
        logger.error(f"Erro ao buscar operador por nome: {e}")
        return []

async def buscar_operador_por_chat_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca operador pelo chat_id do Telegram
    
    Args:
        chat_id: ID do chat do Telegram
        
    Returns:
        Dados do operador ou None se não encontrado
    """
    try:
        params = {"chat_id_telegram": chat_id}
        data = await fazer_requisicao_api("GET", "/operadores/", params=params)
        
        if data and 'results' in data and data['results']:
            operador = data['results'][0]
            logger.info(f"Operador encontrado pelo chat_id: {operador.get('nome')}")
            return operador
        
        return None
        
    except APIError as e:
        logger.error(f"Erro ao buscar operador por chat_id: {e}")
        return None

async def atualizar_chat_id_operador(operador_id: int, chat_id: str) -> bool:
    """
    Atualiza o chat_id do operador
    
    Args:
        operador_id: ID do operador
        chat_id: Chat ID do Telegram
        
    Returns:
        True se atualizado com sucesso
    """
    try:
        data = {"chat_id_telegram": chat_id}
        response = await fazer_requisicao_api("PUT", f"/operadores/{operador_id}/", data=data)
        
        if response:
            logger.info(f"Chat ID atualizado para operador {operador_id}")
            return True
        
        return False
        
    except APIError as e:
        logger.error(f"Erro ao atualizar chat_id: {e}")
        return False

# ===============================================
# FUNÇÕES DE EQUIPAMENTOS
# ===============================================

async def listar_equipamentos() -> List[Dict[str, Any]]:
    """
    Lista todos os equipamentos
    
    Returns:
        Lista de equipamentos
    """
    try:
        data = await fazer_requisicao_api("GET", "/equipamentos/")
        
        if data and 'results' in data:
            equipamentos = data['results']
            logger.info(f"Encontrados {len(equipamentos)} equipamentos")
            return equipamentos
        
        return []
        
    except APIError as e:
        logger.error(f"Erro ao listar equipamentos: {e}")
        return []

async def buscar_equipamento_por_uuid(uuid: str) -> Optional[Dict[str, Any]]:
    """
    Busca equipamento por UUID
    
    Args:
        uuid: UUID do equipamento
        
    Returns:
        Dados do equipamento ou None se não encontrado
    """
    try:
        params = {"uuid": uuid}
        data = await fazer_requisicao_api("GET", "/equipamentos/", params=params)
        
        if data and 'results' in data and data['results']:
            equipamento = data['results'][0]
            logger.info(f"Equipamento encontrado: {equipamento.get('nome')}")
            return equipamento
        
        return None
        
    except APIError as e:
        logger.error(f"Erro ao buscar equipamento por UUID: {e}")
        return None

# ===============================================
# FUNÇÕES DE ABASTECIMENTO
# ===============================================

async def registrar_abastecimento(dados_abastecimento: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Registra um novo abastecimento
    
    Args:
        dados_abastecimento: Dados do abastecimento
        
    Returns:
        Dados do abastecimento criado ou None se erro
    """
    try:
        response = await fazer_requisicao_api("POST", "/abastecimentos/", data=dados_abastecimento)
        
        if response:
            logger.info(f"Abastecimento registrado: ID {response.get('id')}")
            return response
        
        return None
        
    except APIError as e:
        logger.error(f"Erro ao registrar abastecimento: {e}")
        return None

async def obter_abastecimentos_operador(operador_id: int) -> List[Dict[str, Any]]:
    """
    Obtém abastecimentos de um operador
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Lista de abastecimentos
    """
    try:
        params = {"operador": operador_id}
        data = await fazer_requisicao_api("GET", "/abastecimentos/", params=params)
        
        if data and 'results' in data:
            abastecimentos = data['results']
            logger.info(f"Encontrados {len(abastecimentos)} abastecimentos do operador {operador_id}")
            return abastecimentos
        
        return []
        
    except APIError as e:
        logger.error(f"Erro ao obter abastecimentos do operador: {e}")
        return []

# ===============================================
# FUNÇÕES DE ORDEM DE SERVIÇO
# ===============================================

async def criar_ordem_servico(dados_os: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cria uma nova ordem de serviço
    
    Args:
        dados_os: Dados da ordem de serviço
        
    Returns:
        Dados da OS criada ou None se erro
    """
    try:
        response = await fazer_requisicao_api("POST", "/ordens-servico/", data=dados_os)
        
        if response:
            logger.info(f"Ordem de serviço criada: ID {response.get('id')}")
            return response
        
        return None
        
    except APIError as e:
        logger.error(f"Erro ao criar ordem de serviço: {e}")
        return None

# ===============================================
# FUNÇÕES NR12 - INTEGRAÇÃO COM API REAL
# ===============================================

async def buscar_tipos_equipamento_nr12() -> List[Dict[str, Any]]:
    """
    Busca tipos de equipamento NR12 da API real
    
    Returns:
        Lista de tipos de equipamento
    """
    try:
        url = f"{API_BASE_URL}/nr12/tipos-equipamento/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                tipos = data.get('results', []) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(tipos)} tipos de equipamento NR12")
                return tipos
            else:
                logger.error(f"Erro ao buscar tipos de equipamento NR12: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar tipos de equipamento NR12: {e}")
        return []

async def buscar_itens_padrao_nr12(tipo_equipamento_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Busca itens padrão de checklist NR12
    
    Args:
        tipo_equipamento_id: ID do tipo de equipamento (opcional)
        
    Returns:
        Lista de itens padrão
    """
    try:
        url = f"{API_BASE_URL}/nr12/itens-padrao/"
        params = {}
        
        if tipo_equipamento_id:
            params['tipo_equipamento'] = tipo_equipamento_id
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                itens = data.get('results', []) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(itens)} itens padrão NR12")
                return itens
            else:
                logger.error(f"Erro ao buscar itens padrão NR12: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar itens padrão NR12: {e}")
        return []

async def buscar_checklists_nr12(
    equipamento_id: Optional[int] = None,
    status: Optional[str] = None,
    data_checklist: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Busca checklists NR12
    
    Args:
        equipamento_id: ID do equipamento (opcional)
        status: Status do checklist (opcional)
        data_checklist: Data do checklist (YYYY-MM-DD) (opcional)
        
    Returns:
        Lista de checklists
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/"
        params = {}
        
        if equipamento_id:
            params['equipamento'] = equipamento_id
        if status:
            params['status'] = status
        if data_checklist:
            params['data_checklist'] = data_checklist
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                checklists = data.get('results', []) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(checklists)} checklists NR12")
                return checklists
            else:
                logger.error(f"Erro ao buscar checklists NR12: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar checklists NR12: {e}")
        return []

async def criar_checklist_nr12(
    equipamento_id: int,
    responsavel_id: Optional[int] = None,
    turno: str = "MANHA"
) -> Optional[Dict[str, Any]]:
    """
    Cria um novo checklist NR12
    
    Args:
        equipamento_id: ID do equipamento
        responsavel_id: ID do responsável (opcional)
        turno: Turno do checklist
        
    Returns:
        Dados do checklist criado ou None se erro
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/"
        data = {
            'equipamento': equipamento_id,
            'turno': turno,
            'status': 'PENDENTE',
            'data_checklist': date.today().isoformat()
        }
        
        if responsavel_id:
            data['responsavel'] = responsavel_id
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 201:
                checklist = response.json()
                logger.info(f"Checklist NR12 criado: ID {checklist.get('id')}")
                return checklist
            else:
                logger.error(f"Erro ao criar checklist NR12: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao criar checklist NR12: {e}")
        return None

async def buscar_itens_checklist_nr12(checklist_id: int) -> List[Dict[str, Any]]:
    """
    Busca itens de um checklist NR12 específico
    
    Args:
        checklist_id: ID do checklist
        
    Returns:
        Lista de itens do checklist
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/{checklist_id}/itens/"
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                itens = data.get('results', []) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(itens)} itens do checklist {checklist_id}")
                return itens
            else:
                logger.error(f"Erro ao buscar itens do checklist: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar itens do checklist: {e}")
        return []

async def atualizar_item_checklist_nr12(
    item_id: int,
    status: str,
    observacao: str = "",
    responsavel_id: Optional[int] = None
) -> bool:
    """
    Atualiza um item do checklist NR12
    
    Args:
        item_id: ID do item
        status: Status do item (OK, NOK, PENDENTE)
        observacao: Observação opcional
        responsavel_id: ID do responsável (opcional)
        
    Returns:
        True se atualizado com sucesso
    """
    try:
        # Endpoint correto baseado na API vista
        url = f"{API_BASE_URL}/nr12/itens-checklist/{item_id}/"
        
        # Mapear status do bot para o formato da API
        status_map = {
            'OK': 'OK',
            'NOK': 'NOK',  # ou pode ser 'NAO_CONFORME'
            'PENDENTE': 'PENDENTE'
        }
        
        data = {
            'status': status_map.get(status, status),
            'observacao': observacao
        }
        
        if responsavel_id:
            data['verificado_por'] = responsavel_id
        
        logger.info(f"Atualizando item {item_id}: {data}")
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            # Tentar PUT primeiro
            response = await client.put(url, json=data)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Item {item_id} atualizado com sucesso via PUT")
                return True
            
            # Se PUT não funcionar, tentar PATCH
            response = await client.patch(url, json=data)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Item {item_id} atualizado com sucesso via PATCH")
                return True
            
            # Log da resposta de erro
            logger.error(f"Erro ao atualizar item {item_id}: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
                
    except Exception as e:
        logger.error(f"Erro ao atualizar item: {e}")
        return False

async def finalizar_checklist_nr12(
    checklist_id: int,
    responsavel_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Finaliza um checklist NR12
    
    Args:
        checklist_id: ID do checklist
        responsavel_id: ID do responsável (opcional)
        
    Returns:
        Dados do checklist finalizado ou None se erro
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/{checklist_id}/finalizar/"
        data = {}
        
        if responsavel_id:
            data['responsavel'] = responsavel_id
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                checklist = response.json()
                logger.info(f"Checklist {checklist_id} finalizado")
                return checklist
            else:
                logger.error(f"Erro ao finalizar checklist: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao finalizar checklist: {e}")
        return None

async def buscar_checklists_operador_hoje(operador_id: int) -> List[Dict[str, Any]]:
    """
    Busca checklists do operador para o dia atual
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Lista de checklists do dia
    """
    try:
        hoje = date.today().isoformat()
        return await buscar_checklists_nr12(
            data_checklist=hoje
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar checklists do operador: {e}")
        return []

async def buscar_equipamentos_com_nr12() -> List[Dict[str, Any]]:
    """
    Busca equipamentos que têm NR12 configurado
    
    Returns:
        Lista de equipamentos com NR12
    """
    try:
        # Buscar equipamentos normais e filtrar os que têm NR12
        equipamentos = await listar_equipamentos()
        
        # Filtrar apenas equipamentos que podem ter NR12
        equipamentos_nr12 = []
        for equipamento in equipamentos:
            # Você pode adicionar lógica específica para identificar equipamentos NR12
            # Por exemplo, verificar se tem campo 'ativo_nr12' ou 'tipo_nr12'
            if equipamento.get('status_operacional') in ['DISPONIVEL', 'EM_USO']:
                equipamentos_nr12.append(equipamento)
        
        return equipamentos_nr12
        
    except Exception as e:
        logger.error(f"Erro ao buscar equipamentos com NR12: {e}")
        return []

async def verificar_checklist_equipamento_hoje(equipamento_id: int) -> Optional[Dict[str, Any]]:
    """
    Verifica se já existe checklist para o equipamento hoje
    
    Args:
        equipamento_id: ID do equipamento
        
    Returns:
        Dados do checklist se existe, None caso contrário
    """
    try:
        hoje = date.today().isoformat()
        checklists = await buscar_checklists_nr12(
            equipamento_id=equipamento_id,
            data_checklist=hoje
        )
        
        if checklists:
            return checklists[0]  # Retornar o primeiro checklist do dia
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao verificar checklist do equipamento: {e}")
        return None

# ===============================================
# FUNÇÕES DE COMPATIBILIDADE
# ===============================================

# Manter compatibilidade com código existente
async def get_checklist_do_dia(equipamento_id: int) -> Optional[Dict[str, Any]]:
    """Alias para verificar_checklist_equipamento_hoje"""
    return await verificar_checklist_equipamento_hoje(equipamento_id)

async def criar_checklist(equipamento_id: int, operador_id: int) -> Optional[Dict[str, Any]]:
    """Alias para criar_checklist_nr12"""
    return await criar_checklist_nr12(equipamento_id, operador_id)