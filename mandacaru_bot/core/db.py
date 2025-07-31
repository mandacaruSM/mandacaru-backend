# ===============================================
# ADICIONAR NO FINAL DO ARQUIVO: mandacaru_bot/core/db.py
# Funções específicas para API NR12 Real
# ===============================================

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
                logger.info(f"Checklist NR12 criado com ID {checklist.get('id')}")
                return checklist
            else:
                logger.error(f"Erro ao criar checklist NR12: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Erro ao criar checklist NR12: {e}")
        return None

async def buscar_itens_checklist_nr12(checklist_id: int) -> List[Dict[str, Any]]:
    """
    Busca itens de um checklist específico
    
    Args:
        checklist_id: ID do checklist
        
    Returns:
        Lista de itens do checklist
    """
    try:
        url = f"{API_BASE_URL}/nr12/itens-checklist/"
        params = {'checklist': checklist_id}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                itens = data.get('results', []) if isinstance(data, dict) else data
                logger.info(f"Encontrados {len(itens)} itens para checklist {checklist_id}")
                return itens
            else:
                logger.error(f"Erro ao buscar itens do checklist: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Erro ao buscar itens do checklist {checklist_id}: {e}")
        return []

async def atualizar_item_checklist_nr12(
    item_id: int,
    status: str,
    observacao: Optional[str] = None
) -> bool:
    """
    Atualiza um item do checklist
    
    Args:
        item_id: ID do item
        status: Novo status (OK, NOK, PENDENTE)
        observacao: Observação (opcional)
        
    Returns:
        True se atualizado com sucesso
    """
    try:
        url = f"{API_BASE_URL}/nr12/itens-checklist/{item_id}/"
        data = {'status': status}
        
        if observacao:
            data['observacao'] = observacao
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.patch(url, json=data)
            
            if response.status_code == 200:
                logger.info(f"Item checklist {item_id} atualizado para {status}")
                return True
            else:
                logger.error(f"Erro ao atualizar item checklist: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro ao atualizar item checklist {item_id}: {e}")
        return False

async def finalizar_checklist_nr12(checklist_id: int, observacoes: Optional[str] = None) -> bool:
    """
    Finaliza um checklist
    
    Args:
        checklist_id: ID do checklist
        observacoes: Observações finais (opcional)
        
    Returns:
        True se finalizado com sucesso
    """
    try:
        url = f"{API_BASE_URL}/nr12/checklists/{checklist_id}/"
        data = {'status': 'CONCLUIDO'}
        
        if observacoes:
            data['observacoes'] = observacoes
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.patch(url, json=data)
            
            if response.status_code == 200:
                logger.info(f"Checklist {checklist_id} finalizado")
                return True
            else:
                logger.error(f"Erro ao finalizar checklist: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Erro ao finalizar checklist {checklist_id}: {e}")
        return False

async def buscar_checklists_operador_hoje(operador_id: int) -> List[Dict[str, Any]]:
    """
    Busca checklists do operador para hoje
    
    Args:
        operador_id: ID do operador
        
    Returns:
        Lista de checklists do dia
    """
    try:
        hoje = date.today().isoformat()
        
        # Buscar checklists de hoje
        checklists = await buscar_checklists_nr12(
            data_checklist=hoje
        )
        
        # Filtrar por responsável (se aplicável)
        # Na API real, você pode adicionar filtro por responsavel
        checklists_operador = []
        for checklist in checklists:
            # Aqui você pode filtrar por operador se houver campo específico
            checklists_operador.append(checklist)
        
        return checklists_operador
        
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