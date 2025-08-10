# ===============================================
# ARQUIVO: mandacaru_bot/core/db.py
# Interface com a API do Django
# ===============================================

import httpx
import logging
from typing import List, Dict, Any, Optional
from .config import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

# ===============================================
# FUNÇÕES DE API GENÉRICAS
# ===============================================

async def fazer_requisicao_api(
    method: str,
    endpoint: str,
    data: Dict[str, Any] = None,
    params: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """Função genérica para fazer requisições à API"""
    
    url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            
            if method.upper() == 'GET':
                response = await client.get(url, params=params)
            elif method.upper() == 'POST':
                response = await client.post(url, json=data, params=params)
            elif method.upper() == 'PATCH':
                response = await client.patch(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = await client.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = await client.delete(url, params=params)
            else:
                logger.error(f"❌ Método HTTP inválido: {method}")
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"❌ Erro na API: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Erro na requisição: {e}")
        return None

async def verificar_status_api() -> bool:
    """Verifica se a API está respondendo"""
    try:
        result = await fazer_requisicao_api('GET', '/')
        return result is not None
    except Exception:
        return False

# ===============================================
# FUNÇÕES DE OPERADORES
# ===============================================

async def buscar_operador_por_nome(nome: str) -> Optional[Dict[str, Any]]:
    """Busca operador pelo nome usando endpoint correto"""
    logger.info(f"🔍 Buscando operador: {nome}")

    # Usar endpoint /api/operadores/busca/ com parâmetro nome
    result = await fazer_requisicao_api('GET', 'operadores/busca/', params={'nome': nome})

    if result and result.get('success') and result.get('results'):
        operadores = result['results']
        if operadores:
            # Retornar o primeiro resultado
            operador = operadores[0]
            logger.info(f"✅ Operador encontrado: {operador.get('nome')}")
            return operador

    logger.warning(f"⚠️ Operador não encontrado: {nome}")
    return None

async def buscar_operador_por_chat_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """Busca operador pelo chat_id do Telegram usando endpoint correto"""
    logger.info(f"🔍 Buscando operador por chat_id: {chat_id}")

    # Usar endpoint específico /api/operadores/por-chat-id/
    result = await fazer_requisicao_api('GET', 'operadores/por-chat-id/', params={'chat_id': chat_id})

    if result and result.get('success'):
        operador = result.get('operador')
        logger.info(f"✅ Operador encontrado por chat_id: {operador.get('nome')}")
        return operador
    else:
        error_msg = result.get('error', 'Erro desconhecido') if result else 'Sem resposta'
        logger.warning(f"⚠️ Operador não encontrado para chat_id {chat_id}: {error_msg}")
        return None

async def atualizar_chat_id_operador(operador_id: int, chat_id: str) -> bool:
    """Atualiza o chat_id do operador"""
    logger.info(f"🔄 Atualizando chat_id do operador {operador_id}")
    
    data = {'chat_id_telegram': str(chat_id)}
    result = await fazer_requisicao_api('PATCH', f'operadores/{operador_id}/', data=data)
    
    if result:
        logger.info(f"✅ Chat_id atualizado para operador {operador_id}")
        return True
    else:
        logger.error(f"❌ Erro ao atualizar chat_id do operador {operador_id}")
        return False

async def buscar_operador_por_chat_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """Busca operador pelo chat_id do Telegram"""
    logger.info(f"🔍 Buscando operador por chat_id: {chat_id}")
    
    result = await fazer_requisicao_api('GET', 'operadores/', params={'chat_id_telegram': chat_id})
    
    if result and result.get('results'):
        operadores = result['results']
        if operadores:
            operador = operadores[0]
            logger.info(f"✅ Operador encontrado por chat_id: {operador.get('nome')}")
            return operador
    
    logger.warning(f"⚠️ Operador não encontrado para chat_id: {chat_id}")
    return None

# ===============================================
# FUNÇÕES DE EQUIPAMENTOS
# ===============================================

async def listar_equipamentos(operador_id: int = None) -> List[Dict[str, Any]]:
    """Lista equipamentos disponíveis"""
    logger.info(f"🔍 Listando equipamentos para operador {operador_id}")
    
    params = {}
    if operador_id:
        params['operador_id'] = operador_id
    
    result = await fazer_requisicao_api('GET', 'equipamentos/', params=params)
    
    if result:
        equipamentos = result.get('results', [])
        logger.info(f"✅ {len(equipamentos)} equipamentos encontrados")
        return equipamentos
    
    logger.warning("⚠️ Nenhum equipamento encontrado")
    return []

async def buscar_equipamento_por_id(equipamento_id: int) -> Optional[Dict[str, Any]]:
    """Busca equipamento pelo ID"""
    logger.info(f"🔍 Buscando equipamento ID: {equipamento_id}")
    
    result = await fazer_requisicao_api('GET', f'equipamentos/{equipamento_id}/')
    
    if result:
        logger.info(f"✅ Equipamento encontrado: {result.get('nome')}")
    else:
        logger.warning(f"⚠️ Equipamento ID {equipamento_id} não encontrado")
    
    return result

async def buscar_equipamento_por_uuid(uuid: str) -> Optional[Dict[str, Any]]:
    """Busca equipamento pelo UUID (QR Code)"""
    logger.info(f"🔍 Buscando equipamento por UUID: {uuid}")
    
    # Tentar endpoint específico por UUID primeiro
    result = await fazer_requisicao_api('GET', f'equipamentos/por-uuid/{uuid}/')
    
    if result:
        logger.info(f"✅ Equipamento encontrado por UUID: {result.get('nome')}")
        return result
    
    # Se não funcionou, tentar busca geral com parâmetro UUID
    result = await fazer_requisicao_api('GET', 'equipamentos/', params={'uuid': uuid})
    
    if result and result.get('results'):
        equipamentos = result['results']
        if equipamentos:
            equipamento = equipamentos[0]
            logger.info(f"✅ Equipamento encontrado por busca UUID: {equipamento.get('nome')}")
            return equipamento
    
    logger.warning(f"⚠️ Equipamento não encontrado para UUID: {uuid}")
    return None

# ===============================================
# FUNÇÕES DE CHECKLISTS NR12
# ===============================================

async def listar_checklists_operador(operador_id: int) -> List[Dict[str, Any]]:
    """Lista checklists disponíveis para o operador"""
    logger.info(f"🔍 Listando checklists para operador {operador_id}")
    
    result = await fazer_requisicao_api('GET', f'operadores/{operador_id}/equipamentos/')
    
    if result and result.get('results'):
        checklists = result['results']
        logger.info(f"✅ {len(checklists)} checklists encontrados")
        return checklists
    
    logger.warning(f"⚠️ Nenhum checklist encontrado para operador {operador_id}")
    return []

async def listar_checklists_equipamento(equipamento_id: int) -> List[Dict[str, Any]]:
    """Lista checklists de um equipamento específico"""
    logger.info(f"🔍 Listando checklists do equipamento {equipamento_id}")
    
    result = await fazer_requisicao_api('GET', f'equipamentos/{equipamento_id}/checklists/')
    
    if result and result.get('checklists'):
        checklists = result['checklists']
        logger.info(f"✅ {len(checklists)} checklists encontrados para equipamento")
        return checklists
    
    logger.warning(f"⚠️ Nenhum checklist encontrado para equipamento {equipamento_id}")
    return []

async def buscar_checklists_nr12() -> List[Dict[str, Any]]:
    """Busca todos os checklists NR12 disponíveis"""
    logger.info("🔍 Buscando checklists NR12")
    
    result = await fazer_requisicao_api('GET', 'nr12/checklists/')
    
    if result:
        checklists = result.get('results', []) if isinstance(result, dict) else result
        logger.info(f"✅ {len(checklists)} checklists encontrados")
        return checklists
    
    logger.warning("⚠️ Nenhum checklist NR12 encontrado")
    return []

async def criar_checklist_nr12(equipamento_id: int, operador_id: int) -> Optional[Dict[str, Any]]:
    """Cria novo checklist NR12"""
    logger.info(f"➕ Criando checklist para equipamento {equipamento_id}")
    
    data = {
        'equipamento_id': equipamento_id,
        'operador_id': operador_id,
        'data_checklist': None  # API definirá a data atual
    }
    
    result = await fazer_requisicao_api('POST', 'nr12/checklists/', data=data)
    
    if result:
        logger.info(f"✅ Checklist criado com ID: {result.get('id')}")
    else:
        logger.error("❌ Erro ao criar checklist")
    
    return result

async def buscar_checklist_por_id(checklist_id: int) -> Optional[Dict[str, Any]]:
    """Busca checklist pelo ID"""
    logger.info(f"🔍 Buscando checklist ID: {checklist_id}")
    
    result = await fazer_requisicao_api('GET', f'nr12/checklists/{checklist_id}/')
    
    if result:
        logger.info(f"✅ Checklist encontrado")
    else:
        logger.warning(f"⚠️ Checklist ID {checklist_id} não encontrado")
    
    return result

async def buscar_itens_checklist_nr12(checklist_id: int) -> List[Dict[str, Any]]:
    """Busca itens de um checklist NR12 específico"""
    logger.info(f"📋 Buscando itens do checklist {checklist_id}")
    
    result = await fazer_requisicao_api('GET', f'nr12/checklists/{checklist_id}/itens/')
    
    if result:
        itens = result.get('results', []) if isinstance(result, dict) else result
        logger.info(f"✅ {len(itens)} itens encontrados")
        return itens
    
    logger.warning(f"⚠️ Nenhum item encontrado para checklist {checklist_id}")
    return []

async def atualizar_item_checklist_nr12(
    item_id: int,
    status: str,
    observacao: str = "",
    operador_codigo: str = "BOT001"
) -> bool:
    """Atualiza item de checklist usando endpoint correto da API"""
    logger.info(f"🔄 Atualizando item {item_id} com status {status}")
    
    data = {
        'item_id': item_id,
        'status': status,
        'observacao': observacao,
        'operador_codigo': operador_codigo
    }
    
    result = await fazer_requisicao_api('POST', 'nr12/bot/item-checklist/atualizar/', data=data)
    
    if result and result.get('success'):
        logger.info(f"✅ Item {item_id} atualizado com sucesso")
        return True
    else:
        logger.error(f"❌ Erro ao atualizar item {item_id}: {result.get('error', 'Erro desconhecido') if result else 'Sem resposta'}")
        return False

async def finalizar_checklist_nr12(checklist_id: int, operador_codigo: str) -> bool:
    """Finaliza checklist NR12"""
    logger.info(f"🏁 Finalizando checklist {checklist_id}")
    
    data = {
        'acao': 'finalizar_checklist',
        'checklist_id': checklist_id,
        'operador_codigo': operador_codigo
    }
    
    # Usar endpoint genérico do bot para finalizar
    result = await fazer_requisicao_api('POST', f'nr12/bot/equipamento/{checklist_id}/', data=data)
    
    if result and result.get('success'):
        logger.info(f"✅ Checklist {checklist_id} finalizado")
        return True
    else:
        logger.error(f"❌ Erro ao finalizar checklist {checklist_id}")
        return False

# ===============================================
# FUNÇÕES DE VALIDAÇÃO
# ===============================================

async def validar_operador(nome: str, data_nascimento: str) -> Optional[Dict[str, Any]]:
    """Valida dados do operador usando endpoint correto"""
    logger.info(f"🔐 Validando operador: {nome}")

    # Usar o endpoint correto /api/operadores/validar-login/
    data = {
        'nome': nome,
        'data_nascimento': data_nascimento
    }

    result = await fazer_requisicao_api('POST', 'operadores/validar-login/', data=data)

    if result and result.get('success'):
        operador_data = result.get('operador')
        logger.info(f"✅ Operador {nome} validado com sucesso")
        return operador_data
    else:
        error_msg = result.get('error', 'Erro desconhecido') if result else 'Sem resposta da API'
        logger.warning(f"⚠️ Falha na validação para {nome}: {error_msg}")
        return None

# ===============================================
# ADICIONAR nova função para buscar por código
# ===============================================

async def buscar_operador_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Busca operador pelo código usando endpoint correto"""
    logger.info(f"🔍 Buscando operador por código: {codigo}")

    # Usar endpoint /api/operadores/busca/ com parâmetro codigo
    result = await fazer_requisicao_api('GET', 'operadores/busca/', params={'codigo': codigo})

    if result and result.get('success') and result.get('results'):
        operadores = result['results']
        if operadores:
            operador = operadores[0]  # Primeiro resultado
            logger.info(f"✅ Operador encontrado por código: {operador.get('nome')}")
            return operador

    logger.warning(f"⚠️ Operador não encontrado para código: {codigo}")
    return None
    

# FUNÇÕES NR12 (ADICIONADAS)
async def buscar_equipamentos_com_nr12(operador_id=None):
    try:
        url = '/equipamentos/'
        params = {'tem_nr12': True}
        if operador_id:
            params['operador_id'] = operador_id
        data = await fazer_requisicao_api('GET', url, params=params)
        return data.get('results', []) if data else []
    except Exception as e:
        logger.error(f'Erro ao buscar equipamentos NR12: {e}')
        return []

async def buscar_checklists_nr12(equipamento_id=None, operador_id=None, status=None):
    try:
        url = '/nr12/checklists/'
        params = {}
        if equipamento_id: params['equipamento'] = equipamento_id
        if operador_id: params['operador_id'] = operador_id
        if status: params['status'] = status
        data = await fazer_requisicao_api('GET', url, params=params)
        return data.get('results', []) if data else []
    except Exception as e:
        logger.error(f'Erro ao buscar checklists: {e}')
        return []

async def criar_checklist_nr12(dados):
    try:
        data = await fazer_requisicao_api('POST', '/nr12/checklists/', json=dados)
        return data
    except Exception as e:
        logger.error(f'Erro ao criar checklist: {e}')
        return None

async def buscar_itens_checklist_nr12(checklist_id):
    try:
        data = await fazer_requisicao_api('GET', f'/nr12/checklists/{checklist_id}/itens/')
        return data.get('results', []) if data else []
    except Exception as e:
        logger.error(f'Erro ao buscar itens: {e}')
        return []

async def atualizar_item_checklist_nr12(item_id, resposta_data):
    try:
        await fazer_requisicao_api('PATCH', f'/nr12/itens-checklist/{item_id}/', json=resposta_data)
        return True
    except Exception as e:
        logger.error(f'Erro ao atualizar item: {e}')
        return False

async def finalizar_checklist_nr12(checklist_id):
    try:
        data = await fazer_requisicao_api('POST', f'/nr12/checklists/{checklist_id}/finalizar/', json={})
        return data
    except Exception as e:
        logger.error(f'Erro ao finalizar: {e}')
        return None

    logger.info(f"✅ Operador {nome} validado com sucesso")
    return operador