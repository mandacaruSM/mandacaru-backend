# ===============================================
# ARQUIVO: mandacaru_bot/bot_qr/handlers.py
# Handlers para QR Codes
# ===============================================

import logging
import re
import uuid as uuid_lib
from typing import Dict, Any, Optional
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command

from core.session import (
    obter_operador_sessao, verificar_autenticacao,
    definir_equipamento_atual, definir_dados_temporarios
)
from core.db import buscar_equipamento_por_uuid, listar_equipamentos
from core.templates import MessageTemplates

logger = logging.getLogger(__name__)

# ===============================================
# PROCESSAMENTO DE QR CODES
# ===============================================

async def processar_qr_code_start(message: Message, comando_completo: str):
    """Processa comando /start com QR code"""
    chat_id = str(message.chat.id)
    
    try:
        # Extrair parâmetro do comando
        partes = comando_completo.split(' ', 1)
        if len(partes) < 2:
            return False
        
        parametro = partes[1].strip()
        logger.info(f"📱 Processando parâmetro QR: {parametro}")
        
        # Verificar se é QR de equipamento: eq_uuid
        if parametro.startswith('eq_'):
            uuid_str = parametro.replace('eq_', '')
            await processar_qr_equipamento(message, uuid_str)
            return True
        
        # Verificar se é UUID direto (36 caracteres)
        if len(parametro) == 36 and '-' in parametro:
            try:
                uuid_obj = uuid_lib.UUID(parametro)
                await processar_qr_equipamento(message, str(uuid_obj))
                return True
            except ValueError:
                pass
        
        # Outros tipos de QR podem ser adicionados aqui
        logger.warning(f"⚠️ Tipo de QR não reconhecido: {parametro}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar QR code: {e}")
        await message.answer(MessageTemplates.error_generic())
        return False

async def processar_qr_equipamento(message: Message, uuid_str: str):
    """Processa QR code de equipamento"""
    chat_id = str(message.chat.id)
    
    try:
        logger.info(f"🔍 Buscando equipamento por UUID: {uuid_str}")
        
        # Verificar se usuário está autenticado
        if not verificar_autenticacao(chat_id):
            await message.answer(
                "🔐 **Equipamento Detectado!**\n\n"
                f"UUID: `{uuid_str[:8]}...`\n\n"
                "Para acessar este equipamento, você precisa fazer login primeiro.\n\n"
                "Digite seu nome completo para continuar:"
            )
            # Salvar UUID para depois da autenticação
            definir_dados_temporarios(chat_id, 'equipamento_uuid_pendente', uuid_str)
            return
        
        # Buscar equipamento
        equipamento = await buscar_equipamento_por_uuid(uuid_str)
        
        if not equipamento:
            await message.answer(
                "❌ **Equipamento Não Encontrado**\n\n"
                f"UUID: `{uuid_str[:8]}...`\n\n"
                "Este QR Code pode estar:\n"
                "• Desatualizado\n"
                "• De outro sistema\n"
                "• Corrompido\n\n"
                "💡 Contate o responsável para verificar.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]
                ])
            )
            return
        
        # Verificar se operador tem acesso a este equipamento
        operador = obter_operador_sessao(chat_id)
        if not operador:
            logger.error("❌ Operador não encontrado na sessão")
            await message.answer(MessageTemplates.error_generic())
            return

        equipamentos_permitidos = await listar_equipamentos(operador_id=operador["id"])
        if not any(eq["id"] == equipamento["id"] for eq in equipamentos_permitidos):
            logger.warning(
                f"🚫 Operador {operador['id']} sem permissão para equipamento {equipamento['id']}"
            )
            await message.answer(
                "❌ Acesso negado. Você não tem permissão para este equipamento.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]]
                ),
            )
            return

        
        # Salvar equipamento na sessão
        definir_equipamento_atual(chat_id, equipamento)
        
        # Mostrar informações do equipamento
        await mostrar_menu_equipamento_qr(message, equipamento)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar equipamento: {e}")
        await message.answer(MessageTemplates.error_generic())

async def mostrar_menu_equipamento_qr(message: Message, equipamento: Dict[str, Any]):
    """Mostra menu específico para equipamento acessado via QR"""
    
    try:
        nome = equipamento.get('nome', 'Equipamento')
        marca = equipamento.get('marca', 'N/A')
        modelo = equipamento.get('modelo', 'N/A')
        status = equipamento.get('status_operacional', 'N/A')
        horimetro = equipamento.get('horimetro_atual', 0)
        
        # Emoji baseado no status
        status_emoji = "🟢" if status == "Operacional" else "🟡" if status == "Manutenção" else "🔴"
        
        texto = f"📱 **QR Code Escaneado!**\n\n"
        texto += f"🚜 **{nome}**\n"
        texto += f"🏭 **Marca:** {marca}\n"
        texto += f"📦 **Modelo:** {modelo}\n"
        texto += f"{status_emoji} **Status:** {status}\n"
        texto += f"⏱️ **Horímetro:** {horimetro:,.1f}h\n\n"
        texto += "Selecione a ação desejada:"
        
        # Criar keyboard com ações específicas
        keyboard = []
        
        # Ação principal: Checklist
        keyboard.append([
            InlineKeyboardButton(
                text="📋 Novo Checklist", 
                callback_data=f"qr_create_checklist_{equipamento['id']}"
            )
        ])
        
        # Verificar se há checklist pendente
        keyboard.append([
            InlineKeyboardButton(
                text="📊 Ver Checklists", 
                callback_data=f"qr_list_checklists_{equipamento['id']}"
            )
        ])
        
        # Ações secundárias
        keyboard.append([
            InlineKeyboardButton(text="⛽ Abastecimento", callback_data=f"qr_fuel_{equipamento['id']}"),
            InlineKeyboardButton(text="🔧 Manutenção", callback_data=f"qr_maintenance_{equipamento['id']}")
        ])
        
        # Informações
        keyboard.append([
            InlineKeyboardButton(text="📄 Detalhes", callback_data=f"qr_details_{equipamento['id']}"),
            InlineKeyboardButton(text="📈 Relatório", callback_data=f"qr_report_{equipamento['id']}")
        ])
        
        # Navegação
        keyboard.append([
            InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")
        ])
        
        await message.answer(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar menu do equipamento: {e}")
        await message.answer(MessageTemplates.error_generic())

# ===============================================
# HANDLERS DE CALLBACK PARA QR
# ===============================================

def require_auth(handler):
    """Decorator que exige autenticação (reutilizado)"""
    async def wrapper(obj, *args, **kwargs):
        # Determinar chat_id baseado no tipo de objeto
        if hasattr(obj, 'chat'):
            chat_id = str(obj.chat.id)
        elif hasattr(obj, 'message') and hasattr(obj.message, 'chat'):
            chat_id = str(obj.message.chat.id)
        else:
            logger.error("❌ Não foi possível determinar chat_id")
            return
        
        # Verificar autenticação
        if not verificar_autenticacao(chat_id):
            await obj.answer(MessageTemplates.unauthorized_access())
            return
        
        # Adicionar operador aos argumentos
        operador = obter_operador_sessao(chat_id)
        kwargs['operador'] = operador
        
        return await handler(obj, *args, **kwargs)
    
    return wrapper

@require_auth
async def qr_create_checklist_handler(callback: CallbackQuery, operador=None):
    """Handler para criar checklist via QR"""
    
    try:
        await callback.answer("⏳ Criando checklist...")
        
        # Extrair ID do equipamento
        equipamento_id = int(callback.data.split('_')[-1])
        
        # Redirecionar para handler de criação normal
        from bot_checklist.handlers import criar_checklist_equipamento
        
        resultado = await criar_checklist_equipamento(
            equipamento_id,
            operador['codigo']
        )
        
        if resultado and resultado.get('success'):
            checklist = resultado.get('checklist', {})
            checklist_id = checklist.get('id')
            
            texto = "✅ **Checklist Criado via QR!**\n\n"
            texto += f"**ID:** {checklist_id}\n"
            texto += f"**Turno:** {checklist.get('turno', 'MANHA')}\n"
            texto += f"**Itens:** {checklist.get('total_itens', '?')}\n\n"
            texto += "Deseja iniciar a verificação agora?"
            
            keyboard = [
                [InlineKeyboardButton(text="▶️ Iniciar Agora", callback_data=f"start_checklist_{checklist_id}")],
                [InlineKeyboardButton(text="📋 Listar Todos", callback_data="list_checklists")],
                [InlineKeyboardButton(text="🔄 Escanear Outro QR", callback_data="scan_new_qr")]
            ]
            
            await callback.message.edit_text(
                texto,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        else:
            erro = resultado.get('error', 'Erro desconhecido') if resultado else 'Falha na comunicação'
            
            await callback.message.edit_text(
                f"❌ **Erro ao Criar Checklist**\n\n{erro}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Tentar Novamente", callback_data=f"qr_create_checklist_{equipamento_id}")],
                    [InlineKeyboardButton(text="🔄 Escanear Outro QR", callback_data="scan_new_qr")]
                ])
            )
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar checklist via QR: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth  
async def qr_details_handler(callback: CallbackQuery, operador=None):
    """Mostra detalhes completos do equipamento"""
    
    try:
        await callback.answer()
        
        # Extrair ID do equipamento
        equipamento_id = int(callback.data.split('_')[-1])
        
        # Buscar equipamento
        from core.db import buscar_equipamento_por_id
        equipamento = await buscar_equipamento_por_id(equipamento_id)
        
        if not equipamento:
            await callback.message.edit_text("❌ Equipamento não encontrado")
            return
        
        # Montar informações detalhadas
        nome = equipamento.get('nome', 'N/A')
        marca = equipamento.get('marca', 'N/A')
        modelo = equipamento.get('modelo', 'N/A')
        n_serie = equipamento.get('n_serie', 'N/A')
        ano_fabricacao = equipamento.get('ano_fabricacao', 'N/A')
        horimetro = equipamento.get('horimetro_atual', 0)
        status = equipamento.get('status_operacional', 'N/A')
        
        texto = f"📋 **Detalhes do Equipamento**\n\n"
        texto += f"🚜 **Nome:** {nome}\n"
        texto += f"🏭 **Marca:** {marca}\n"
        texto += f"📦 **Modelo:** {modelo}\n"
        texto += f"🔢 **Nº Série:** {n_serie}\n"
        texto += f"📅 **Ano:** {ano_fabricacao}\n"
        texto += f"⏱️ **Horímetro:** {horimetro:,.1f}h\n"
        texto += f"📊 **Status:** {status}\n"
        
        # Adicionar informações do cliente se disponível
        if equipamento.get('cliente_nome'):
            texto += f"🏢 **Cliente:** {equipamento['cliente_nome']}\n"
        
        keyboard = [
            [
                InlineKeyboardButton(text="📋 Criar Checklist", callback_data=f"qr_create_checklist_{equipamento_id}"),
                InlineKeyboardButton(text="📊 Ver Histórico", callback_data=f"qr_list_checklists_{equipamento_id}")
            ],
            [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"qr_menu_{equipamento_id}")]
        ]
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar detalhes: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

async def scan_new_qr_handler(callback: CallbackQuery):
    """Instrui como escanear novo QR"""
    
    await callback.answer()
    
    texto = "📱 **Como Escanear QR Code**\n\n"
    texto += "Para escanear um novo QR Code:\n\n"
    texto += "1️⃣ **Abra a câmera** do seu celular\n"
    texto += "2️⃣ **Aponte para o QR Code** do equipamento\n"
    texto += "3️⃣ **Toque no link** que aparecer\n"
    texto += "4️⃣ **Clique em 'Iniciar'** quando o Telegram abrir\n\n"
    texto += "🔍 O QR Code geralmente está na plaqueta do equipamento.\n\n"
    texto += "💡 **Dica:** Certifique-se de que há luz suficiente para a câmera ler o código."
    
    keyboard = [
        [InlineKeyboardButton(text="📋 Meus Checklists", callback_data="list_checklists")],
        [InlineKeyboardButton(text="🏠 Menu Principal", callback_data="menu_refresh")]
    ]
    
    await callback.message.edit_text(
        texto,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# ===============================================
# REGISTRAR HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra handlers de QR code no dispatcher"""
    
    # Callbacks específicos de QR
    dp.callback_query.register(qr_create_checklist_handler, F.data.startswith("qr_create_checklist_"))
    dp.callback_query.register(qr_details_handler, F.data.startswith("qr_details_"))
    dp.callback_query.register(scan_new_qr_handler, F.data == "scan_new_qr")
    
    # Callback para instruções de scan
    dp.callback_query.register(scan_new_qr_handler, F.data == "scan_qr")
    
    logger.info("✅ Handlers de QR Code registrados")