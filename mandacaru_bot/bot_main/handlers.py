# ===============================================
# ARQUIVO COMPLETO: mandacaru_bot/bot_main/handlers.py
# VERSÃO FINAL CORRIGIDA - SEM DUPLICAÇÕES
# ===============================================

import logging
import re
from datetime import datetime
from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import httpx
from core.config import API_BASE_URL, API_TIMEOUT

# Imports do core
from core.session import *
from core.db import (
    buscar_operador_por_nome, 
    buscar_operador_por_chat_id,
    buscar_equipamento_por_uuid,
    atualizar_chat_id_operador
)

logger = logging.getLogger(__name__)

# ===============================================
# UTILITÁRIOS
# ===============================================

def validar_data_nascimento(data_str: str):
    """Valida formato de data DD/MM/AAAA"""
    try:
        return datetime.strptime(data_str, '%d/%m/%Y').date()
    except ValueError:
        return None

def criar_menu_principal():
    """Cria o menu principal do bot"""
    keyboard = [
        [InlineKeyboardButton(text="📋 Checklist", callback_data="menu_checklist")],
        [InlineKeyboardButton(text="⛽ Abastecimento", callback_data="menu_abastecimento")],
        [InlineKeyboardButton(text="🔧 Ordem de Serviço", callback_data="menu_os")],
        [InlineKeyboardButton(text="💰 Financeiro", callback_data="menu_financeiro")],
        [InlineKeyboardButton(text="📱 QR Code", callback_data="menu_qrcode")],
        [InlineKeyboardButton(text="❓ Ajuda", callback_data="menu_ajuda")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ===============================================
# HANDLERS PRINCIPAIS
# ===============================================

async def start_command(message: Message):
    """Comando /start - COM LOGIN AUTOMÁTICO"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "usuário"
        
        # Limpar sessão anterior
        await limpar_sessao(user_id)
        
        # Verificar se chat_id está registrado no banco
        operador_banco = await buscar_operador_por_chat_id(str(user_id))
        
        if operador_banco:
            # LOGIN AUTOMÁTICO!
            await iniciar_sessao(user_id, operador_banco, 'AUTENTICADO')
            
            await message.answer(
                f"👋 **Bem-vindo de volta, {operador_banco.get('nome')}!**\n\n"
                "✅ Login automático realizado com sucesso.\n\n"
                "🏠 Use o menu abaixo para navegar:",
                reply_markup=criar_menu_principal(),
                parse_mode='Markdown'
            )
            return
        
        # Chat_id não registrado - processo normal de login
        await atualizar_sessao(user_id, {'estado': 'AGUARDANDO_NOME'})
        
        await message.answer(
            f"👋 Olá, @{username}!\n\n"
            "🔐 **Primeiro acesso detectado.**\n\n"
            "Para usar o bot, preciso verificar sua identidade.\n\n"
            "👤 **Informe seu nome completo:**"
        )
        
    except Exception as e:
        logger.error(f"Erro no comando start: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

async def handle_qr_code_start(message: Message):
    """Handler para QR codes: /start eq_{uuid} - COM LOGIN AUTOMÁTICO"""
    try:
        comando = message.text.strip()
        user_id = message.from_user.id
        
        # Padrão: /start eq_{uuid}
        match = re.match(r'/start eq_([a-f0-9\-]{36})', comando)
        
        if not match:
            # Se não é QR code, processar normalmente
            await start_command(message)
            return
            
        uuid_equipamento = match.group(1)
        
        # Buscar equipamento na API
        equipamento_data = await buscar_equipamento_por_uuid(uuid_equipamento)
        
        if not equipamento_data:
            await message.answer(
                "❌ **Equipamento Não Encontrado**\n\n"
                "O QR Code escaneado não corresponde a nenhum equipamento válido.",
                parse_mode='Markdown'
            )
            return
        
        # Verificar se usuário JÁ está autenticado na sessão
        operador_sessao = await obter_operador_sessao(user_id)
        
        if operador_sessao:
            # Usuário já logado na sessão - ir direto para menu
            await mostrar_menu_equipamento(message, equipamento_data, operador_sessao)
            return
        
        # Verificar se chat_id está registrado no banco
        operador_banco = await buscar_operador_por_chat_id(str(user_id))
        
        if operador_banco:
            # CHAT_ID JÁ REGISTRADO - LOGIN AUTOMÁTICO!
            await iniciar_sessao(user_id, operador_banco, 'AUTENTICADO')
            
            await message.answer(
                f"👋 **Bem-vindo de volta, {operador_banco.get('nome')}!**\n\n"
                f"📱 Login automático realizado.\n"
                f"🚜 Acessando equipamento **{equipamento_data.get('nome')}**...",
                parse_mode='Markdown'
            )
            
            # Ir direto para menu do equipamento
            await mostrar_menu_equipamento(message, equipamento_data, operador_banco)
            return
        
        # Chat_id NÃO registrado - pedir login manual
        await atualizar_sessao(user_id, {
            'estado': 'AGUARDANDO_NOME',
            'equipamento_qr_uuid': uuid_equipamento,
            'equipamento_qr_data': equipamento_data
        })
        
        await message.answer(
            f"📱 **QR Code: {equipamento_data.get('nome', 'Equipamento')}**\n\n"
            "🔐 Para acessar este equipamento, primeiro faça seu login.\n\n"
            "👤 **Informe seu nome completo:**",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro no QR Code: {e}")
        await message.answer(
            f"❌ **Erro no QR Code**\n\n"
            f"Ocorreu um erro: {str(e)}",
            parse_mode='Markdown'
        )

async def handle_nome(message: Message):
    """Processa nome do operador"""
    try:
        user_id = message.from_user.id
        nome = message.text.strip()
        
        if len(nome) < 3:
            await message.answer("❌ Nome deve ter pelo menos 3 caracteres. Tente novamente:")
            return
        
        # Buscar operador na API
        operador_data = await buscar_operador_por_nome(nome)
        
        if not operador_data:
            await message.answer(
                f"❌ **Operador não encontrado**\n\n"
                f"Nome pesquisado: *{nome}*\n\n"
                "Verifique se digitou corretamente e tente novamente:",
                parse_mode='Markdown'
            )
            return
        
        # Salvar dados temporários e pedir data nascimento
        await atualizar_sessao(user_id, {
            'estado': 'AGUARDANDO_DATA_NASCIMENTO',
            'operador_temp': operador_data,
            'nome_pesquisado': nome
        })
        
        await message.answer(
            f"✅ **Operador encontrado:** {operador_data.get('nome')}\n\n"
            "🗓️ **Para confirmar sua identidade, informe sua data de nascimento:**\n"
            "📅 Formato: DD/MM/AAAA (ex: 15/03/1990)"
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar nome: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

async def handle_data_nascimento(message: Message):
    """Processa data de nascimento e finaliza autenticação"""
    try:
        user_id = message.from_user.id
        data_texto = message.text.strip()
        
        # Validar formato da data
        data_valida = validar_data_nascimento(data_texto)
        
        if not data_valida:
            await message.answer(
                "❌ **Data inválida!**\n\n"
                "Use o formato DD/MM/AAAA (ex: 15/03/1990)\n\n"
                "Digite novamente:"
            )
            return
        
        # Obter dados temporários
        sessao = await obter_sessao(user_id)
        
        if not sessao or not sessao.get('operador_temp'):
            await message.answer("❌ Sessão expirada. Digite /start para recomeçar.")
            return
        
        operador_temp = sessao['operador_temp']
        
        # Validar data de nascimento
        data_cadastro = operador_temp.get('data_nascimento')
        if not data_cadastro:
            await message.answer("❌ Operador não possui data de nascimento cadastrada. Contate o administrador.")
            return
        
        # Comparar datas
        if data_cadastro != data_valida.strftime('%Y-%m-%d'):
            await message.answer(
                "❌ **Data de nascimento incorreta!**\n\n"
                "Verifique a data e tente novamente:"
            )
            return
        
        # AUTENTICAÇÃO BEM-SUCEDIDA!
        
        # Registrar chat_id no banco
        operador_id = operador_temp.get('id')
        sucesso_update = await atualizar_chat_id_operador(operador_id, str(user_id))
        
        if sucesso_update:
            logger.info(f"Chat ID {user_id} registrado para operador {operador_id}")
        
        # Iniciar sessão autenticada
        await iniciar_sessao(user_id, operador_temp, 'AUTENTICADO')
        
        # Verificar se veio de QR code
        if sessao.get('equipamento_qr_data'):
            equipamento_data = sessao['equipamento_qr_data']
            await message.answer(
                f"✅ **Login realizado com sucesso!**\n\n"
                f"👋 Bem-vindo, {operador_temp.get('nome')}!\n\n"
                f"🚜 Acessando equipamento **{equipamento_data.get('nome')}**...",
                parse_mode='Markdown'
            )
            await mostrar_menu_equipamento(message, equipamento_data, operador_temp)
        else:
            # Login normal
            await message.answer(
                f"✅ **Autenticação realizada com sucesso!**\n\n"
                f"👋 Bem-vindo, {operador_temp.get('nome')}!\n\n"
                "🏠 Use o menu abaixo para navegar:",
                reply_markup=criar_menu_principal(),
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"Erro ao processar data nascimento: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")

async def mostrar_menu_equipamento(message: Message, equipamento_data: dict, operador: dict):
    """Mostra menu de ações para o equipamento"""
    
    nome = equipamento_data.get('nome', 'Equipamento')
    horimetro = equipamento_data.get('horimetro_atual', 0)
    status = equipamento_data.get('status_operacional', 'Desconhecido')
    
    # Criar menu
    keyboard = [
        [InlineKeyboardButton(text="📋 Novo Checklist", callback_data=f"eq_checklist_{equipamento_data['id']}")],
        [InlineKeyboardButton(text="⛽ Registrar Abastecimento", callback_data=f"eq_abastecimento_{equipamento_data['id']}")],
        [InlineKeyboardButton(text="🔧 Abrir Ordem de Serviço", callback_data=f"eq_os_{equipamento_data['id']}")],
        [InlineKeyboardButton(text="⏱️ Atualizar Horímetro", callback_data=f"eq_horimetro_{equipamento_data['id']}")],
        [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
    ]
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    mensagem = f"""🚜 **{nome}**

📊 **Status:** {status}
⏱️ **Horímetro:** {horimetro:,.0f}h
👤 **Operador:** {operador.get('nome', 'N/A')}

🎯 **O que você deseja fazer?**"""
    
    await message.answer(mensagem, reply_markup=markup, parse_mode='Markdown')

# ===============================================
# FUNÇÕES DE BUSCA DE CHECKLISTS
# ===============================================

async def buscar_checklists_operador(operador_id: int) -> list:
    """Busca checklists dos equipamentos que o operador pode usar"""
    try:
        # ESTRATÉGIA 1: Buscar equipamentos que o operador pode usar
        equipamentos_autorizados = await buscar_equipamentos_operador(operador_id)
        
        if not equipamentos_autorizados:
            logger.warning(f"Nenhum equipamento autorizado para operador {operador_id}")
            return []
        
        equipamento_ids = [eq.get('id') for eq in equipamentos_autorizados if eq.get('id')]
        logger.info(f"Operador {operador_id} autorizado para equipamentos: {equipamento_ids}")
        
        # ESTRATÉGIA 2: Buscar todos os checklists e filtrar por equipamentos autorizados
        todos_checklists = await buscar_todos_checklists()
        
        # Filtrar checklists dos equipamentos autorizados
        checklists_autorizados = []
        for checklist in todos_checklists:
            equipamento_id = checklist.get('equipamento_id') or checklist.get('equipamento', {}).get('id')
            
            if equipamento_id in equipamento_ids:
                checklists_autorizados.append(checklist)
        
        logger.info(f"Encontrados {len(checklists_autorizados)} checklists para operador {operador_id}")
        return checklists_autorizados
        
    except Exception as e:
        logger.error(f"Erro ao buscar checklists por equipamentos autorizados: {e}")
        return []

async def buscar_equipamentos_operador(operador_id: int) -> list:
    """Busca equipamentos que o operador está autorizado a usar"""
    try:
        urls_teste = [
            f"{API_BASE_URL}/equipamentos/?operador_autorizado={operador_id}",
            f"{API_BASE_URL}/equipamentos/?operador_id={operador_id}",
            f"{API_BASE_URL}/operadores/{operador_id}/equipamentos/",
            f"{API_BASE_URL}/equipamentos/"
        ]
        
        async with httpx.AsyncClient() as client:
            for url in urls_teste:
                try:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        equipamentos = data.get('results', data if isinstance(data, list) else [])
                        
                        if url.endswith('/equipamentos/'):
                            # Se é a URL geral, filtrar apenas equipamentos ativos
                            equipamentos = [eq for eq in equipamentos if eq.get('ativo_nr12', True)]
                        
                        if equipamentos:
                            logger.info(f"Equipamentos encontrados em {url}: {len(equipamentos)}")
                            return equipamentos
                            
                except Exception as e:
                    logger.warning(f"Erro ao tentar {url}: {e}")
                    continue
        
        return []
        
    except Exception as e:
        logger.error(f"Erro ao buscar equipamentos do operador: {e}")
        return []

async def buscar_todos_checklists() -> list:
    """Busca todos os checklists disponíveis"""
    try:
        urls_teste = [
            f"{API_BASE_URL}/nr12/checklists/",
            f"{API_BASE_URL}/checklists/",
            f"{API_BASE_URL}/checklist/",
            f"{API_BASE_URL}/nr12-checklist/"
        ]
        
        async with httpx.AsyncClient() as client:
            for url in urls_teste:
                try:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if isinstance(data, list):
                            logger.info(f"Checklists encontrados em {url}: {len(data)}")
                            return data
                        elif isinstance(data, dict) and 'results' in data:
                            checklists = data['results']
                            logger.info(f"Checklists encontrados em {url}: {len(checklists)}")
                            return checklists
                        elif isinstance(data, dict) and 'data' in data:
                            return data['data']
                            
                except Exception as e:
                    logger.warning(f"Erro ao tentar {url}: {e}")
                    continue
        
        return []
        
    except Exception as e:
        logger.error(f"Erro ao buscar todos os checklists: {e}")
        return []

async def buscar_checklists_equipamento(equipamento_id: int) -> list:
    """Busca checklists de um equipamento específico"""
    try:
        urls_teste = [
            f"{API_BASE_URL}/nr12/checklists/?equipamento_id={equipamento_id}",
            f"{API_BASE_URL}/checklists/?equipamento={equipamento_id}",
            f"{API_BASE_URL}/equipamentos/{equipamento_id}/checklists/",
        ]
        
        async with httpx.AsyncClient() as client:
            for url in urls_teste:
                try:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        checklists = data.get('results', data if isinstance(data, list) else [])
                        
                        if checklists:
                            logger.info(f"Checklists do equipamento {equipamento_id}: {len(checklists)}")
                            return checklists
                            
                except Exception as e:
                    continue
        
        return []
        
    except Exception as e:
        logger.error(f"Erro ao buscar checklists do equipamento {equipamento_id}: {e}")
        return []

async def mostrar_lista_checklists(message: Message, checklists: list, operador: dict):
    """Mostra lista de checklists em botões"""
    try:
        if not checklists:
            await message.answer(
                "📋 **Nenhum checklist encontrado**\n\n"
                "💡 Tente acessar via QR Code do equipamento"
            )
            return
        
        # Criar botões para cada checklist (máximo 10)
        keyboard = []
        for i, checklist in enumerate(checklists[:10]):
            equipamento_nome = checklist.get('equipamento_nome', 'Equipamento')
            data_check = checklist.get('data_checklist', checklist.get('data_realizacao', ''))
            status = checklist.get('status', 'pendente')
            
            # Emoji baseado no status
            emoji = "✅" if status == "concluido" else "⏳" if status == "em_andamento" else "📋"
            
            texto_botao = f"{emoji} {equipamento_nome}"
            callback_data = f"checklist_{checklist.get('id', i)}"
            
            keyboard.append([InlineKeyboardButton(text=texto_botao, callback_data=callback_data)])
        
        # Botão de voltar
        keyboard.append([InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            f"📋 **Seus Checklists ({len(checklists)})**\n\n"
            f"👤 **Operador:** {operador.get('nome')}\n"
            f"📊 **Encontrados:** {len(checklists)} checklists\n\n"
            "🎯 **Selecione um checklist:**",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar lista de checklists: {e}")
        await message.answer("❌ Erro ao exibir checklists")

async def mostrar_links_equipamentos(message: Message):
    """Mostra links diretos para equipamentos conhecidos"""
    try:
        # Equipamentos conhecidos para teste
        equipamentos_teste = [
            {"id": 1, "nome": "Prisma (AUT)", "uuid": "ea23d82d-549b-44bf-8981-7f94e6802461"},
            {"id": 6, "nome": "EH01 (ESC)", "uuid": "9cca38f1-a244-4911-8875-19f1191dd045"}
        ]
        
        keyboard = []
        
        for eq in equipamentos_teste:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🚜 {eq['nome']}", 
                    callback_data=f"link_eq_{eq['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "🔗 **Links dos Equipamentos**\n\n"
            "🎯 **Acesso direto aos equipamentos:**\n"
            "Clique no equipamento desejado para acessar suas opções.\n\n"
            "💡 **Dica:** Você também pode escanear o QR Code físico do equipamento!",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar links de equipamentos: {e}")
        await message.answer("❌ Erro ao carregar equipamentos")

async def processar_link_equipamento(message: Message, equipamento_id: str, operador: dict):
    """Processa clique em link direto de equipamento"""
    try:
        # Buscar dados do equipamento
        equipamento_data = await buscar_equipamento_por_uuid(equipamento_id)
        
        if not equipamento_data:
            # Se não encontrar por UUID, buscar por ID
            equipamentos_teste = {
                "1": {"id": 1, "nome": "Prisma (AUT)", "uuid": "ea23d82d-549b-44bf-8981-7f94e6802461", "horimetro_atual": 1520, "status_operacional": "Operacional"},
                "6": {"id": 6, "nome": "EH01 (ESC)", "uuid": "9cca38f1-a244-4911-8875-19f1191dd045", "horimetro_atual": 2840, "status_operacional": "Operacional"}
            }
            
            equipamento_data = equipamentos_teste.get(equipamento_id)
        
        if not equipamento_data:
            await message.answer("❌ Equipamento não encontrado")
            return
        
        # Mostrar menu do equipamento
        await mostrar_menu_equipamento(message, equipamento_data, operador)
        
    except Exception as e:
        logger.error(f"Erro ao processar link do equipamento {equipamento_id}: {e}")
        await message.answer("❌ Erro ao acessar equipamento")

# ===============================================
# HANDLERS DE CALLBACKS
# ===============================================

async def handle_menu_callback(callback: CallbackQuery):
    """Handler para callbacks do menu"""
    try:
        data = callback.data
        user_id = callback.from_user.id
        
        # Verificar se usuário está autenticado
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada. Digite /start")
            return
        
        # Responder ao callback para remover loading
        await callback.answer()
        
        if data == "menu_checklist":
            # Submenu mais detalhado
            keyboard = [
                [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
                [InlineKeyboardButton(text="🔗 Acessar Equipamentos", callback_data="checklist_qr_links")],
                [InlineKeyboardButton(text="❓ Como Usar", callback_data="checklist_novo")],
                [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
            ]
            
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            await callback.message.answer(
                "📋 **Módulo Checklist**\n\n"
                "🎯 **Opções disponíveis:**\n"
                "• Ver seus checklists\n"
                "• Acessar equipamentos\n"
                "• Aprender a usar\n\n"
                "Escolha uma opção:",
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        elif data == "menu_abastecimento":
            await callback.message.answer(
                "⛽ **Módulo Abastecimento**\n\n"
                "🚧 Em desenvolvimento...\n\n"
                "Em breve você poderá:\n"
                "• Registrar abastecimentos\n"
                "• Controlar consumo\n"
                "• Ver relatórios de custos",
                parse_mode='Markdown'
            )
            
        elif data == "menu_os":
            await callback.message.answer(
                "🔧 **Módulo Ordem de Serviço**\n\n"
                "🚧 Em desenvolvimento...\n\n"
                "Em breve você poderá:\n"
                "• Criar solicitações\n"
                "• Acompanhar status\n"
                "• Ver histórico",
                parse_mode='Markdown'
            )
            
        elif data == "menu_financeiro":
            await callback.message.answer(
                "💰 **Módulo Financeiro**\n\n"
                "🚧 Em desenvolvimento...\n\n"
                "Em breve você poderá:\n"
                "• Consultar relatórios\n"
                "• Acompanhar gastos\n"
                "• Análises financeiras",
                parse_mode='Markdown'
            )
            
        elif data == "menu_qrcode":
            await callback.message.answer(
                "📱 **Módulo QR Code**\n\n"
                "🚧 Em desenvolvimento...\n\n"
                "💡 **Para usar QR Codes:**\n"
                "Escaneie o código de um equipamento para acessá-lo diretamente!",
                parse_mode='Markdown'
            )
            
        elif data == "menu_ajuda":
            await callback.message.answer(
                "❓ **Central de Ajuda**\n\n"
                "🤖 **Como usar o bot:**\n"
                "1. Faça login com /start\n"
                "2. Use os botões do menu\n"
                "3. Escaneie QR codes dos equipamentos\n\n"
                "🆘 **Precisa de ajuda?**\n"
                "Entre em contato com o suporte técnico.",
                parse_mode='Markdown'
            )
            
        elif data == "menu_principal":
            await callback.message.answer(
                f"🏠 **Menu Principal**\n\n"
                f"👋 Olá, {operador.get('nome')}!\n\n"
                "Escolha uma opção:",
                reply_markup=criar_menu_principal(),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Erro no callback do menu: {e}")
        await callback.answer("❌ Erro interno")

async def handle_equipamento_callback(callback: CallbackQuery):
    """Handler para callbacks de equipamentos"""
    try:
        data = callback.data
        user_id = callback.from_user.id
        
        # Verificar autenticação
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        # Extrair ação e ID do equipamento
        parts = data.split("_")
        if len(parts) < 3:
            await callback.message.answer("❌ Comando inválido")
            return
        
        acao = parts[1]  # checklist, abastecimento, os, horimetro
        equipamento_id = parts[2]
        
        if acao == "checklist":
            await callback.message.answer(
                f"📋 **Novo Checklist**\n\n"
                f"🚜 Equipamento ID: {equipamento_id}\n"
                f"👤 Operador: {operador.get('nome')}\n\n"
                "🚧 Funcionalidade em desenvolvimento...",
                parse_mode='Markdown'
            )
            
        elif acao == "abastecimento":
            await callback.message.answer(
                f"⛽ **Registrar Abastecimento**\n\n"
                f"🚜 Equipamento ID: {equipamento_id}\n"
                f"👤 Operador: {operador.get('nome')}\n\n"
                "🚧 Funcionalidade em desenvolvimento...",
                parse_mode='Markdown'
            )
            
        elif acao == "os":
            await callback.message.answer(
                f"🔧 **Nova Ordem de Serviço**\n\n"
                f"🚜 Equipamento ID: {equipamento_id}\n"
                f"👤 Operador: {operador.get('nome')}\n\n"
                "🚧 Funcionalidade em desenvolvimento...",
                parse_mode='Markdown'
            )
            
        elif acao == "horimetro":
            await callback.message.answer(
                f"⏱️ **Atualizar Horímetro**\n\n"
                f"🚜 Equipamento ID: {equipamento_id}\n"
                f"👤 Operador: {operador.get('nome')}\n\n"
                "🚧 Funcionalidade em desenvolvimento...",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Erro no callback de equipamento: {e}")
        await callback.answer("❌ Erro interno")

async def handle_checklist_callback(callback: CallbackQuery):
    """Handler para callbacks de checklist - VERSÃO ÚNICA E COMPLETA"""
    try:
        data = callback.data
        user_id = callback.from_user.id
        
        # Verificar autenticação
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data == "checklist_meus":
            # Informar ao usuário que está buscando
            temp_msg = await callback.message.answer("🔍 Buscando seus checklists...")
            
            # Buscar checklists dos equipamentos autorizados
            operador_id = operador.get('id')
            checklists = await buscar_checklists_operador(operador_id)
            
            # Deletar mensagem temporária
            try:
                await temp_msg.delete()
            except:
                pass
            
            if not checklists:
                # Tentar buscar checklists por equipamentos conhecidos
                checklists_encontrados = []
                equipamentos_teste = [1, 6]  # IDs dos equipamentos prisma e EH01
                
                for eq_id in equipamentos_teste:
                    checklists_eq = await buscar_checklists_equipamento(eq_id)
                    checklists_encontrados.extend(checklists_eq)
                
                if checklists_encontrados:
                    await mostrar_lista_checklists(callback.message, checklists_encontrados, operador)
                    return
                
                # Se realmente não encontrou nada
                keyboard = [
                    [InlineKeyboardButton(text="🔗 Links Equipamentos", callback_data="checklist_qr_links")],
                    [InlineKeyboardButton(text="🔍 Debug: Ver Todos", callback_data="checklist_debug")],
                    [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
                ]
                markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                
                await callback.message.answer(
                    f"📋 **Meus Checklists**\n\n"
                    f"🔍 Nenhum checklist encontrado.\n\n"
                    f"👤 **Operador ID:** {operador_id}\n"
                    f"📊 **Debug:** Use 'Ver Todos' para diagnóstico\n\n"
                    f"💡 **Tente:**\n"
                    f"• Acessar via Links Equipamentos\n"
                    f"• Verificar permissões no sistema",
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                return
            
            # Mostrar lista de checklists encontrados
            await mostrar_lista_checklists(callback.message, checklists, operador)
            
        elif data == "checklist_debug":
            # Função de debug para ver todos os checklists
            temp_msg = await callback.message.answer("🔍 Buscando TODOS os checklists...")
            
            todos_checklists = await buscar_todos_checklists()
            
            try:
                await temp_msg.delete()
            except:
                pass
            
            texto = f"🐛 **Debug - Todos os Checklists**\n\n"
            texto += f"📊 **Total encontrado:** {len(todos_checklists)}\n\n"
            
            # Mostrar primeiros 5 para análise
            for i, checklist in enumerate(todos_checklists[:5]):
                equipamento_id = checklist.get('equipamento_id') or checklist.get('equipamento', {}).get('id', 'N/A')
                equipamento_nome = checklist.get('equipamento_nome') or checklist.get('equipamento', {}).get('nome', 'N/A')
                data_check = checklist.get('data_checklist', checklist.get('data_realizacao', 'N/A'))
                
                texto += f"{i+1}. **Equip ID:** {equipamento_id}\n"
                texto += f"   **Nome:** {equipamento_nome}\n"
                texto += f"   **Data:** {data_check}\n\n"
            
            if len(todos_checklists) > 5:
                texto += f"... e mais {len(todos_checklists) - 5} checklists\n"
            
            keyboard = [
                [InlineKeyboardButton(text="📋 Voltar", callback_data="checklist_meus")],
                [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            await callback.message.answer(texto, reply_markup=markup, parse_mode='Markdown')
            
        elif data == "checklist_novo":
            # Instruções com botões úteis
            keyboard = [
                [InlineKeyboardButton(text="🔗 Links Equipamentos", callback_data="checklist_qr_links")],
                [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
                [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            await callback.message.answer(
                "📋 **Como Criar Novo Checklist**\n\n"
                "🎯 **Método 1 - Links Diretos:**\n"
                "• Clique em 'Links Equipamentos'\n"
                "• Escolha o equipamento\n"
                "• Clique 'Novo Checklist'\n\n"
                "🎯 **Método 2 - QR Code:**\n"
                "• Escaneie QR Code do equipamento\n"
                "• Escolha 'Novo Checklist'\n\n"
                "💡 **Importante:** Você precisa ter autorização para usar o equipamento!",
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        elif data == "checklist_qr_links":
            # Mostrar links diretos para equipamentos
            await mostrar_links_equipamentos(callback.message)
            
        elif data.startswith("link_eq_"):
            # Link direto para equipamento
            equipamento_id = data.split("_")[-1]
            await processar_link_equipamento(callback.message, equipamento_id, operador)
            
    except Exception as e:
        logger.error(f"Erro no callback de checklist: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# REGISTRO DOS HANDLERS - FUNÇÃO LIMPA
# ===============================================

def register_handlers(dp):
    """Registra todos os handlers principais - SEM DUPLICAÇÕES"""
    
    # CALLBACKS (devem vir PRIMEIRO!)
    dp.callback_query.register(handle_menu_callback, F.data.startswith("menu_"))
    dp.callback_query.register(handle_equipamento_callback, F.data.startswith("eq_"))
    dp.callback_query.register(handle_checklist_callback, F.data.startswith("checklist_"))
    
    # MENSAGENS DE TEXTO
    dp.message.register(handle_qr_code_start, F.text.startswith('/start eq_'))
    dp.message.register(start_command, F.text == '/start')
    
    # Filtros para evitar conflitos com botões
    async def filtro_nome_valido(message: Message):
        """Filtro para capturar apenas quando está esperando nome"""
        user_id = message.from_user.id
        estado = await obter_estado_sessao(user_id)
        return estado == 'AGUARDANDO_NOME' and not message.text.startswith(('📋', '⛽', '🔧', '💰', '📱', '❓', '🏠'))
    
    async def filtro_data_valida(message: Message):
        """Filtro para capturar apenas quando está esperando data"""
        user_id = message.from_user.id
        estado = await obter_estado_sessao(user_id)
        return estado == 'AGUARDANDO_DATA_NASCIMENTO' and not message.text.startswith(('📋', '⛽', '🔧', '💰', '📱', '❓', '🏠'))
    
    dp.message.register(handle_nome, filtro_nome_valido)
    dp.message.register(handle_data_nascimento, filtro_data_valida)