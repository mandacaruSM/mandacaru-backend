#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar as correções automaticamente no bot Mandacaru
Execute: python aplicar_correcoes.py
"""

import os
import shutil
from datetime import datetime

def fazer_backup(arquivo):
    """Faz backup de um arquivo"""
    if os.path.exists(arquivo):
        backup = f"{arquivo}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(arquivo, backup)
        print(f"✅ Backup criado: {backup}")
        return True
    return False

def aplicar_correcao_db():
    """Aplica correção no arquivo core/db.py"""
    arquivo = "mandacaru_bot/core/db.py"
    
    print(f"🔧 Aplicando correção em {arquivo}")
    
    # Fazer backup
    if not fazer_backup(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    # Ler arquivo atual
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    # Verificar se já foi corrigido
    if 'chat_id: Optional[str] = None' in conteudo:
        print("✅ Correção já aplicada em core/db.py")
        return True
    
    # Aplicar correção na função atualizar_item_checklist_nr12
    funcao_antiga = '''async def atualizar_item_checklist_nr12(
    item_id: int,
    status: str,
    observacao: str = "",
    responsavel_id: Optional[int] = None
) -> bool:'''

    funcao_nova = '''async def atualizar_item_checklist_nr12(
    item_id: int,
    status: str,
    observacao: str = "",
    responsavel_id: Optional[int] = None,
    chat_id: Optional[str] = None  # NOVO PARÂMETRO
) -> bool:'''

    if funcao_antiga in conteudo:
        conteudo = conteudo.replace(funcao_antiga, funcao_nova)
        print("✅ Assinatura da função atualizada")
    else:
        print("⚠️ Assinatura da função não encontrada - pode já estar corrigida")
    
    # Aplicar correção na lógica da função
    logica_antiga = '''        # Dados conforme documentação da API do bot
        data = {
            'item_id': item_id,
            'status': status_map.get(status, status),
            'observacao': observacao,
            'operador_codigo': 'BOT001'  # Código padrão do bot
        }'''

    logica_nova = '''        # CORREÇÃO: Obter código do operador real
        operador_codigo = 'BOT001'  # Valor padrão
        
        if chat_id:
            # Tentar obter código do operador real
            operador_codigo_real = await obter_codigo_operador_por_chat_id(chat_id)
            if operador_codigo_real:
                operador_codigo = operador_codigo_real
                logger.info(f"✅ Usando operador real: {operador_codigo}")
            else:
                logger.warning(f"⚠️ Operador não encontrado para chat_id: {chat_id}, usando BOT001")
        
        # Dados da requisição
        data = {
            'item_id': item_id,
            'status': status_map.get(status, status),
            'observacao': observacao,
            'operador_codigo': operador_codigo  # AGORA USA OPERADOR REAL
        }'''

    if logica_antiga in conteudo:
        conteudo = conteudo.replace(logica_antiga, logica_nova)
        print("✅ Lógica da função atualizada")
    else:
        print("⚠️ Lógica da função não encontrada - verificar manualmente")
    
    # Adicionar nova função se não existir
    nova_funcao = '''
# ===============================================
# NOVA FUNÇÃO: Buscar operador por chat_id
# ===============================================

async def obter_codigo_operador_por_chat_id(chat_id: str) -> Optional[str]:
    """
    Obtém o código do operador baseado no chat_id do Telegram
    
    Args:
        chat_id: ID do chat do Telegram
        
    Returns:
        Código do operador ou None se não encontrado
    """
    try:
        url = f"{API_BASE_URL}/operadores/"
        params = {'chat_id_telegram': chat_id}
        
        logger.info(f"🔍 Buscando operador para chat_id: {chat_id}")
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                resultados = data.get('results', [])
                
                if resultados:
                    operador = resultados[0]
                    codigo = operador.get('codigo')
                    nome = operador.get('nome', 'N/A')
                    logger.info(f"✅ Operador encontrado: {nome} (código: {codigo})")
                    return codigo
                else:
                    logger.warning(f"⚠️ Nenhum operador encontrado para chat_id: {chat_id}")
                    return None
            else:
                logger.error(f"❌ Erro ao buscar operador: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Erro ao buscar código do operador: {e}")
        return None
'''
    
    if 'obter_codigo_operador_por_chat_id' not in conteudo:
        # Adicionar antes da última linha do arquivo
        conteudo = conteudo.rstrip() + nova_funcao + '\n'
        print("✅ Nova função adicionada")
    else:
        print("✅ Nova função já existe")
    
    # Salvar arquivo corrigido
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"✅ Arquivo {arquivo} atualizado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

def aplicar_correcao_handlers():
    """Aplica correção no arquivo bot_checklist/handlers.py"""
    arquivo = "mandacaru_bot/bot_checklist/handlers.py"
    
    print(f"🔧 Aplicando correção em {arquivo}")
    
    # Fazer backup
    if not fazer_backup(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    # Ler arquivo atual
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    # Verificar se já foi corrigido
    if 'chat_id=chat_id  # NOVO PARÂMETRO' in conteudo:
        print("✅ Correção já aplicada em handlers.py")
        return True
    
    # Aplicar correção nas chamadas da função
    chamada_antiga = '''        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status=status,
            observacao="",
            responsavel_id=operador.get('id')
        )'''

    chamada_nova = '''        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status=status,
            observacao="",
            responsavel_id=operador.get('id'),
            chat_id=chat_id  # NOVO PARÂMETRO
        )'''

    if chamada_antiga in conteudo:
        conteudo = conteudo.replace(chamada_antiga, chamada_nova)
        print("✅ Chamada da função em processar_resposta_item atualizada")
    
    # Corrigir também a chamada em processar_observacao_item
    chamada_obs_antiga = '''        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status='PENDENTE',  # Manter status atual
            observacao=observacao,
            responsavel_id=operador.get('id')
        )'''

    chamada_obs_nova = '''        sucesso = await atualizar_item_checklist_nr12(
            item_id=item_id,
            status='PENDENTE',  # Manter status atual
            observacao=observacao,
            responsavel_id=operador.get('id'),
            chat_id=chat_id  # NOVO PARÂMETRO
        )'''

    if chamada_obs_antiga in conteudo:
        conteudo = conteudo.replace(chamada_obs_antiga, chamada_obs_nova)
        print("✅ Chamada da função em processar_observacao_item atualizada")
    
    # Salvar arquivo corrigido
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"✅ Arquivo {arquivo} atualizado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 APLICANDO CORREÇÕES NO BOT MANDACARU")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("mandacaru_bot"):
        print("❌ Diretório mandacaru_bot não encontrado")
        print("Execute este script a partir da raiz do projeto")
        return False
    
    sucesso_total = True
    
    # Aplicar correções
    print("\n1️⃣ Corrigindo core/db.py...")
    if not aplicar_correcao_db():
        sucesso_total = False
    
    print("\n2️⃣ Corrigindo bot_checklist/handlers.py...")
    if not aplicar_correcao_handlers():
        sucesso_total = False
    
    # Resultado final
    print("\n" + "=" * 50)
    if sucesso_total:
        print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print("\n🔄 Próximos passos:")
        print("1. Reinicie o bot: python mandacaru_bot/start.py")
        print("2. Execute os testes: python teste_correcoes_api.py")
        print("3. Teste manualmente o checklist")
    else:
        print("❌ ALGUMAS CORREÇÕES FALHARAM")
        print("Verifique os erros acima e aplique manualmente")
    
    return sucesso_total

if __name__ == "__main__":
    main()