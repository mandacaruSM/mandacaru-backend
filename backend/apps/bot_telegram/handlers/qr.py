# ================================================================
# QR CODE HANDLER ATUALIZADO - backend/apps/bot_telegram/handlers/qr.py
# ================================================================

def extrair_codigo_equipamento(qr_data: str) -> Optional[str]:
    """
    Extrai código de equipamento dos dados do QR baseado no sistema real.
    O QR Code aponta para: /bot/equipamento/{id}/
    """
    try:
        import json
        import re
        
        logger.info(f"🔍 Extraindo código do QR: {qr_data}")
        
        # MÉTODO 1: JSON estruturado
        try:
            data = json.loads(qr_data)
            if data.get('tipo') == 'equipamento':
                if 'id' in data:
                    logger.info(f"📋 Código extraído via JSON (ID): {data['id']}")
                    return str(data['id'])
                if 'codigo' in data:
                    logger.info(f"📋 Código extraído via JSON (código): {data['codigo']}")
                    return data['codigo']
        except json.JSONDecodeError:
            pass
        
        # MÉTODO 2: URL do QR Code (/bot/equipamento/{id}/)
        url_pattern = r'/bot/equipamento/(\d+)/?'
        match = re.search(url_pattern, qr_data)
        if match:
            equipamento_id = match.group(1)
            logger.info(f"📋 Código extraído via URL: ID {equipamento_id}")
            return equipamento_id
        
        # MÉTODO 3: Padrões de string conhecidos
        patterns = [
            r'^AUT(\d+)$',  # AUT0001
            r'^ESC(\d+)$',  # ESC0001  
            r'^CAR(\d+)$',  # CAR0001
            r'^EQ(\d+)$',   # EQ0001
            r'^(\w{2,5})(\d+)$',  # Qualquer prefixo + números
        ]
        
        for pattern in patterns:
            match = re.match(pattern, qr_data.strip(), re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    # Formato: PREFIXO + NÚMERO (ex: AUT0001)
                    logger.info(f"📋 Código extraído via padrão: {qr_data}")
                    return qr_data.strip()
                else:
                    # Apenas número extraído
                    numero = match.group(1)
                    logger.info(f"📋 Código extraído via padrão (número): {numero}")
                    return numero
        
        # MÉTODO 4: Apenas números (ID direto)
        if re.match(r'^\d{1,6}$', qr_data.strip()):
            logger.info(f"📋 Código extraído como ID: {qr_data}")
            return qr_data.strip()
        
        # MÉTODO 5: Código direto dos equipamentos existentes
        if re.match(r'^[A-Z]{2,5}\d{4}$', qr_data.strip().upper()):
            logger.info(f"📋 Código extraído formato padrão: {qr_data}")
            return qr_data.strip().upper()
        
        logger.warning(f"⚠️ Não foi possível extrair código de: {qr_data}")
        return None
        
    except Exception as e:
        logger.error(f"💥 Erro ao extrair código de equipamento: {e}")
        return None

async def buscar_equipamento_por_codigo(codigo: str):
    """Busca equipamento por código ou ID (versão QR)"""
    try:
        from backend.apps.equipamentos.models import Equipamento
        
        logger.info(f"🔍 [QR] Buscando equipamento: {codigo}")
        
        # Se é número, buscar por ID
        if codigo.isdigit():
            equipamento_id = int(codigo)
            equipamento = await sync_to_async(
                lambda: Equipamento.objects.filter(
                    id=equipamento_id,
                    ativo=True,
                    ativo_nr12=True
                ).exclude(status='INATIVO').select_related('categoria', 'cliente', 'tipo_nr12').first()
            )()
            
            if equipamento:
                logger.info(f"✅ [QR] Equipamento encontrado por ID: {equipamento.nome}")
                return equipamento
        
        # Se começa com letras, buscar por código gerado
        equipamentos = await sync_to_async(
            lambda: list(Equipamento.objects.filter(
                ativo=True,
                ativo_nr12=True
            ).exclude(status='INATIVO').select_related('categoria', 'cliente', 'tipo_nr12'))
        )()
        
        for eq in equipamentos:
            if eq.codigo.upper() == codigo.upper():
                logger.info(f"✅ [QR] Equipamento encontrado por código: {eq.nome}")
                return eq
        
        logger.info(f"❌ [QR] Equipamento não encontrado: {codigo}")
        return None
        
    except Exception as e:
        logger.error(f"💥 [QR] Erro na busca do equipamento: {e}")
        return None