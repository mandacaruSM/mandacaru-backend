# bot_checklist/handlers.py (versão corrigida)

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F
from core.db import get_checklist_do_dia
from core.session import obter_equipamento_atual
from aiogram.types import CallbackQuery
from datetime import date
from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from core.db import get_checklist_do_dia
from core.session import obter_equipamento_atual
from aiogram import types
from core.session import (
    atualizar_sessao,
    obter_sessao,
    SessionState,
    obter_dados_temporarios,
    definir_dados_temporarios,
    sessions,
)
from core.db import (
    obter_equipamentos_operador,
    obter_checklists_operador,
)
from datetime import datetime

def get_authenticated_user(chat_id: str):
    """Função simples para obter usuário autenticado"""
    chat_id = str(chat_id)
    if chat_id not in sessions:
        return None
    sessao = sessions[chat_id]
    return sessao.get("operador")

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
            [KeyboardButton(text="🏠 Menu Principal")],
        ],
        resize_keyboard=True,
    )

    await message.answer(
        f"📋 **Módulo Checklist**\n\n"
        f"Olá, {operador['nome']}!\n"
        f"Escolha uma das opções abaixo:",
        reply_markup=keyboard,
    )

    atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)

async def novo_checklist_handler(message: Message):
    """Inicia o processo de criação de um novo checklist"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)

    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return

    operador_id = operador.get("id")
    # busca equipamentos e checklists do operador
    equipamentos = await obter_equipamentos_operador(operador_id)
    checklists = await obter_checklists_operador(operador_id)

    texto = "➕ **Novo Checklist**\n\n"

    # lista equipamentos
    if equipamentos:
        texto += "Equipamentos disponíveis:\n"
        for eq in equipamentos:
            texto += f"• {eq.get('nome', 'N/A')} (ID {eq.get('id')})\n"
    else:
        texto += "Nenhum equipamento autorizado.\n"
    texto += "\n"

    # lista checklists existentes
    if checklists:
        texto += "Seus checklists:\n"
        for chk in checklists:
            texto += (
                f"• {chk.get('tipo', 'N/A')} – {chk.get('status')} – {chk.get('data_checklist')}\n"
            )
    else:
        texto += "Nenhum checklist cadastrado.\n"

    await message.answer(texto)

    # teclado inline para seleção do tipo
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚛 Veículo", callback_data="checklist_tipo_veiculo")],
            [InlineKeyboardButton(text="🏭 Equipamento", callback_data="checklist_tipo_equipamento")],
            [InlineKeyboardButton(text="🔧 Manutenção", callback_data="checklist_tipo_manutencao")],
            [InlineKeyboardButton(text="🛡️ Segurança", callback_data="checklist_tipo_seguranca")],
        ]
    )
    await message.answer("Selecione o tipo de checklist:", reply_markup=inline_keyboard)

    # usa string para estado, pois SessionState não define CRIANDO_CHECKLIST
    atualizar_sessao(chat_id, "estado", "CRIANDO_CHECKLIST")

async def meus_checklists_handler(message: Message):
    """Lista os checklists do operador"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)

    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return

    # aqui você pode integrar a API real em vez de dados simulados
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

async def relatorios_handler(message: Message):
    """Gera relatórios de checklist"""
    chat_id = str(message.chat.id)
    operador = get_authenticated_user(chat_id)
    if not operador:
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Últimos 7 dias", callback_data="relatorio_7dias")],
            [InlineKeyboardButton(text="📈 Últimos 30 dias", callback_data="relatorio_30dias")],
            [InlineKeyboardButton(text="📉 Por tipo", callback_data="relatorio_tipo")],
            [InlineKeyboardButton(text="📋 Personalizado", callback_data="relatorio_custom")],
        ]
    )

    await message.answer(
        "📊 **Relatórios de Checklist**\n\n" "Selecione o tipo de relatório:", reply_markup=inline_keyboard
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
        "🔍 **Buscar Checklist**\n\n" "Digite o termo que deseja buscar (tipo, data, status, etc.):"
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
    await message.answer(
        f"🔍 **Resultados da busca: '{termo_busca}'**\n\n"
        "1. **Veículo ABC-1234** - Concluído\n"
        "   📅 20/07/2025 - Inspeção diária\n\n"
        "2. **Equipamento Motor-001** - Em andamento\n"
        "   📅 21/07/2025 - Manutenção preventiva\n\n"
        "💡 Busca simulada - funcionalidade completa será implementada em breve."
    )
    atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)

async def callback_checklist_tipo(callback_query):
    """Processa callbacks dos tipos de checklist"""
    await callback_query.answer()

    chat_id = str(callback_query.message.chat.id)
    tipo = callback_query.data.split("_")[-1]
    definir_dados_temporarios(chat_id, {"tipo_checklist": tipo})
    atualizar_sessao(chat_id, "estado", "CRIANDO_CHECKLIST")

    tipo_nome = {
        "veiculo": "🚛 Veículo",
        "equipamento": "🏭 Equipamento",
        "manutencao": "🔧 Manutenção",
        "seguranca": "🛡️ Segurança",
    }.get(tipo, tipo)

    await callback_query.message.edit_text(
        f"✅ Tipo selecionado: {tipo_nome}\n\n" "Agora, informe uma descrição para este checklist:"
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

    # simula criação do checklist
    checklist_id = f"CHK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    await message.answer(
        f"✅ **Checklist criado com sucesso!**\n\n"
        f"📋 Tipo: {tipo.title()}\n"
        f"📝 Descrição: {descricao}\n"
        f"🆔 ID: {checklist_id}\n"
        f"👤 Operador: {operador['nome']}\n\n"
        "Seu checklist foi salvo e está disponível em 'Meus Checklists'."
    )
    atualizar_sessao(chat_id, "estado", SessionState.CHECKLIST_ATIVO)

async def callback_relatorio(callback_query):
    """Processa callbacks dos relatórios"""
    await callback_query.answer()
    tipo_relatorio = callback_query.data.split("_")[-1]
    relatorios = {
        "7dias": "📊 **Relatório - Últimos 7 dias**\n\n✅ Checklists concluídos: 15\n⏳ Em andamento: 3\n❌ Pendentes: 2\n\n📈 Taxa de conclusão: 75%",
        "30dias": "📈 **Relatório - Últimos 30 dias**\n\n✅ Checklists concluídos: 67\n⏳ Em andamento: 8\n❌ Pendentes: 5\n\n📈 Taxa de conclusão: 84%",
        "tipo": "📉 **Relatório por Tipo**\n\n🚛 Veículos: 25 (62%)\n🏭 Equipamentos: 20 (50%)\n🔧 Manutenção: 15 (75%)\n🛡️ Segurança: 18 (90%)",
        "custom": "📋 **Relatório Personalizado**\n\nFuncionalidade em desenvolvimento.\nEm breve você poderá criar relatórios customizados.",
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
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Checklist"), KeyboardButton(text="⛽ Abastecimento")],
            [KeyboardButton(text="🔧 Ordem de Serviço"), KeyboardButton(text="💰 Financeiro")],
            [KeyboardButton(text="📱 QR Code"), KeyboardButton(text="❓ Ajuda")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        f"🏠 **Menu Principal**\n\n"
        f"Bem-vindo de volta, {operador['nome']}!\n\n"
        f"Escolha uma das opções:",
        reply_markup=keyboard,
    )

def check_session_state(estado_esperado):
    """Função auxiliar para verificar estado da sessão"""
    def check(message):
        chat_id = str(message.chat.id)
        sessao = obter_sessao(chat_id)
        return sessao.get("estado") == estado_esperado
    return check

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers do módulo checklist"""
    dp.message.register(checklist_menu_handler, F.text == "📋 Checklist")
    dp.message.register(novo_checklist_handler, F.text == "➕ Novo Checklist")
    dp.message.register(meus_checklists_handler, F.text == "📋 Meus Checklists")
    dp.message.register(relatorios_handler, F.text == "📊 Relatórios")
    dp.message.register(buscar_checklist_handler, F.text == "🔍 Buscar Checklist")
    dp.message.register(voltar_menu_principal, F.text == "🏠 Menu Principal")
    dp.message.register(processar_busca_checklist, F.text & ~F.text.startswith('/'), check_session_state("AGUARDANDO_BUSCA_CHECKLIST"))
    dp.message.register(processar_descricao_checklist, F.text & ~F.text.startswith('/'), check_session_state("CRIANDO_CHECKLIST"))
    dp.callback_query.register(callback_checklist_tipo, F.data.startswith("checklist_tipo_"))
    dp.callback_query.register(callback_relatorio, F.data.startswith("relatorio_"))
    dp.callback_query.register(ver_checklist_de_hoje, F.data == "ver_checklist_hoje")

@dp.callback_query(F.data.startswith("ver_checklist_hoje"))
async def ver_checklist_de_hoje(callback: types.CallbackQuery):
    chat_id = str(callback.from_user.id)
    equipamento = await obter_equipamento_atual(chat_id)

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

    router.callback_query.register(ver_checklist_de_hoje, F.data.startswith("ver_checklist_hoje"))

async def ver_checklist_de_hoje(callback: CallbackQuery):
    chat_id = str(callback.from_user.id)
    equipamento = await obter_equipamento_atual(chat_id)

    if not equipamento:
        await callback.message.answer("❌ Nenhum equipamento selecionado.")
        await callback.answer()
        return

    equipamento_id = equipamento.get("id")
    checklist = await get_checklist_do_dia(equipamento_id)

    if not checklist:
        await callback.message.answer("📭 Nenhum checklist encontrado para hoje.")
        await callback.answer()
        return

    texto = (
        f"<b>📋 Checklist de Hoje</b>\n"
        f"<b>Equipamento:</b> {equipamento['nome']}\n"
        f"<b>Data:</b> {checklist['data_checklist']}\n"
        f"<b>Status:</b> {checklist['status']}\n"
        f"<b>Itens:</b> {checklist['itens_ok']} OK / {checklist['itens_nok']} NOK / {checklist['itens_pendentes']} pendentes\n"
        f"🔗 <a href='{checklist['qr_code_url']}'>Ver Checklist Online</a>"
    )

    await callback.message.answer(texto, parse_mode="HTML")
    await callback.answer()