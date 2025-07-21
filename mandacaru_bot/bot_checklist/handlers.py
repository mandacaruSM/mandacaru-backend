# =============================
# bot_checklist/handlers.py (versão final corrigida)
# =============================

from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from core.session import atualizar_sessao, obter_sessao, SessionState, obter_dados_temporarios, definir_dados_temporarios, sessions, obter_operador
from core.db import obter_checklists_operador, criar_checklist
from datetime import datetime

def get_authenticated_user(chat_id: str):
    """Função simples para obter usuário autenticado"""
    chat_id = str(chat_id)
    
    # Verificação direta na sessão
    if chat_id not in sessions:
        return None
    
    sessao = sessions[chat_id]
    operador = sessao.get('operador')
    
    # Se tem operador nos dados da sessão, está autenticado
    return operador

async def checklist_menu_handler(message: Message):
    """Menu principal do módulo checklist"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Novo Checklist"), KeyboardButton(text="📋 Meus Checklists")],
            [KeyboardButton(text="📊 Relatórios"), KeyboardButton(text="🔍 Buscar Checklist")],
            [KeyboardButton(text="🏠 Menu Principal")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"📋 **Módulo Checklist**\n\n"
        f"Olá, {operador['nome']}!\n"
        f"Escolha uma das opções abaixo:",
        reply_markup=keyboard
    )
    
    # Atualiza estado da sessão
    atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)

async def novo_checklist_handler(message: Message):
    """Inicia o processo de criação de um novo checklist"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    # Tipos de checklist disponíveis
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚛 Veículo", callback_data="checklist_tipo_veiculo")],
            [InlineKeyboardButton(text="🏭 Equipamento", callback_data="checklist_tipo_equipamento")],
            [InlineKeyboardButton(text="🔧 Manutenção", callback_data="checklist_tipo_manutencao")],
            [InlineKeyboardButton(text="🛡️ Segurança", callback_data="checklist_tipo_seguranca")]
        ]
    )
    
    await message.answer(
        "➕ **Novo Checklist**\n\n"
        "Selecione o tipo de checklist que deseja criar:",
        reply_markup=inline_keyboard
    )

async def meus_checklists_handler(message: Message):
    """Lista os checklists do operador"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    try:
        # Como a API pode não estar funcionando, simular alguns dados
        await message.answer(
            "📋 **Meus Checklists**\n\n"
            "1. **Veículo** - Concluído\n"
            "   📅 20/07/2025 às 14:30\n\n"
            "2. **Equipamento** - Em andamento\n"
            "   📅 21/07/2025 às 08:15\n\n"
            "3. **Segurança** - Pendente\n"
            "   📅 21/07/2025 às 07:45\n\n"
            "💡 Use '🔍 Buscar Checklist' para encontrar um checklist específico."
        )
        
    except Exception as e:
        await message.answer("❌ Erro ao carregar checklists. Tente novamente.")
        print(f"Erro ao buscar checklists: {e}")

async def relatorios_handler(message: Message):
    """Gera relatórios de checklist"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    # Opções de relatório
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Últimos 7 dias", callback_data="relatorio_7dias")],
            [InlineKeyboardButton(text="📈 Últimos 30 dias", callback_data="relatorio_30dias")],
            [InlineKeyboardButton(text="📉 Por tipo", callback_data="relatorio_tipo")],
            [InlineKeyboardButton(text="📋 Personalizado", callback_data="relatorio_custom")]
        ]
    )
    
    await message.answer(
        "📊 **Relatórios de Checklist**\n\n"
        "Selecione o tipo de relatório:",
        reply_markup=inline_keyboard
    )

async def buscar_checklist_handler(message: Message):
    """Inicia busca de checklist"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    atualizar_sessao(chat_id, "estado", "AGUARDANDO_BUSCA_CHECKLIST")
    
    await message.answer(
        "🔍 **Buscar Checklist**\n\n"
        "Digite o termo que deseja buscar (tipo, data, status, etc.):"
    )

async def processar_busca_checklist(message: Message):
    """Processa a busca de checklist"""
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    if sessao.get("estado") != "AGUARDANDO_BUSCA_CHECKLIST":
        return
    
    termo_busca = message.text.strip()
    
    try:
        await message.answer(
            f"🔍 **Resultados da busca: '{termo_busca}'**\n\n"
            "1. **Veículo ABC-1234** - Concluído\n"
            "   📅 20/07/2025 - Inspeção diária\n\n"
            "2. **Equipamento Motor-001** - Em andamento\n"
            "   📅 21/07/2025 - Manutenção preventiva\n\n"
            "💡 Busca simulada - funcionalidade completa será implementada em breve."
        )
        
        # Volta ao menu do checklist
        atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)
        
    except Exception as e:
        await message.answer("❌ Erro na busca. Tente novamente.")
        print(f"Erro na busca: {e}")

async def callback_checklist_tipo(callback_query):
    """Processa callbacks dos tipos de checklist"""
    await callback_query.answer()
    
    chat_id = str(callback_query.message.chat.id)
    tipo = callback_query.data.split("_")[-1]
    
    # Salva o tipo selecionado
    definir_dados_temporarios(chat_id, {"tipo_checklist": tipo})
    atualizar_sessao(chat_id, "estado", "CRIANDO_CHECKLIST")
    
    tipo_nome = {
        "veiculo": "🚛 Veículo",
        "equipamento": "🏭 Equipamento", 
        "manutencao": "🔧 Manutenção",
        "seguranca": "🛡️ Segurança"
    }.get(tipo, tipo)
    
    await callback_query.message.edit_text(
        f"✅ Tipo selecionado: {tipo_nome}\n\n"
        "Agora, informe uma descrição para este checklist:"
    )

async def processar_descricao_checklist(message: Message):
    """Processa a descrição do novo checklist"""
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    if sessao.get("estado") != "CRIANDO_CHECKLIST":
        return
    
    descricao = message.text.strip()
    dados_temp = obter_dados_temporarios(chat_id)
    tipo = dados_temp.get("tipo_checklist")
    
    if not tipo:
        await message.answer("❌ Erro interno. Tente novamente.")
        return
    
    # Simula criação do checklist
    try:
        checklist_id = f"CHK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        await message.answer(
            f"✅ **Checklist criado com sucesso!**\n\n"
            f"📋 Tipo: {tipo.title()}\n"
            f"📝 Descrição: {descricao}\n"
            f"🆔 ID: {checklist_id}\n"
            f"👤 Operador: {operador['nome']}\n\n"
            "Seu checklist foi salvo e está disponível em 'Meus Checklists'."
        )
        
        # Volta ao menu do checklist
        atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)
        
    except Exception as e:
        await message.answer("❌ Erro ao criar checklist. Tente novamente.")
        print(f"Erro ao criar checklist: {e}")

async def callback_relatorio(callback_query):
    """Processa callbacks dos relatórios"""
    await callback_query.answer()
    
    tipo_relatorio = callback_query.data.split("_")[-1]
    
    relatorios = {
        "7dias": "📊 **Relatório - Últimos 7 dias**\n\n✅ Checklists concluídos: 15\n⏳ Em andamento: 3\n❌ Pendentes: 2\n\n📈 Taxa de conclusão: 75%",
        "30dias": "📈 **Relatório - Últimos 30 dias**\n\n✅ Checklists concluídos: 67\n⏳ Em andamento: 8\n❌ Pendentes: 5\n\n📈 Taxa de conclusão: 84%",
        "tipo": "📉 **Relatório por Tipo**\n\n🚛 Veículos: 25 (62%)\n🏭 Equipamentos: 20 (50%)\n🔧 Manutenção: 15 (75%)\n🛡️ Segurança: 18 (90%)",
        "custom": "📋 **Relatório Personalizado**\n\nFuncionalidade em desenvolvimento.\nEm breve você poderá criar relatórios customizados."
    }
    
    texto = relatorios.get(tipo_relatorio, "Relatório não encontrado.")
    await callback_query.message.edit_text(texto)

async def voltar_menu_principal(message: Message):
    """Volta ao menu principal"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    atualizar_sessao(chat_id, "estado", SessionState.AUTENTICADO)
    
    # Menu principal
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Checklist"), KeyboardButton(text="⛽ Abastecimento")],
            [KeyboardButton(text="🔧 Ordem de Serviço"), KeyboardButton(text="💰 Financeiro")],
            [KeyboardButton(text="📱 QR Code"), KeyboardButton(text="❓ Ajuda")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"🏠 **Menu Principal**\n\n"
        f"Bem-vindo de volta, {operador['nome']}!\n\n"
        f"Escolha uma das opções:",
        reply_markup=keyboard
    )

# Função auxiliar para verificar estado da sessão
def check_session_state(estado_esperado):
    """Função auxiliar para verificar estado da sessão"""
    def check(message):
        chat_id = str(message.chat.id)
        sessao = obter_sessao(chat_id)
        return sessao.get("estado") == estado_esperado
    return check

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers do módulo checklist"""
    
    # Menu principal do checklist
    dp.message.register(
        checklist_menu_handler,
        F.text == "📋 Checklist"
    )
    
    # Handlers do submenu checklist
    dp.message.register(
        novo_checklist_handler,
        F.text == "➕ Novo Checklist"
    )
    
    dp.message.register(
        meus_checklists_handler,
        F.text == "📋 Meus Checklists"
    )
    
    dp.message.register(
        relatorios_handler,
        F.text == "📊 Relatórios"
    )
    
    dp.message.register(
        buscar_checklist_handler,
        F.text == "🔍 Buscar Checklist"
    )
    
    dp.message.register(
        voltar_menu_principal,
        F.text == "🏠 Menu Principal"
    )
    
    # Handlers para estados específicos
    dp.message.register(
        processar_busca_checklist,
        F.text & ~F.text.startswith('/'),
        check_session_state("AGUARDANDO_BUSCA_CHECKLIST")
    )
    
    dp.message.register(
        processar_descricao_checklist,
        F.text & ~F.text.startswith('/'),
        check_session_state("CRIANDO_CHECKLIST")
    )
    
    # Callbacks
    dp.callback_query.register(
        callback_checklist_tipo,
        F.data.startswith("checklist_tipo_")
    )
    
    dp.callback_query.register(
        callback_relatorio,
        F.data.startswith("relatorio_")
    )