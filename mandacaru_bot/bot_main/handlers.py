import logging
import re
from datetime import datetime, date
from aiogram import Dispatcher, F, types, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx
import asyncio
from typing import Optional

# Imports do core
from core.config import API_BASE_URL, API_TIMEOUT
from core.session import (
    iniciar_sessao, obter_sessao, atualizar_sessao, 
    limpar_sessao, obter_operador_sessao, obter_estado_sessao, obter_equipamento_atual
)
from core.db import (
    buscar_operador_por_nome, 
    buscar_operador_por_chat_id,
    buscar_equipamento_por_uuid,
    atualizar_chat_id_operador,
    get_checklist_do_dia
)
from core.templates import MessageTemplates
from core.utils import Validators
from core.middleware import require_auth

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data.startswith("checklist_"))
@require_auth
async def processar_checklist_callback(callback: types.CallbackQuery, operador: dict):
    chat_id = callback.from_user.id
    equipamento = await obter_equipamento_atual(str(chat_id))
    if not equipamento:
        await callback.message.answer("❌ Nenhum equipamento selecionado.")
        return

    equipamento_id = equipamento.get("id")
    checklist = await get_checklist_do_dia(equipamento_id)
    if not checklist:
        await callback.message.answer("❌ Nenhum checklist encontrado para hoje.")
        return

    texto = (
        f"<b>Checklist de hoje:</b>\n"
        f"Equipamento: {equipamento['nome']}\n"
        f"Data: {checklist['data_checklist']}\n"
        f"Status: {checklist['status']}"
    )
    await callback.message.answer(texto, parse_mode="HTML")
    await callback.answer()

# ===============================================
# ESTADOS FSM
# ===============================================

class AuthStates(StatesGroup):
    """Estados do processo de autenticação"""
    waiting_for_name = State()
    waiting_for_birth_date = State()

class EquipmentStates(StatesGroup):
    """Estados para interações com equipamentos"""
    waiting_for_fuel_quantity = State()
    waiting_for_fuel_value = State()
    waiting_for_horimeter = State()
    waiting_for_os_description = State()
    waiting_for_checklist_confirm = State()

# ===============================================
# HANDLERS DE AUTENTICAÇÃO
# ===============================================

async def start_handler(message: Message, state: FSMContext):
    """Handler do comando /start - COM LOGIN AUTOMÁTICO"""
    chat_id = str(message.chat.id)
    username = message.from_user.username or "usuário"
    
    try:
        # Verificar se é QR code
        if message.text and message.text.startswith('/start eq_'):
            await handle_qr_code_start(message, state)
            return
            
        # Limpar sessão anterior e estado FSM
        await limpar_sessao(chat_id)
        await state.clear()
        
        # VERIFICAR SE CHAT_ID ESTÁ REGISTRADO NO BANCO
        operador_banco = await buscar_operador_por_chat_id(chat_id)
        
        if operador_banco:
            # LOGIN AUTOMÁTICO! 🎉
            await iniciar_sessao(chat_id, operador_banco, 'AUTENTICADO')
            
            await message.answer(
                f"👋 **Bem-vindo de volta, {operador_banco.get('nome')}!**\n\n"
                "✅ Login automático realizado com sucesso.\n\n"
                "🏠 Use o menu abaixo para navegar:",
                reply_markup=criar_menu_principal(),
                parse_mode='HTML'
            )
            return
        
        # Chat_id não registrado - processo normal de login
        await message.answer(
            f"👋 Olá, @{username}!\n\n"
            "🔐 **Primeiro acesso detectado.**\n\n"
            "Para usar o bot, preciso verificar sua identidade.\n\n"
            "👤 **Informe seu nome completo:**",
            parse_mode="Markdown"
        )
        
        await state.set_state(AuthStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"Erro no comando start: {e}")
        await message.answer("❌ Erro interno. Tente novamente.")


async def process_name(message: Message, state: FSMContext):
    """Processa o nome do operador"""
    nome = message.text.strip()
    
    if len(nome) < 3:
        await message.answer(
            "❌ Nome muito curto. Digite seu nome completo:",
            parse_mode="Markdown"
        )
        return
    
    try:
        # Buscar operador na API
        operadores = await buscar_operador_por_nome(nome)
        
        if not operadores:
            await message.answer(
                "❌ Operador não encontrado.\n\n"
                "Verifique se digitou o nome corretamente ou entre em contato com o administrador.\n\n"
                "Digite /start para tentar novamente.",
                parse_mode="Markdown"
            )
            await state.clear()
            return
        
        # Se encontrou múltiplos, pega o primeiro
        operador = operadores[0]
        
        # Salvar dados temporários no estado
        await state.update_data(operador=operador)
        
        await message.answer(
            f"✅ Olá, **{operador['nome']}**!\n\n"
            f"Agora digite sua **data de nascimento** (DD/MM/AAAA):",
            parse_mode="Markdown"
        )
        
        await state.set_state(AuthStates.waiting_for_birth_date)
        
    except Exception as e:
        logger.error(f"Erro ao buscar operador: {e}")
        await message.answer(
            MessageTemplates.error_template(
                "Erro na Busca",
                "Não foi possível verificar seu cadastro. Tente novamente mais tarde."
            ),
            parse_mode="Markdown"
        )
        await state.clear()

async def process_birth_date(message: Message, state: FSMContext):
    """Processa a data de nascimento para validação"""
    data_texto = message.text.strip()
    
    # Validar formato
    try:
        # Aceitar formatos DD/MM/YYYY
        data_valida = datetime.strptime(data_texto, '%d/%m/%Y').date()
    except ValueError:
        await message.answer(
            "❌ Data inválida. Use o formato DD/MM/AAAA\n"
            "Exemplo: 15/03/1990",
            parse_mode="Markdown"
        )
        return
    
    try:
        # Recuperar dados do estado
        data = await state.get_data()
        operador = data.get('operador')
        
        if not operador:
            await message.answer(
                "❌ Sessão expirada. Digite /start para recomeçar.",
                parse_mode="Markdown"
            )
            await state.clear()
            return
        
        # Validar data de nascimento
        data_nascimento_api = operador.get('data_nascimento')
        
        # Converter data da API para o mesmo formato
        if data_nascimento_api:
            # Se vier no formato YYYY-MM-DD, converter para comparação
            try:
                data_api_obj = datetime.strptime(data_nascimento_api, '%Y-%m-%d').date()
            except:
                data_api_obj = None
        else:
            data_api_obj = None
        
        if data_api_obj != data_valida:
            await message.answer(
                "❌ Data de nascimento incorreta.\n\n"
                "Por segurança, o acesso foi negado.\n"
                "Digite /start para tentar novamente.",
                parse_mode="Markdown"
            )
            await state.clear()
            return
        
        # IMPORTANTE: Atualizar chat_id na API
        chat_id = str(message.chat.id)
        operador_id = operador['id']
        
        sucesso = await atualizar_chat_id_operador(operador_id, chat_id)
        
        if sucesso:
            logger.info(f"✅ Chat ID {chat_id} registrado para operador {operador_id}")
        else:
            logger.warning(f"⚠️ Falha ao atualizar chat_id para operador {operador_id}")
        
        # Criar sessão autenticada
        await iniciar_sessao(
            chat_id,
            {
                'id': operador['id'],
                'nome': operador['nome'],
                'is_admin': operador.get('is_admin', False),
                'funcao': operador.get('funcao', 'Operador')
            },
            'AUTENTICADO'
        )
        
        # Limpar estado do FSM
        await state.clear()
        
        # Verificar se veio de QR code
        equipamento_qr = data.get('equipamento_qr_data')
        if equipamento_qr:
            await message.answer(
                f"✅ **Login realizado com sucesso!**\n\n"
                f"👋 Bem-vindo, {operador['nome']}!\n\n"
                f"🚜 Acessando equipamento **{equipamento_qr.get('nome')}**...",
                parse_mode='HTML'
            )
            await mostrar_menu_equipamento(message, equipamento_qr, operador)
        else:
            # Mostrar menu principal
            await show_main_menu(message, operador)
        
    except Exception as e:
        logger.error(f"Erro no processo de autenticação: {e}")
        await message.answer(
            MessageTemplates.error_template(
                "Erro na Autenticação", 
                "Não foi possível completar o login. Tente novamente."
            ),
            parse_mode="Markdown"
        )
        await state.clear()

# ===============================================
# HANDLERS DE QR CODE
# ===============================================

async def handle_qr_code_start(message: Message, state: FSMContext):
    """Handler para QR codes: /start eq_{uuid}"""
    try:
        comando = message.text.strip()
        chat_id = str(message.chat.id)
        
        # Padrão: /start eq_{uuid}
        match = re.match(r'/start eq_([a-f0-9\-]{36})', comando)
        
        if not match:
            # Se não é QR code, processar normalmente
            await start_handler(message, state)
            return
            
        uuid_equipamento = match.group(1)
        
        # Buscar equipamento na API
        equipamento_data = await buscar_equipamento_por_uuid(uuid_equipamento)
        
        if not equipamento_data:
            await message.answer(
                "❌ **Equipamento Não Encontrado**\n\n"
                "O QR Code escaneado não corresponde a nenhum equipamento válido.",
                parse_mode='HTML'
            )
            return
        
        # Verificar se usuário está autenticado
        operador = await obter_operador_sessao(chat_id)
        
        if operador:
            # Usuário já logado - ir direto para menu
            await mostrar_menu_equipamento(message, equipamento_data, operador)
            return
        
        # Verificar se chat_id está registrado no banco
        operador_banco = await buscar_operador_por_chat_id(chat_id)
        
        if operador_banco:
            # LOGIN AUTOMÁTICO
            await iniciar_sessao(chat_id, operador_banco, 'AUTENTICADO')
            
            await message.answer(
                f"👋 **Bem-vindo de volta, {operador_banco.get('nome')}!**\n\n"
                f"📱 Login automático realizado.\n"
                f"🚜 Acessando equipamento **{equipamento_data.get('nome')}**...",
                parse_mode='HTML'
            )
            
            await mostrar_menu_equipamento(message, equipamento_data, operador_banco)
            return
        
        # Não registrado - pedir login
        await state.update_data(
            equipamento_qr_uuid=uuid_equipamento,
            equipamento_qr_data=equipamento_data
        )
        
        await message.answer(
            f"📱 **QR Code: {equipamento_data.get('nome', 'Equipamento')}**\n\n"
            "🔐 Para acessar este equipamento, primeiro faça seu login.\n\n"
            "👤 **Informe seu nome completo:**",
            parse_mode='HTML'
        )
        
        await state.set_state(AuthStates.waiting_for_name)
        
    except Exception as e:
        logger.error(f"Erro no QR Code: {e}")
        await message.answer(
            f"❌ **Erro no QR Code**\n\n"
            f"Ocorreu um erro: {str(e)}",
            parse_mode='HTML'
        )

# ===============================================
# MENUS E NAVEGAÇÃO
# ===============================================

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

async def show_main_menu(message: Message, operador: dict):
    """Mostra o menu principal após autenticação"""
    keyboard = criar_menu_principal()
    
    is_admin = operador.get('is_admin', False)
    admin_text = "\n\n🔑 *Você tem privilégios de administrador!*\nUse /admin para acessar o painel." if is_admin else ""
    
    await message.answer(
        f"✅ **Login realizado com sucesso!**\n\n"
        f"👤 Operador: {operador['nome']}\n"
        f"💼 Função: {operador.get('funcao', 'Operador')}\n"
        f"🕐 Horário: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        f"{admin_text}\n\n"
        f"Escolha uma opção abaixo:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def mostrar_menu_equipamento(message: Message, equipamento_data: dict, operador: dict):
    """Mostra menu de ações para o equipamento"""
    try:
        equipamento_id = equipamento_data.get('id')
        nome = equipamento_data.get('nome', 'Equipamento')
        horimetro = equipamento_data.get('horimetro_atual', 0)
        status = equipamento_data.get('status_operacional', 'Desconhecido')
        
        # Criar menu
        keyboard = [
            [InlineKeyboardButton(text="📋 Novo Checklist NR12", callback_data=f"eq_novo_checklist_{equipamento_id}")],
            [InlineKeyboardButton(text="⛽ Registrar Abastecimento", callback_data=f"eq_abastecimento_{equipamento_id}")],
            [InlineKeyboardButton(text="🔧 Abrir Ordem de Serviço", callback_data=f"eq_os_{equipamento_id}")],
            [InlineKeyboardButton(text="⏱️ Atualizar Horímetro", callback_data=f"eq_horimetro_{equipamento_id}")],
            [InlineKeyboardButton(text="📊 Ver Histórico", callback_data=f"eq_historico_{equipamento_id}")],
            [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
        ]
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        mensagem = f"""🚜 **{nome}**

📊 **Status:** {status}
⏱️ **Horímetro:** {horimetro:,.0f}h
👤 **Operador:** {operador.get('nome', 'N/A')}

🎯 **O que você deseja fazer?**"""
        
        await message.answer(
            mensagem,
            reply_markup=markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Erro ao mostrar menu do equipamento: {e}")
        await message.answer("❌ Erro ao carregar dados do equipamento")

# ===============================================
# HANDLERS DE CALLBACK
# ===============================================

async def handle_menu_callback(callback: CallbackQuery):
    """Handler para callbacks do menu principal"""
    try:
        data = callback.data
        user_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada. Digite /start")
            return
        
        await callback.answer()
        
        if data == "menu_checklist":
            keyboard = [
                [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="checklist_meus")],
                [InlineKeyboardButton(text="🔗 Acessar Equipamentos", callback_data="checklist_links")],
                [InlineKeyboardButton(text="❓ Como Usar", callback_data="checklist_ajuda")],
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
                parse_mode='HTML'
            )
            
        elif data == "menu_principal":
            await callback.message.answer(
                f"🏠 **Menu Principal**\n\n"
                f"👋 Olá, {operador.get('nome')}!\n\n"
                "Escolha uma opção:",
                reply_markup=criar_menu_principal(),
                parse_mode='HTML'
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
                parse_mode='HTML'
            )
            
        else:
            await callback.message.answer(
                f"🚧 **{data.replace('menu_', '').title()}**\n\n"
                "Este módulo está em desenvolvimento.",
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Erro no callback do menu: {e}")
        await callback.answer("❌ Erro interno")

async def handle_equipamento_callback(callback: CallbackQuery, state: FSMContext):
    """Handler atualizado para callbacks de equipamento"""
    try:
        data = callback.data
        user_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        # Processar novo checklist NR12
        if data.startswith("eq_novo_checklist_"):
            equipamento_id = data.split("_")[-1]
            await processar_novo_checklist_nr12(callback, state, equipamento_id, operador)
            
        elif data.startswith("eq_abastecimento_"):
            equipamento_id = data.split("_")[-1]
            await processar_abastecimento(callback, state, equipamento_id, operador)
            
        elif data.startswith("eq_os_"):
            equipamento_id = data.split("_")[-1]
            await processar_ordem_servico(callback, state, equipamento_id, operador)
            
        elif data.startswith("eq_horimetro_"):
            equipamento_id = data.split("_")[-1]
            await processar_horimetro(callback, state, equipamento_id, operador)
            
        elif data.startswith("eq_historico_"):
            equipamento_id = data.split("_")[-1]
            await mostrar_historico_equipamento(callback, equipamento_id, operador)
            
        elif data.startswith("criar_checklist_"):
            # Formato: criar_checklist_{equipamento_id}_{turno}
            partes = data.split("_")
            equipamento_id = partes[2]
            turno = partes[3]
            await criar_checklist_nr12(callback, state, equipamento_id, turno, operador)
            
        elif data.startswith("confirmar_checklist_"):
            await confirmar_criacao_checklist(callback, state)
            
        elif data.startswith("cancelar_"):
            await callback.message.answer("❌ Operação cancelada.")
            await state.clear()
            
    except Exception as e:
        logger.error(f"Erro no callback de equipamento: {e}")
        await callback.answer("❌ Erro interno")

async def handle_checklist_callback(callback: CallbackQuery):
    """Handler para callbacks de checklist"""
    try:
        data = callback.data
        user_id = str(callback.from_user.id)
        
        # Verificar autenticação
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data == "checklist_links":
            # Mostrar equipamentos de exemplo
            keyboard = [
                [InlineKeyboardButton(text="🚜 Prisma (AUT)", callback_data="link_eq_1")],
                [InlineKeyboardButton(text="🚜 EH01 (ESC)", callback_data="link_eq_6")],
                [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
            ]
            
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            await callback.message.answer(
                "🔗 **Links dos Equipamentos**\n\n"
                "Clique no equipamento desejado para acessar suas opções.\n\n"
                "💡 **Dica:** Você também pode escanear o QR Code físico do equipamento!",
                reply_markup=markup,
                parse_mode='HTML'
            )
            
        elif data.startswith("link_eq_"):
            # Processar link de equipamento
            equipamento_id = data.split("_")[-1]
            
            # Dados de exemplo
            equipamentos_exemplo = {
                "1": {"id": 1, "nome": "Prisma (AUT)", "horimetro_atual": 1520, "status_operacional": "Operacional"},
                "6": {"id": 6, "nome": "EH01 (ESC)", "horimetro_atual": 2840, "status_operacional": "Operacional"}
            }
            
            equipamento_data = equipamentos_exemplo.get(equipamento_id)
            
            if equipamento_data:
                await mostrar_menu_equipamento(callback.message, equipamento_data, operador)
            else:
                await callback.message.answer("❌ Equipamento não encontrado")
                
        else:
            await callback.message.answer(
                f"🚧 **Checklist - {data}**\n\n"
                "Funcionalidade em desenvolvimento...",
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Erro no callback de checklist: {e}")
        await callback.answer("❌ Erro interno")

async def processar_novo_checklist_nr12(callback: CallbackQuery, state: FSMContext, equipamento_id: str, operador: dict):
    """Processa criação de novo checklist NR12"""
    try:
        await callback.answer("📋 Verificando checklists...")
        
        # Buscar checklists do dia
        hoje = date.today().strftime('%Y-%m-%d')
        
        # Verificar checklists existentes via API
        url = f"{API_BASE_URL}/nr12/checklists/"
        params = {
            'equipamento_id': equipamento_id,
            'data_checklist': hoje
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                checklists_hoje = data.get('results', [])
                
                # Verificar turnos já realizados
                turnos_realizados = [c.get('turno') for c in checklists_hoje if c.get('turno')]
                
                turnos_disponiveis = []
                todos_turnos = [
                    {'valor': 'MATUTINO', 'texto': 'Matutino (06:00-14:00)', 'emoji': '🌅'},
                    {'valor': 'VESPERTINO', 'texto': 'Vespertino (14:00-22:00)', 'emoji': '☀️'},
                    {'valor': 'NOTURNO', 'texto': 'Noturno (22:00-06:00)', 'emoji': '🌙'}
                ]
                
                for turno in todos_turnos:
                    if turno['valor'] not in turnos_realizados:
                        turnos_disponiveis.append(turno)
                
                if not turnos_disponiveis:
                    await callback.message.answer(
                        "✅ **Todos os turnos já foram realizados hoje!**\n\n"
                        f"📅 Data: {hoje}\n"
                        f"🚜 Equipamento ID: {equipamento_id}\n\n"
                        "Volte amanhã para novos checklists.",
                        parse_mode='HTML'
                    )
                    return
                
                # Montar teclado com turnos disponíveis
                keyboard = []
                for turno in turnos_disponiveis:
                    keyboard.append([
                        InlineKeyboardButton(
                            text=f"{turno['emoji']} {turno['texto']}", 
                            callback_data=f"criar_checklist_{equipamento_id}_{turno['valor']}"
                        )
                    ])
                
                keyboard.append([
                    InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar_checklist")
                ])
                
                markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                
                texto_turnos_realizados = ""
                if turnos_realizados:
                    texto_turnos_realizados = f"\n✅ **Turnos já realizados hoje:** {', '.join(turnos_realizados)}"
                
                await callback.message.answer(
                    f"📋 **Novo Checklist NR12**\n\n"
                    f"🚜 Equipamento ID: {equipamento_id}\n"
                    f"📅 Data: {hoje}{texto_turnos_realizados}\n\n"
                    f"🕐 **Selecione o turno:**",
                    reply_markup=markup,
                    parse_mode='HTML'
                )
                
    except Exception as e:
        logger.error(f"Erro ao processar novo checklist: {e}")
        await callback.message.answer("❌ Erro ao criar checklist. Tente novamente.")

# ===============================================
# FUNÇÃO: CRIAR CHECKLIST NR12
# ===============================================

async def criar_checklist_nr12(callback: CallbackQuery, state: FSMContext, equipamento_id: str, turno: str, operador: dict):
    """Cria checklist NR12 via API"""
    try:
        await callback.answer("⏳ Criando checklist...")
        
        # Preparar dados
        dados = {
            'equipamento_id': int(equipamento_id),
            'operador_id': operador.get('id'),
            'turno': turno,
            'data_checklist': date.today().strftime('%Y-%m-%d'),
            'status': 'PENDENTE'
        }
        
        # Salvar no estado para confirmação
        await state.update_data(
            checklist_data=dados,
            equipamento_id=equipamento_id,
            turno=turno
        )
        
        # Pedir confirmação
        keyboard = [
            [InlineKeyboardButton(text="✅ Confirmar", callback_data="confirmar_checklist_sim")],
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="confirmar_checklist_nao")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        turno_texto = {
            'MATUTINO': '🌅 Matutino',
            'VESPERTINO': '☀️ Vespertino',
            'NOTURNO': '🌙 Noturno'
        }.get(turno, turno)
        
        await callback.message.answer(
            f"📋 **Confirmar Criação do Checklist**\n\n"
            f"🚜 Equipamento ID: {equipamento_id}\n"
            f"🕐 Turno: {turno_texto}\n"
            f"📅 Data: {date.today().strftime('%d/%m/%Y')}\n"
            f"👤 Operador: {operador.get('nome')}\n\n"
            f"Deseja criar este checklist?",
            reply_markup=markup,
            parse_mode='HTML'
        )
        
        await state.set_state(EquipmentStates.waiting_for_checklist_confirm)
        
    except Exception as e:
        logger.error(f"Erro ao criar checklist: {e}")
        await callback.message.answer("❌ Erro ao criar checklist")

# ===============================================
# FUNÇÃO: PROCESSAR ABASTECIMENTO
# ===============================================

async def processar_abastecimento(callback: CallbackQuery, state: FSMContext, equipamento_id: str, operador: dict):
    """Inicia processo de registro de abastecimento"""
    try:
        # Salvar equipamento_id no estado
        await state.update_data(
            equipamento_id=equipamento_id,
            operador_id=operador.get('id')
        )
        
        # Criar teclado para cancelar
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Cancelar")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await callback.message.answer(
            f"⛽ **Registrar Abastecimento**\n\n"
            f"🚜 Equipamento ID: {equipamento_id}\n"
            f"👤 Operador: {operador.get('nome')}\n\n"
            f"Digite a quantidade de combustível em litros:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await state.set_state(EquipmentStates.waiting_for_fuel_quantity)
        
    except Exception as e:
        logger.error(f"Erro ao processar abastecimento: {e}")
        await callback.message.answer("❌ Erro ao iniciar abastecimento")

# ===============================================
# FUNÇÃO: PROCESSAR ORDEM DE SERVIÇO
# ===============================================

async def processar_ordem_servico(callback: CallbackQuery, state: FSMContext, equipamento_id: str, operador: dict):
    """Inicia processo de criação de ordem de serviço"""
    try:
        await state.update_data(
            equipamento_id=equipamento_id,
            operador_id=operador.get('id')
        )
        
        # Criar teclado com tipos de OS
        keyboard = [
            [InlineKeyboardButton(text="🔧 Manutenção Corretiva", callback_data="os_tipo_corretiva")],
            [InlineKeyboardButton(text="🛠️ Manutenção Preventiva", callback_data="os_tipo_preventiva")],
            [InlineKeyboardButton(text="🚨 Urgente", callback_data="os_tipo_urgente")],
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancelar_os")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.answer(
            f"🔧 **Nova Ordem de Serviço**\n\n"
            f"🚜 Equipamento ID: {equipamento_id}\n"
            f"👤 Solicitante: {operador.get('nome')}\n\n"
            f"Selecione o tipo de OS:",
            reply_markup=markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar OS: {e}")
        await callback.message.answer("❌ Erro ao criar ordem de serviço")

# ===============================================
# FUNÇÃO: PROCESSAR HORÍMETRO
# ===============================================

async def processar_horimetro(callback: CallbackQuery, state: FSMContext, equipamento_id: str, operador: dict):
    """Inicia processo de atualização de horímetro"""
    try:
        # Buscar horímetro atual
        url = f"{API_BASE_URL}/equipamentos/{equipamento_id}/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                equipamento = response.json()
                horimetro_atual = equipamento.get('horimetro_atual', 0)
                
                await state.update_data(
                    equipamento_id=equipamento_id,
                    horimetro_atual=horimetro_atual
                )
                
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="❌ Cancelar")]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                
                await callback.message.answer(
                    f"⏱️ **Atualizar Horímetro**\n\n"
                    f"🚜 Equipamento ID: {equipamento_id}\n"
                    f"📊 Horímetro atual: {horimetro_atual:,.0f}h\n\n"
                    f"Digite o novo valor do horímetro:",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                await state.set_state(EquipmentStates.waiting_for_horimeter)
            else:
                await callback.message.answer("❌ Erro ao buscar dados do equipamento")
                
    except Exception as e:
        logger.error(f"Erro ao processar horímetro: {e}")
        await callback.message.answer("❌ Erro ao atualizar horímetro")

# ===============================================
# FUNÇÃO: MOSTRAR HISTÓRICO
# ===============================================

async def mostrar_historico_equipamento(callback: CallbackQuery, equipamento_id: str, operador: dict):
    """Mostra histórico do equipamento"""
    try:
        await callback.answer("📊 Carregando histórico...")
        
        # Buscar dados do equipamento
        url = f"{API_BASE_URL}/equipamentos/{equipamento_id}/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                equipamento = response.json()
                
                # Simular histórico (substituir por dados reais da API)
                texto = f"📊 **Histórico do Equipamento**\n\n"
                texto += f"🚜 **{equipamento.get('nome', 'Equipamento')}**\n"
                texto += f"📍 ID: {equipamento_id}\n\n"
                
                texto += "**📋 Últimos Checklists:**\n"
                texto += "• 30/07/2025 - Matutino - ✅ Concluído\n"
                texto += "• 29/07/2025 - Vespertino - ✅ Concluído\n"
                texto += "• 29/07/2025 - Matutino - ✅ Concluído\n\n"
                
                texto += "**⛽ Últimos Abastecimentos:**\n"
                texto += "• 28/07/2025 - 150L - R$ 975,00\n"
                texto += "• 25/07/2025 - 200L - R$ 1.300,00\n\n"
                
                texto += "**🔧 Últimas Manutenções:**\n"
                texto += "• 20/07/2025 - Troca de óleo\n"
                texto += "• 15/07/2025 - Revisão geral\n\n"
                
                texto += f"⏱️ **Horímetro:** {equipamento.get('horimetro_atual', 0):,.0f}h\n"
                texto += f"📊 **Status:** {equipamento.get('status_operacional', 'N/A')}"
                
                # Botão para voltar
                keyboard = [
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"link_eq_{equipamento_id}")]
                ]
                markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                
                await callback.message.answer(
                    texto,
                    reply_markup=markup,
                    parse_mode='HTML'
                )
            else:
                await callback.message.answer("❌ Erro ao buscar histórico")
                
    except Exception as e:
        logger.error(f"Erro ao mostrar histórico: {e}")
        await callback.message.answer("❌ Erro ao carregar histórico")

# ===============================================
# HANDLERS PARA PROCESSAR INPUTS DO USUÁRIO
# ===============================================

async def process_fuel_quantity(message: Message, state: FSMContext):
    """Processa quantidade de combustível"""
    if message.text == "❌ Cancelar":
        await message.answer("❌ Abastecimento cancelado.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    
    try:
        quantidade = float(message.text.replace(',', '.'))
        if quantidade <= 0:
            await message.answer("❌ A quantidade deve ser maior que zero. Digite novamente:")
            return
        
        await state.update_data(quantidade_combustivel=quantidade)
        
        await message.answer(
            f"💰 Digite o valor total do abastecimento (R$):",
            parse_mode='HTML'
        )
        
        await state.set_state(EquipmentStates.waiting_for_fuel_value)
        
    except ValueError:
        await message.answer("❌ Valor inválido. Digite apenas números:")

async def process_fuel_value(message: Message, state: FSMContext):
    """Processa valor do combustível"""
    if message.text == "❌ Cancelar":
        await message.answer("❌ Abastecimento cancelado.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    
    try:
        # Remover R$ e converter vírgula para ponto
        valor_texto = message.text.replace('R$', '').replace(',', '.').strip()
        valor = float(valor_texto)
        
        if valor <= 0:
            await message.answer("❌ O valor deve ser maior que zero. Digite novamente:")
            return
        
        # Recuperar dados do estado
        data = await state.get_data()
        quantidade = data.get('quantidade_combustivel')
        equipamento_id = data.get('equipamento_id')
        operador_id = data.get('operador_id')
        
        # Calcular preço por litro
        preco_litro = valor / quantidade
        
        # Aqui você enviaria para a API
        # Por enquanto, apenas confirmar
        
        await message.answer(
            f"✅ **Abastecimento Registrado!**\n\n"
            f"🚜 Equipamento ID: {equipamento_id}\n"
            f"⛽ Quantidade: {quantidade:.1f}L\n"
            f"💰 Valor total: R$ {valor:.2f}\n"
            f"📊 Preço/litro: R$ {preco_litro:.2f}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"✅ Dados salvos com sucesso!",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Valor inválido. Digite apenas números:")

async def process_horimeter_value(message: Message, state: FSMContext):
    """Processa novo valor do horímetro"""
    if message.text == "❌ Cancelar":
        await message.answer("❌ Atualização cancelada.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    
    try:
        novo_horimetro = float(message.text.replace(',', '.'))
        
        data = await state.get_data()
        horimetro_atual = data.get('horimetro_atual', 0)
        equipamento_id = data.get('equipamento_id')
        
        if novo_horimetro < horimetro_atual:
            await message.answer(
                f"⚠️ O novo valor ({novo_horimetro:.0f}h) é menor que o atual ({horimetro_atual:.0f}h).\n"
                f"Digite novamente ou cancele a operação:"
            )
            return
        
        diferenca = novo_horimetro - horimetro_atual
        
        # Aqui você atualizaria na API
        
        await message.answer(
            f"✅ **Horímetro Atualizado!**\n\n"
            f"🚜 Equipamento ID: {equipamento_id}\n"
            f"📊 Valor anterior: {horimetro_atual:,.0f}h\n"
            f"📊 Novo valor: {novo_horimetro:,.0f}h\n"
            f"📈 Diferença: +{diferenca:.0f}h\n"
            f"📅 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"✅ Dados salvos com sucesso!",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Valor inválido. Digite apenas números:")

# ===============================================
# ADICIONAR NO REGISTRO DE HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers principais"""
    
    # ... handlers existentes ...
    
    # Estados de equipamento
    dp.message.register(process_fuel_quantity, EquipmentStates.waiting_for_fuel_quantity)
    dp.message.register(process_fuel_value, EquipmentStates.waiting_for_fuel_value)
    dp.message.register(process_horimeter_value, EquipmentStates.waiting_for_horimeter)
    
    # Callbacks de OS
    dp.callback_query.register(handle_os_type_callback, F.data.startswith("os_tipo_"))
    dp.callback_query.register(handle_checklist_confirm_callback, F.data.startswith("confirmar_checklist_"))
    
    logger.info("Handlers principais registrados com sucesso")

# ===============================================
# REGISTRO DOS HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers principais"""
    
    # Comandos
    dp.message.register(start_handler, Command("start"))
    
    # Estados de autenticação
    dp.message.register(process_name, AuthStates.waiting_for_name)
    dp.message.register(process_birth_date, AuthStates.waiting_for_birth_date)
    
    # Callbacks
    dp.callback_query.register(handle_menu_callback, F.data.startswith("menu_"))
    dp.callback_query.register(handle_equipamento_callback, F.data.startswith("eq_"))
    dp.callback_query.register(handle_checklist_callback, F.data.startswith("checklist_"))
    dp.callback_query.register(handle_checklist_callback, F.data.startswith("link_eq_"))
    
    logger.info("Handlers principais registrados com sucesso")


# ===============================================
# HANDLERS ADICIONAIS PARA bot_main/handlers.py
# ===============================================

async def handle_os_type_callback(callback: CallbackQuery, state: FSMContext):
    """Handler para tipo de OS selecionado"""
    try:
        data = callback.data
        user_id = str(callback.from_user.id)
        
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data == "cancelar_os":
            await callback.message.answer("❌ Criação de OS cancelada.")
            await state.clear()
            return
        
        # Extrair tipo da OS
        tipo_os = data.replace("os_tipo_", "")
        tipo_texto = {
            'corretiva': '🔧 Manutenção Corretiva',
            'preventiva': '🛠️ Manutenção Preventiva',
            'urgente': '🚨 Urgente'
        }.get(tipo_os, tipo_os)
        
        # Salvar tipo no estado
        await state.update_data(tipo_os=tipo_os)
        
        # Criar teclado para cancelar
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Cancelar")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        await callback.message.answer(
            f"📝 **Nova OS - {tipo_texto}**\n\n"
            f"Descreva o problema ou serviço necessário:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await state.set_state(EquipmentStates.waiting_for_os_description)
        
    except Exception as e:
        logger.error(f"Erro no callback de tipo OS: {e}")
        await callback.answer("❌ Erro interno")

async def process_os_description(message: Message, state: FSMContext):
    """Processa descrição da OS"""
    if message.text == "❌ Cancelar":
        await message.answer("❌ Criação de OS cancelada.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    
    try:
        descricao = message.text.strip()
        
        if len(descricao) < 10:
            await message.answer("❌ A descrição deve ter pelo menos 10 caracteres. Digite novamente:")
            return
        
        # Recuperar dados do estado
        data = await state.get_data()
        equipamento_id = data.get('equipamento_id')
        tipo_os = data.get('tipo_os')
        operador_id = data.get('operador_id')
        
        tipo_texto = {
            'corretiva': '🔧 Manutenção Corretiva',
            'preventiva': '🛠️ Manutenção Preventiva',
            'urgente': '🚨 Urgente'
        }.get(tipo_os, tipo_os)
        
        # Aqui você enviaria para a API
        # Por enquanto, apenas simular
        os_numero = f"OS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        await message.answer(
            f"✅ **Ordem de Serviço Criada!**\n\n"
            f"📋 Número: {os_numero}\n"
            f"🚜 Equipamento ID: {equipamento_id}\n"
            f"🔧 Tipo: {tipo_texto}\n"
            f"📝 Descrição: {descricao}\n"
            f"👤 Solicitante: {message.from_user.first_name}\n"
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"✅ OS registrada com sucesso!",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Erro ao processar descrição da OS: {e}")
        await message.answer("❌ Erro ao criar OS. Tente novamente.")

async def handle_checklist_confirm_callback(callback: CallbackQuery, state: FSMContext):
    """Handler para confirmação de checklist"""
    try:
        data = callback.data
        user_id = str(callback.from_user.id)
        
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data == "confirmar_checklist_nao":
            await callback.message.answer("❌ Criação de checklist cancelada.")
            await state.clear()
            return
        
        if data == "confirmar_checklist_sim":
            # Recuperar dados do estado
            state_data = await state.get_data()
            checklist_data = state_data.get('checklist_data')
            
            if not checklist_data:
                await callback.message.answer("❌ Erro: dados do checklist não encontrados.")
                await state.clear()
                return
            
            try:
                # Criar checklist via API
                url = f"{API_BASE_URL}/nr12/checklists/"
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, 
                        json=checklist_data, 
                        timeout=API_TIMEOUT
                    )
                    
                    if response.status_code == 201:
                        checklist_criado = response.json()
                        checklist_id = checklist_criado.get('id', 'N/A')
                        
                        # Criar botões de ação
                        keyboard = [
                            [InlineKeyboardButton(
                                text="📝 Iniciar Preenchimento", 
                                callback_data=f"iniciar_checklist_{checklist_id}"
                            )],
                            [InlineKeyboardButton(
                                text="📊 Ver Detalhes", 
                                callback_data=f"detalhes_checklist_{checklist_id}"
                            )],
                            [InlineKeyboardButton(
                                text="🏠 Menu Principal", 
                                callback_data="menu_principal"
                            )]
                        ]
                        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                        
                        turno_texto = {
                            'MATUTINO': '🌅 Matutino',
                            'VESPERTINO': '☀️ Vespertino',
                            'NOTURNO': '🌙 Noturno'
                        }.get(checklist_data.get('turno'), checklist_data.get('turno'))
                        
                        await callback.message.answer(
                            f"✅ **Checklist Criado com Sucesso!**\n\n"
                            f"📋 ID: {checklist_id}\n"
                            f"🚜 Equipamento ID: {checklist_data.get('equipamento_id')}\n"
                            f"🕐 Turno: {turno_texto}\n"
                            f"📅 Data: {checklist_data.get('data_checklist')}\n"
                            f"👤 Operador: {operador.get('nome')}\n\n"
                            f"O que deseja fazer agora?",
                            reply_markup=markup,
                            parse_mode='HTML'
                        )
                    else:
                        error_msg = response.json().get('error', 'Erro desconhecido')
                        await callback.message.answer(
                            f"❌ **Erro ao criar checklist**\n\n"
                            f"Mensagem: {error_msg}",
                            parse_mode='HTML'
                        )
                        
            except Exception as e:
                logger.error(f"Erro ao criar checklist via API: {e}")
                await callback.message.answer("❌ Erro ao comunicar com o servidor.")
            
            await state.clear()
            
    except Exception as e:
        logger.error(f"Erro na confirmação do checklist: {e}")
        await callback.answer("❌ Erro interno")

async def handle_checklist_action_callback(callback: CallbackQuery):
    """Handler para ações do checklist (iniciar, ver detalhes)"""
    try:
        data = callback.data
        user_id = str(callback.from_user.id)
        
        operador = await obter_operador_sessao(user_id)
        if not operador:
            await callback.answer("❌ Sessão expirada")
            return
        
        await callback.answer()
        
        if data.startswith("iniciar_checklist_"):
            checklist_id = data.split("_")[-1]
            
            # Aqui você implementaria a interface de preenchimento
            # Por enquanto, apenas informar
            await callback.message.answer(
                f"📝 **Iniciando Checklist #{checklist_id}**\n\n"
                f"🚧 Interface de preenchimento em desenvolvimento...\n\n"
                f"Em breve você poderá:\n"
                f"• Responder perguntas do checklist\n"
                f"• Adicionar fotos\n"
                f"• Registrar observações\n"
                f"• Assinar digitalmente",
                parse_mode='HTML'
            )
            
        elif data.startswith("detalhes_checklist_"):
            checklist_id = data.split("_")[-1]
            
            # Buscar detalhes do checklist
            try:
                url = f"{API_BASE_URL}/nr12/checklists/{checklist_id}/"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=API_TIMEOUT)
                    
                    if response.status_code == 200:
                        checklist = response.json()
                        
                        status_emoji = {
                            'PENDENTE': '⏳',
                            'EM_ANDAMENTO': '🔄',
                            'CONCLUIDO': '✅',
                            'CANCELADO': '❌'
                        }.get(checklist.get('status'), '❓')
                        
                        await callback.message.answer(
                            f"📊 **Detalhes do Checklist #{checklist_id}**\n\n"
                            f"🚜 Equipamento: {checklist.get('equipamento_nome', 'N/A')}\n"
                            f"👤 Operador: {checklist.get('operador_nome', 'N/A')}\n"
                            f"🕐 Turno: {checklist.get('turno', 'N/A')}\n"
                            f"📅 Data: {checklist.get('data_checklist', 'N/A')}\n"
                            f"📊 Status: {status_emoji} {checklist.get('status', 'N/A')}\n\n"
                            f"📝 Total de itens: {checklist.get('total_itens', 0)}\n"
                            f"✅ Itens conformes: {checklist.get('itens_conformes', 0)}\n"
                            f"❌ Não conformidades: {checklist.get('nao_conformidades', 0)}",
                            parse_mode='HTML'
                        )
                    else:
                        await callback.message.answer("❌ Erro ao buscar detalhes do checklist")
                        
            except Exception as e:
                logger.error(f"Erro ao buscar detalhes do checklist: {e}")
                await callback.message.answer("❌ Erro ao carregar detalhes")
                
    except Exception as e:
        logger.error(f"Erro no callback de ação do checklist: {e}")
        await callback.answer("❌ Erro interno")

# ===============================================
# FUNÇÃO AUXILIAR: CRIAR MENU EQUIPAMENTO
# ===============================================

def criar_menu_equipamento(equipamento_id: str, tem_checklist_pendente: bool = False):
    """Cria menu de ações para equipamento"""
    keyboard = []
    
    if tem_checklist_pendente:
        keyboard.append([
            InlineKeyboardButton(
                text="▶️ Continuar Checklist", 
                callback_data=f"continuar_checklist_{equipamento_id}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton(text="📋 Novo Checklist NR12", callback_data=f"eq_novo_checklist_{equipamento_id}")],
        [InlineKeyboardButton(text="⛽ Registrar Abastecimento", callback_data=f"eq_abastecimento_{equipamento_id}")],
        [InlineKeyboardButton(text="🔧 Abrir Ordem de Serviço", callback_data=f"eq_os_{equipamento_id}")],
        [InlineKeyboardButton(text="⏱️ Atualizar Horímetro", callback_data=f"eq_horimetro_{equipamento_id}")],
        [InlineKeyboardButton(text="📊 Ver Histórico", callback_data=f"eq_historico_{equipamento_id}")],
        [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_principal")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ===============================================
# ATUALIZAR REGISTRO DE HANDLERS (ADICIONAR)
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers principais"""
    
    # Comandos
    dp.message.register(start_handler, Command("start"))
    
    # Estados de autenticação
    dp.message.register(process_name, AuthStates.waiting_for_name)
    dp.message.register(process_birth_date, AuthStates.waiting_for_birth_date)
    
    # Estados de equipamento
    dp.message.register(process_fuel_quantity, EquipmentStates.waiting_for_fuel_quantity)
    dp.message.register(process_fuel_value, EquipmentStates.waiting_for_fuel_value)
    dp.message.register(process_horimeter_value, EquipmentStates.waiting_for_horimeter)
    dp.message.register(process_os_description, EquipmentStates.waiting_for_os_description)
    
    # Callbacks principais
    dp.callback_query.register(handle_menu_callback, F.data.startswith("menu_"))
    dp.callback_query.register(handle_equipamento_callback, F.data.startswith("eq_"))
    dp.callback_query.register(handle_checklist_callback, F.data.startswith("checklist_"))
    dp.callback_query.register(handle_checklist_callback, F.data.startswith("link_eq_"))
    
    # Callbacks específicos
    dp.callback_query.register(handle_equipamento_callback, F.data.startswith("criar_checklist_"))
    dp.callback_query.register(handle_checklist_action_callback, F.data.startswith("iniciar_checklist_"))
    dp.callback_query.register(handle_checklist_action_callback, F.data.startswith("detalhes_checklist_"))
    dp.callback_query.register(handle_os_type_callback, F.data.startswith("os_tipo_"))
    dp.callback_query.register(handle_checklist_confirm_callback, F.data.startswith("confirmar_checklist_"))
    dp.callback_query.register(handle_equipamento_callback, F.data.startswith("cancelar_"))
    
    logger.info("Handlers principais registrados com sucesso")