# =============================
# bot_checklist/handlers.py
# =============================

from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from core.middleware import require_auth, log_user_action
from core.session import atualizar_sessao, obter_sessao, SessionState, obter_dados_temporarios, definir_dados_temporarios
from core.db import obter_checklists_operador, criar_checklist
from datetime import datetime

@require_auth
async def checklist_menu_handler(message: Message, operador=None):
    """Menu principal do módulo checklist"""
    await log_user_action(message, "CHECKLIST_MENU_ACCESSED")
    
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
    chat_id = str(message.chat.id)
    atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)

@require_auth
async def novo_checklist_handler(message: Message, operador=None):
    """Inicia o processo de criação de um novo checklist"""
    await log_user_action(message, "NOVO_CHECKLIST_INICIADO")
    
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

@require_auth
async def meus_checklists_handler(message: Message, operador=None):
    """Lista os checklists do operador"""
    await log_user_action(message, "MEUS_CHECKLISTS_VISUALIZADO")
    
    try:
        checklists = await obter_checklists_operador(operador['id'])
        
        if not checklists:
            await message.answer(
                "📋 Você ainda não possui checklists.\n\n"
                "Use a opção '➕ Novo Checklist' para criar seu primeiro checklist."
            )
            return
        
        # Monta a lista de checklists
        texto = "📋 **Meus Checklists**\n\n"
        
        for i, checklist in enumerate(checklists[:10], 1):  # Limita a 10 para não sobrecarregar
            data_criacao = checklist.get('data_criacao', 'N/A')
            tipo = checklist.get('tipo', 'N/A')
            status = checklist.get('status', 'N/A')
            
            texto += f"{i}. **{tipo}** - {status}\n"
            texto += f"   📅 {data_criacao}\n\n"
        
        if len(checklists) > 10:
            texto += f"... e mais {len(checklists) - 10} checklists.\n\n"
        
        texto += "Use '🔍 Buscar Checklist' para encontrar um checklist específico."
        
        await message.answer(texto)
        
    except Exception as e:
        await message.answer("❌ Erro ao carregar checklists. Tente novamente.")
        print(f"Erro ao buscar checklists: {e}")

@require_auth
async def relatorios_handler(message: Message, operador=None):
    """Gera relatórios de checklist"""
    await log_user_action(message, "RELATORIOS_CHECKLIST_ACESSADO")
    
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

@require_auth
async def buscar_checklist_handler(message: Message, operador=None):
    """Inicia busca de checklist"""
    await log_user_action(message, "BUSCA_CHECKLIST_INICIADA")
    
    chat_id = str(message.chat.id)
    atualizar_sessao(chat_id, "estado", "AGUARDANDO_BUSCA_CHECKLIST")
    
    await message.answer(
        "🔍 **Buscar Checklist**\n\n"
        "Digite o termo que deseja buscar (tipo, data, status, etc.):"
    )

@require_auth
async def processar_busca_checklist(message: Message, operador=None):
    """Processa a busca de checklist"""
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    
    if sessao.get("estado") != "AGUARDANDO_BUSCA_CHECKLIST":
        return
    
    termo_busca = message.text.strip()
    
    try:
        # Aqui você implementaria a busca na API
        # Por enquanto, simulamos
        await message.answer(
            f"🔍 Buscando por: '{termo_busca}'\n\n"
            "Esta funcionalidade será implementada em breve."
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

@require_auth
async def processar_descricao_checklist(message: Message, operador=None):
    """Processa a descrição do novo checklist"""
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    
    if sessao.get("estado") != "CRIANDO_CHECKLIST":
        return
    
    descricao = message.text.strip()
    dados_temp = obter_dados_temporarios(chat_id)
    tipo = dados_temp.get("tipo_checklist")
    
    if not tipo:
        await message.answer("❌ Erro interno. Tente novamente.")
        return
    
    # Cria o checklist
    try:
        dados_checklist = {
            "tipo": tipo,
            "descricao": descricao,
            "operador_id": operador['id'],
            "status": "em_andamento",
            "data_criacao": datetime.now().isoformat()
        }
        
        resultado = await criar_checklist(dados_checklist)
        
        if resultado:
            await message.answer(
                f"✅ **Checklist criado com sucesso!**\n\n"
                f"📋 Tipo: {tipo.title()}\n"
                f"📝 Descrição: {descricao}\n"
                f"🆔 ID: {resultado.get('id', 'N/A')}\n\n"
                "Seu checklist foi salvo e está disponível em 'Meus Checklists'."
            )
            
            await log_user_action(message, "CHECKLIST_CRIADO", f"Tipo: {tipo}, ID: {resultado.get('id')}")
        else:
            await message.answer("❌ Erro ao criar checklist. Tente novamente.")
        
        # Volta ao menu do checklist
        atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)
        
    except Exception as e:
        await message.answer("❌ Erro ao criar checklist. Tente novamente.")
        print(f"Erro ao criar checklist: {e}")

async def callback_relatorio(callback_query):
    """Processa callbacks dos relatórios"""
    await callback_query.answer()
    
    tipo_relatorio = callback_query.data.split("_")[-1]
    
    if tipo_relatorio == "7dias":
        await callback_query.message.edit_text(
            "📊 **Relatório - Últimos 7 dias**\n\n"
            "Gerando relatório...\n\n"
            "Esta funcionalidade será implementada em breve."
        )
    elif tipo_relatorio == "30dias":
        await callback_query.message.edit_text(
            "📈 **Relatório - Últimos 30 dias**\n\n"
            "Gerando relatório...\n\n"
            "Esta funcionalidade será implementada em breve."
        )
    elif tipo_relatorio == "tipo":
        await callback_query.message.edit_text(
            "📉 **Relatório por Tipo**\n\n"
            "Gerando relatório...\n\n"
            "Esta funcionalidade será implementada em breve."
        )
    elif tipo_relatorio == "custom":
        await callback_query.message.edit_text(
            "📋 **Relatório Personalizado**\n\n"
            "Esta funcionalidade será implementada em breve."
        )

@require_auth
async def voltar_menu_principal(message: Message, operador=None):
    """Volta ao menu principal"""
    chat_id = str(message.chat.id)
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
        F.text & ~F.text.startswith('/') &
        lambda message: obter_sessao(str(message.chat.id)).get("estado") == "AGUARDANDO_BUSCA_CHECKLIST"
    )
    
    dp.message.register(
        processar_descricao_checklist,
        F.text & ~F.text.startswith('/') &
        lambda message: obter_sessao(str(message.chat.id)).get("estado") == "CRIANDO_CHECKLIST"
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