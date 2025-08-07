# ===============================================
# ARQUIVO: mandacaru_bot/bot_reports/handlers.py
# Handlers para relatórios e histórico
# ===============================================

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from aiogram import Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

from core.session import obter_operador_sessao, verificar_autenticacao
from core.db import fazer_requisicao_api
from core.templates import MessageTemplates
from core.utils import Formatters

logger = logging.getLogger(__name__)

# ===============================================
# FUNÇÕES DE RELATÓRIO
# ===============================================

async def buscar_historico_checklist(checklist_id: int) -> Optional[Dict[str, Any]]:
    """Busca histórico detalhado de um checklist"""
    logger.info(f"📊 Buscando histórico do checklist {checklist_id}")
    
    # Buscar dados do checklist
    checklist = await fazer_requisicao_api('GET', f'nr12/checklists/{checklist_id}/')
    
    if not checklist:
        return None
    
    # Buscar itens do checklist
    itens = await fazer_requisicao_api('GET', f'nr12/checklists/{checklist_id}/itens/')
    
    if itens:
        checklist['itens'] = itens.get('results', []) if isinstance(itens, dict) else itens
    else:
        checklist['itens'] = []
    
    return checklist

async def buscar_checklists_equipamento_periodo(
    equipamento_id: int, 
    dias: int = 30
) -> List[Dict[str, Any]]:
    """Busca checklists de um equipamento nos últimos X dias"""
    logger.info(f"📊 Buscando checklists do equipamento {equipamento_id} - últimos {dias} dias")
    
    result = await fazer_requisicao_api('GET', f'equipamentos/{equipamento_id}/checklists/', 
                                       params={'dias': dias})
    
    if result and result.get('checklists'):
        checklists = result['checklists']
        logger.info(f"✅ {len(checklists)} checklists encontrados")
        return checklists
    
    logger.warning(f"⚠️ Nenhum checklist encontrado para equipamento {equipamento_id}")
    return []

# ===============================================
# HANDLERS DE RELATÓRIO
# ===============================================

def require_auth(handler):
    """Decorator que exige autenticação (reutilizado)"""
    async def wrapper(obj, *args, **kwargs):
        if hasattr(obj, 'chat'):
            chat_id = str(obj.chat.id)
        elif hasattr(obj, 'message') and hasattr(obj.message, 'chat'):
            chat_id = str(obj.message.chat.id)
        else:
            logger.error("❌ Não foi possível determinar chat_id")
            return
        
        if not verificar_autenticacao(chat_id):
            await obj.answer(MessageTemplates.unauthorized_access())
            return
        
        operador = obter_operador_sessao(chat_id)
        kwargs['operador'] = operador
        
        return await handler(obj, *args, **kwargs)
    
    return wrapper

@require_auth
async def mostrar_relatorio_checklist(callback: CallbackQuery, operador=None):
    """Mostra relatório detalhado de um checklist"""
    
    try:
        await callback.answer("📊 Carregando relatório...")
        
        # Extrair ID do checklist
        checklist_id = int(callback.data.split('_')[-1])
        
        # Buscar dados completos
        historico = await buscar_historico_checklist(checklist_id)
        
        if not historico:
            await callback.message.edit_text(
                "❌ **Checklist Não Encontrado**\n\n"
                "Não foi possível carregar os dados do checklist.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data="list_checklists")]
                ])
            )
            return
        
        # Montar relatório
        equipamento_nome = historico.get('equipamento_nome', 'Equipamento')
        data_checklist = historico.get('data_checklist', 'N/A')
        turno = historico.get('turno', 'N/A')
        status = historico.get('status', 'N/A')
        responsavel = historico.get('responsavel_nome', 'N/A')
        
        # Estatísticas dos itens
        itens = historico.get('itens', [])
        total_itens = len(itens)
        itens_ok = len([i for i in itens if i.get('status') == 'OK'])
        itens_nok = len([i for i in itens if i.get('status') == 'NOK'])
        itens_na = len([i for i in itens if i.get('status') == 'NA'])
        itens_pendentes = len([i for i in itens if i.get('status') == 'PENDENTE'])
        
        # Criar texto do relatório
        texto = f"📊 **Relatório do Checklist**\n\n"
        texto += f"🚜 **Equipamento:** {equipamento_nome}\n"
        texto += f"📅 **Data:** {data_checklist}\n"
        texto += f"🕐 **Turno:** {turno}\n"
        texto += f"👤 **Responsável:** {responsavel}\n"
        texto += f"📊 **Status:** {status}\n\n"
        
        texto += f"📋 **Estatísticas:**\n"
        texto += f"✅ **Aprovados:** {itens_ok}/{total_itens}\n"
        texto += f"❌ **Reprovados:** {itens_nok}/{total_itens}\n"
        texto += f"➖ **N/A:** {itens_na}/{total_itens}\n"
        
        if itens_pendentes > 0:
            texto += f"⏳ **Pendentes:** {itens_pendentes}/{total_itens}\n"
        
        # Calcular percentual de aprovação
        if total_itens > 0:
            percentual = (itens_ok / total_itens) * 100
            texto += f"\n📈 **Taxa de Aprovação:** {percentual:.1f}%"
        
        # Mostrar itens reprovados se houver
        if itens_nok > 0:
            texto += f"\n\n❌ **Itens Reprovados:**"
            itens_reprovados = [i for i in itens if i.get('status') == 'NOK']
            for i, item in enumerate(itens_reprovados[:5], 1):  # Mostrar até 5
                nome_item = item.get('item', 'Item')[:30] + "..." if len(item.get('item', '')) > 30 else item.get('item', 'Item')
                texto += f"\n{i}. {nome_item}"
                if item.get('observacao'):
                    obs = item['observacao'][:40] + "..." if len(item['observacao']) > 40 else item['observacao']
                    texto += f"\n   💬 {obs}"
            
            if len(itens_reprovados) > 5:
                texto += f"\n... e mais {len(itens_reprovados) - 5} item(s)"
        
        # Criar keyboard
        keyboard = []
        
        # Botões de ação
        keyboard.append([
            InlineKeyboardButton(text="📋 Detalhes Completos", callback_data=f"report_details_{checklist_id}"),
            InlineKeyboardButton(text="📤 Exportar", callback_data=f"report_export_{checklist_id}")
        ])
        
        # Navegação
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar", callback_data="list_checklists"),
            InlineKeyboardButton(text="🏠 Menu", callback_data="menu_refresh")
        ])
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar relatório: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def mostrar_historico_equipamento(callback: CallbackQuery, operador=None):
    """Mostra histórico de checklists de um equipamento"""
    
    try:
        await callback.answer("📊 Carregando histórico...")
        
        # Extrair ID do equipamento
        equipamento_id = int(callback.data.split('_')[-1])
        
        # Buscar checklists dos últimos 30 dias
        checklists = await buscar_checklists_equipamento_periodo(equipamento_id, 30)
        
        if not checklists:
            await callback.message.edit_text(
                "📊 **Histórico Vazio**\n\n"
                "Não há checklists registrados para este equipamento nos últimos 30 dias.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Criar Checklist", callback_data=f"create_checklist_{equipamento_id}")],
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"equipment_select_{equipamento_id}")]
                ])
            )
            return
        
        # Ordenar por data (mais recente primeiro)
        checklists_ordenados = sorted(
            checklists, 
            key=lambda x: x.get('data_checklist', ''), 
            reverse=True
        )
        
        # Criar texto do histórico
        texto = f"📊 **Histórico de Checklists**\n\n"
        texto += f"📅 **Período:** Últimos 30 dias\n"
        texto += f"📋 **Total:** {len(checklists)} checklist(s)\n\n"
        
        # Mostrar até 10 checklists mais recentes
        keyboard = []
        
        for i, checklist in enumerate(checklists_ordenados[:10], 1):
            data = checklist.get('data_checklist', 'N/A')
            status = checklist.get('status', 'N/A')
            turno = checklist.get('turno', 'N/A')
            
            # Emoji baseado no status
            emoji = "✅" if status == "CONCLUIDO" else "🔄" if status == "EM_ANDAMENTO" else "📋"
            
            texto += f"{i}. {emoji} **{data}** - {turno}\n"
            texto += f"   Status: {status}\n\n"
            
            # Botão para ver detalhes
            callback_data = f"report_checklist_{checklist.get('id', 0)}"
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{emoji} {data} - {turno}",
                    callback_data=callback_data
                )
            ])
        
        if len(checklists_ordenados) > 10:
            texto += f"... e mais {len(checklists_ordenados) - 10} checklist(s)"
        
        # Botões de navegação
        keyboard.append([
            InlineKeyboardButton(text="📈 Estatísticas", callback_data=f"stats_equipment_{equipamento_id}"),
            InlineKeyboardButton(text="📋 Novo Checklist", callback_data=f"create_checklist_{equipamento_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton(text="🔙 Voltar", callback_data=f"equipment_select_{equipamento_id}")
        ])
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar histórico: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

@require_auth
async def mostrar_estatisticas_equipamento(callback: CallbackQuery, operador=None):
    """Mostra estatísticas de um equipamento"""
    
    try:
        await callback.answer("📈 Calculando estatísticas...")
        
        # Extrair ID do equipamento
        equipamento_id = int(callback.data.split('_')[-1])
        
        # Buscar checklists de períodos diferentes
        checklists_30d = await buscar_checklists_equipamento_periodo(equipamento_id, 30)
        checklists_7d = await buscar_checklists_equipamento_periodo(equipamento_id, 7)
        
        # Calcular estatísticas
        total_30d = len(checklists_30d)
        total_7d = len(checklists_7d)
        
        if total_30d == 0:
            await callback.message.edit_text(
                "📈 **Estatísticas**\n\n"
                "Não há dados suficientes para gerar estatísticas.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"qr_list_checklists_{equipamento_id}")]
                ])
            )
            return
        
        # Analisar status dos checklists
        concluidos_30d = len([c for c in checklists_30d if c.get('status') == 'CONCLUIDO'])
        concluidos_7d = len([c for c in checklists_7d if c.get('status') == 'CONCLUIDO'])
        
        # Taxa de conclusão
        taxa_30d = (concluidos_30d / total_30d * 100) if total_30d > 0 else 0
        taxa_7d = (concluidos_7d / total_7d * 100) if total_7d > 0 else 0
        
        # Frequência (checklists por semana)
        freq_semanal = total_30d / 4.3  # 30 dias ≈ 4.3 semanas
        
        # Criar texto das estatísticas
        texto = f"📈 **Estatísticas do Equipamento**\n\n"
        
        texto += f"📊 **Últimos 30 dias:**\n"
        texto += f"• Total de checklists: {total_30d}\n"
        texto += f"• Concluídos: {concluidos_30d}\n"
        texto += f"• Taxa de conclusão: {taxa_30d:.1f}%\n\n"
        
        texto += f"📊 **Últimos 7 dias:**\n"
        texto += f"• Total de checklists: {total_7d}\n"
        texto += f"• Concluídos: {concluidos_7d}\n"
        texto += f"• Taxa de conclusão: {taxa_7d:.1f}%\n\n"
        
        texto += f"⚡ **Frequência:**\n"
        texto += f"• Média: {freq_semanal:.1f} checklists/semana\n\n"
        
        # Tendência
        if taxa_7d > taxa_30d:
            texto += f"📈 **Tendência:** Melhorando (+{taxa_7d - taxa_30d:.1f}%)"
        elif taxa_7d < taxa_30d:
            texto += f"📉 **Tendência:** Declinando ({taxa_7d - taxa_30d:.1f}%)"
        else:
            texto += f"📊 **Tendência:** Estável"
        
        keyboard = [
            [
                InlineKeyboardButton(text="📋 Ver Histórico", callback_data=f"qr_list_checklists_{equipamento_id}"),
                InlineKeyboardButton(text="📋 Novo Checklist", callback_data=f"create_checklist_{equipamento_id}")
            ],
            [InlineKeyboardButton(text="🔙 Voltar", callback_data=f"equipment_select_{equipamento_id}")]
        ]
        
        await callback.message.edit_text(
            texto,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao mostrar estatísticas: {e}")
        await callback.message.edit_text(MessageTemplates.error_generic())

# ===============================================
# REGISTRAR HANDLERS
# ===============================================

def register_handlers(dp: Dispatcher):
    """Registra handlers de relatórios no dispatcher"""
    
    # Callbacks de relatório
    dp.callback_query.register(mostrar_relatorio_checklist, F.data.startswith("report_checklist_"))
    dp.callback_query.register(mostrar_relatorio_checklist, F.data.startswith("checklist_report_"))
    dp.callback_query.register(mostrar_historico_equipamento, F.data.startswith("qr_list_checklists_"))
    dp.callback_query.register(mostrar_historico_equipamento, F.data.startswith("checklist_history_"))
    dp.callback_query.register(mostrar_estatisticas_equipamento, F.data.startswith("stats_equipment_"))
    dp.callback_query.register(mostrar_estatisticas_equipamento, F.data.startswith("qr_report_"))
    
    logger.info("✅ Handlers de relatórios registrados")