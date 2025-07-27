# mandacaru_bot/core/db.py - FUNÇÃO CORRIGIDA
import httpx
import json
from typing import List, Dict, Any, Optional
from core.config import API_BASE_URL, API_TIMEOUT
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Exceção personalizada para erros da API"""
    pass

async def fazer_requisicao_api(method: str, endpoint: str, params: dict = None, json_data: dict = None) -> Optional[Dict[str, Any]]:
    """
    Função corrigida para fazer requisições à API
    """
    url = f"{API_BASE_URL.rstrip('/')}{endpoint}"
    
    # Headers corretos para forçar JSON
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    logger.info(f"🔗 {method} {url}")
    if params:
        logger.info(f"📋 Params: {params}")
    if json_data:
        logger.info(f"📝 Data: {json_data}")
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers
            )
            
            logger.info(f"🔄 Status: {response.status_code}")
            
            # Log da resposta para debug
            content_type = response.headers.get('content-type', '')
            logger.info(f"📄 Content-Type: {content_type}")
            
            if response.status_code == 200:
                # Verificar se é HTML (problema!)
                if 'text/html' in content_type:
                    logger.error("❌ API retornou HTML ao invés de JSON!")
                    logger.error(f"📄 Conteúdo: {response.text[:500]}...")
                    raise APIError("API retornou HTML ao invés de JSON - verificar configuração das rotas")
                
                # Tentar parseizar JSON
                try:
                    data = response.json()
                    logger.info(f"✅ JSON recebido: {type(data)} com {len(data) if isinstance(data, (list, dict)) else 'N/A'} itens")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Erro ao parsear JSON: {e}")
                    logger.error(f"📄 Resposta bruta: {response.text[:500]}")
                    raise APIError("Resposta não é um JSON válido")
            else:
                logger.error(f"❌ Status {response.status_code}: {response.text}")
                raise APIError(f"Erro HTTP {response.status_code}")
                
    except httpx.RequestError as e:
        logger.error(f"❌ Erro de conexão para {url}: {e}")
        raise APIError("Erro de conexão com o servidor")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {type(e).__name__}: {e}")
        raise APIError(f"Erro interno: {str(e)}")

async def buscar_operador_por_nome(nome: str) -> List[Dict[str, Any]]:
    """
    Busca operadores pelo nome na API - VERSÃO CORRIGIDA
    """
    try:
        params = {"search": nome}
        logger.info(f"🔍 Buscando operador: '{nome}'")
        
        data = await fazer_requisicao_api("GET", "/operadores/", params=params)
        
        if data:
            # Verificar se é resposta paginada do DRF
            if isinstance(data, dict) and 'results' in data:
                results = data.get('results', [])
                logger.info(f"📋 API retornou {len(results)} resultado(s) (resposta paginada)")
            elif isinstance(data, list):
                results = data
                logger.info(f"📋 API retornou {len(results)} resultado(s) (resposta direta)")
            else:
                logger.warning(f"⚠️ Formato de resposta inesperado: {type(data)}")
                results = []
            
            # Log detalhado para debug
            if results:
                for i, op in enumerate(results):
                    nome_op = op.get('nome', 'Nome não encontrado')
                    codigo_op = op.get('codigo', 'Código não encontrado')
                    logger.info(f"👤 Operador {i+1}: {codigo_op} - {nome_op}")
            else:
                logger.warning(f"❌ Nenhum operador encontrado para '{nome}'")
                
            return results
        else:
            logger.error("❌ API retornou dados vazios")
            return []
            
    except APIError as e:
        logger.error(f"❌ Erro ao buscar operador por nome '{nome}': {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Erro inesperado na busca por '{nome}': {type(e).__name__}: {e}")
        return []

# Função de teste para verificar API
async def testar_api_operadores():
    """Função para testar se a API está funcionando corretamente"""
    try:
        logger.info("🧪 Testando API de operadores...")
        
        # Teste 1: Endpoint básico
        data = await fazer_requisicao_api("GET", "/operadores/")
        logger.info(f"✅ Endpoint básico funcionando: {type(data)}")
        
        # Teste 2: Busca específica
        results = await buscar_operador_por_nome("willians")
        logger.info(f"✅ Busca específica: {len(results)} resultados")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Teste da API falhou: {e}")
        return False