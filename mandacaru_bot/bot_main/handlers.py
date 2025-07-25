# =============================
# bot_main/handlers.py (sintaxe corrigida)
# =============================

from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from core.session import *
from core.db import buscar_operador_por_nome, validar_data_nascimento, registrar_chat_id

async def start_handler(message: Message):
    chat_id = str(message.chat.id)
    iniciar_sessao(chat_id)
    await message.answer("👋 Bem-vindo ao Bot Mandacaru!\n\n👤 Informe seu nome completo para buscar seu cadastro no sistema:")

async def nome_handler(message: Message):
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    
    # Verifica se está no estado correto
    if sessao.get("estado") != "AGUARDANDO_NOME":
        return
    
    nome = message.text.strip()
    
    # Validação básica do nome
    if len(nome) < 3:
        await message.answer("❌ Nome muito curto. Digite seu nome completo:")
        return
    
    try:
        operadores = await buscar_operador_por_nome(nome)
        
        if not operadores:
            await message.answer("❌ Nenhum operador encontrado com esse nome.\n\nTente novamente ou verifique se digitou corretamente:")
            return

        operador = operadores[0]  # pega o primeiro resultado encontrado
        atualizar_sessao(chat_id, "estado", "AGUARDANDO_DATA")
        atualizar_sessao(chat_id, "operador", operador)
        
        await message.answer(
            f"👤 Operador encontrado: {operador['nome']}\n\n"
            f"🔐 Para confirmar sua identidade, digite sua data de nascimento no formato DD/MM/AAAA:"
        )
        
    except Exception as e:
        await message.answer("❌ Erro ao buscar operador. Tente novamente em alguns instantes.")
        print(f"Erro ao buscar operador: {e}")

async def data_nascimento_handler(message: Message):
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    
    if sessao.get("estado") != "AGUARDANDO_DATA":
        return
    
    data_digitada = message.text.strip()
    operador = sessao.get("operador")
    
    if not operador:
        await message.answer("❌ Erro interno. Envie /start para tentar novamente.")
        limpar_sessao(chat_id)
        return

    # Validação do formato da data
    try:
        dia, mes, ano = map(int, data_digitada.split("/"))
        if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= ano <= 2025):
            raise ValueError("Data fora do intervalo válido")
        data_formatada = f"{ano:04d}-{mes:02d}-{dia:02d}"
    except:
        await message.answer("❌ Data inválida. Use o formato DD/MM/AAAA (exemplo: 15/03/1990):")
        return

    try:
        if await validar_data_nascimento(operador["id"], data_digitada):
            await registrar_chat_id(operador["id"], chat_id)
            
            # IMPORTANTE: Atualizar sessão para autenticado E manter operador
            atualizar_sessao(chat_id, "estado", SessionState.AUTENTICADO)
            atualizar_sessao(chat_id, "operador", operador)
            
            # Menu principal
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📋 Checklist"), KeyboardButton(text="⛽ Abastecimento")],
                    [KeyboardButton(text="🔧 Ordem de Serviço"), KeyboardButton(text="💰 Financeiro")],
                    [KeyboardButton(text="📱 QR Code"), KeyboardButton(text="❓ Ajuda")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )
            
            await message.answer(
                f"✅ Acesso liberado!\n\n"
                f"Olá, {operador['nome']}! 👋\n\n"
                f"Escolha uma das opções do menu abaixo:",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                "❌ Data de nascimento incorreta.\n\n"
                "Acesso negado. Envie /start para tentar novamente."
            )
            limpar_sessao(chat_id)
            
    except Exception as e:
        await message.answer("❌ Erro ao validar dados. Tente novamente.")
        print(f"Erro na validação: {e}")

async def menu_handler(message: Message):
    """Handler para as opções do menu principal"""
    text = message.text
    chat_id = str(message.chat.id)
    
    # Verificar se está autenticado
    if not esta_autenticado(chat_id):
        await message.answer("🔒 Você precisa estar autenticado. Digite /start para fazer login.")
        return
    
    if text == "❓ Ajuda":
        await message.answer(
            "❓ **Ajuda - Bot Mandacaru**\n\n"
            "Este bot permite acesso aos módulos:\n"
            "• 📋 Checklist - Verificações diárias\n"
            "• ⛽ Abastecimento - Controle de combustível\n"
            "• 🔧 Ordem de Serviço - Solicitações de manutenção\n"
            "• 💰 Financeiro - Consultas financeiras\n"
            "• 📱 QR Code - Geração de códigos\n\n"
            "Para suporte, entre em contato com a equipe técnica."
        )
    elif text in ["⛽ Abastecimento", "🔧 Ordem de Serviço", "💰 Financeiro", "📱 QR Code"]:
        await message.answer(f"{text} - Módulo em desenvolvimento...")

async def debug_session_handler(message: Message):
    """Handler para debug da sessão (temporário)"""
    chat_id = str(message.chat.id)
    sessao = obter_sessao(chat_id)
    operador = obter_operador(chat_id)
    
    from core.session import is_session_expired, get_session_time_remaining
    
    debug_info = f"""
🔍 **Debug da Sessão**

**Chat ID:** {chat_id}
**Estado:** {sessao.get('estado', 'Não definido')}
**Autenticado:** {'✅ Sim' if esta_autenticado(chat_id) else '❌ Não'}
**Sessão expirada:** {'✅ Sim' if is_session_expired(chat_id) else '❌ Não'}
**Operador:** {operador.get('nome') if operador else 'Nenhum'}
**Tempo restante:** {get_session_time_remaining(chat_id)} min
**Dados da sessão:** {len(sessao)} items
**Último acesso:** {sessao.get('ultimo_acesso', 'N/A')}
    """
    await message.answer(debug_info)

async def tempo_sessao_handler(message: Message):
    """Mostra o tempo restante da sessão"""
    chat_id = str(message.chat.id)
    
    if not esta_autenticado(chat_id):
        await message.answer("❌ Você não está autenticado. Digite /start para fazer login.")
        return
    
    from core.session import get_session_time_remaining
    tempo_restante = get_session_time_remaining(chat_id)
    
    if tempo_restante > 0:
        await message.answer(
            f"⏰ **Tempo de Sessão**\n\n"
            f"Tempo restante: **{tempo_restante} minutos**\n\n"
            f"💡 Sua sessão expira automaticamente após 10 minutos de inatividade.\n"
            f"Envie qualquer mensagem para manter a sessão ativa."
        )
    else:
        await message.answer("⏱️ Sua sessão expirou. Digite /start para fazer login novamente.")
        limpar_sessao(chat_id)

# Função para verificar estado da sessão
def check_session_state(estado_esperado):
    """Função auxiliar para verificar estado da sessão"""
    def check(message):
        chat_id = str(message.chat.id)
        sessao = obter_sessao(chat_id)
        return sessao.get("estado") == estado_esperado
    return check

def register_handlers(dp: Dispatcher):
    # Comando /start
    dp.message.register(start_handler, Command("start"))
    
    # Comandos informativos
    dp.message.register(debug_session_handler, Command("debug"))
    dp.message.register(tempo_sessao_handler, Command("tempo"))
    
    # Handler para nome (apenas quando está aguardando nome)
    dp.message.register(
        nome_handler, 
        F.text & ~F.text.startswith('/'),
        check_session_state("AGUARDANDO_NOME")
    )
    
    # Handler para data (apenas quando está aguardando data)
    dp.message.register(
        data_nascimento_handler,
        F.text & ~F.text.startswith('/'),
        check_session_state("AGUARDANDO_DATA")
    )
    
    # Handler para menus principais (quando autenticado)
    dp.message.register(
        menu_handler,
        F.text.in_([
            "⛽ Abastecimento", "🔧 Ordem de Serviço", 
            "💰 Financeiro", "📱 QR Code", "❓ Ajuda"
        ])
    )