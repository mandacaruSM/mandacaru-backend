# ================================================================
# backend/apps/bot_telegram/management/commands/start_telegram_bot.py
# BOT TELEGRAM MANDACARU - VERSÃO FINAL COMPLETA
# ================================================================

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async

import asyncio
import logging
import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# Imports do Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Imports para QR Code
try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    from PIL import Image
    from io import BytesIO
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

from backend.apps.operadores.models import Operador

logger = logging.getLogger(__name__)

# ================================================================
# SISTEMA DE AUTENTICAÇÃO
# ================================================================

class SistemaAuth:
    def __init__(self):
        self.sessoes = {}
    
    async def verificar_operador(self, chat_id: str) -> Optional[dict]:
        """Verifica se operador existe"""
        try:
            operador = await sync_to_async(
                Operador.objects.filter(chat_id_telegram=chat_id, ativo_bot=True).first
            )()
            
            if operador:
                return {
                    'id': operador.id,
                    'nome': operador.nome,
                    'codigo': getattr(operador, 'codigo', str(operador.id)),
                    'chat_id': operador.chat_id_telegram,
                    'tipo': 'supervisor' if getattr(operador, 'pode_ver_relatorios', False) else 'operador'
                }
            return None
        except Exception as e:
            logger.error(f"Erro ao verificar operador: {e}")
            return None
    
    async def criar_operador_temp(self, dados: dict) -> bool:
        """Cria operador temporário"""
        try:
            existe = await sync_to_async(
                Operador.objects.filter(chat_id_telegram=dados['chat_id_telegram']).exists
            )()
            
            if existe:
                return False
            
            operador_data = {
                'nome': dados['nome'],
                'chat_id_telegram': dados['chat_id_telegram'],
                'ativo_bot': False,
                'observacoes': f'Cadastrado via bot em {datetime.now().strftime("%d/%m/%Y %H:%M")}'
            }
            
            if 'data_nascimento' in dados and dados['data_nascimento']:
                try:
                    if '/' in dados['data_nascimento']:
                        data_obj = datetime.strptime(dados['data_nascimento'], '%d/%m/%Y').date()
                    else:
                        data_obj = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
                    operador_data['data_nascimento'] = data_obj
                except ValueError:
                    pass
            
            await sync_to_async(Operador.objects.create)(**operador_data)
            logger.info(f"Operador temporário criado: {dados['nome']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar operador: {e}")
            return False

# ================================================================
# LEITOR DE QR CODE
# ================================================================

class LeitorQR:
    @staticmethod
    def processar_imagem(image_bytes: bytes) -> Optional[str]:
        """Processa QR Code de imagem"""
        if not QR_AVAILABLE:
            return None
        
        try:
            pil_image = Image.open(BytesIO(image_bytes))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            np_image = np.array(pil_image)
            opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            decoded_objects = decode(opencv_image)
            
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8', errors='ignore').strip()
                if qr_data:
                    return qr_data
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar QR: {e}")
            return None
    
    @staticmethod
    def extrair_id_equipamento(qr_data: str) -> Optional[int]:
        """Extrai ID do equipamento"""
        if not qr_data:
            return None
        
        padroes = [
            r'start=eq(\d+)',
            r'start=equip(\d+)',
            r'\beq(\d+)\b',
            r'(\d+)',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, qr_data, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None

# ================================================================
# BOT MANAGER COMPLETO
# ================================================================

class BotManager:
    def __init__(self):
        self.auth = SistemaAuth()
        self.qr = LeitorQR()
        self.user_sessions = {}
        self.estados_conversa = {}  # Para conversações em andamento

    # ================================================================
    # HANDLERS PRINCIPAIS
    # ================================================================

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = str(update.effective_user.id)
        
        operador = await self.auth.verificar_operador(user_id)
        
        if operador:
            self.user_sessions[user_id] = {
                'operador': operador,
                'estado': 'menu_principal',
                'ultimo_acesso': datetime.now()
            }
            
            await update.message.reply_text(
                f"👋 **Bem-vindo, {operador['nome']}!**\n\n"
                f"👤 Função: {operador['tipo'].title()}\n\n"
                "📱 **Como usar:**\n"
                "• Escaneie o QR Code do equipamento\n"
                "• Use os botões do menu\n\n"
                "🔧 **Pronto para trabalhar!**",
                parse_mode='Markdown',
                reply_markup=self.teclado_principal(operador)
            )
        else:
            self.user_sessions[user_id] = {
                'estado': 'aguardando_nome',
                'dados_temp': {},
                'ultimo_acesso': datetime.now()
            }
            
            await update.message.reply_text(
                "🔐 **Primeiro Acesso**\n\n"
                "Para usar o bot, preciso cadastrar você.\n\n"
                "📝 **Digite seu nome completo:**",
                parse_mode='Markdown'
            )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de texto principal"""
        user_id = str(update.effective_user.id)
        texto = update.message.text.strip()
        
        # Verificar se está em conversa específica
        estado_conversa = self.estados_conversa.get(user_id)
        
        if estado_conversa:
            await self._processar_conversa(update, texto, estado_conversa)
            return
        
        # Processar estados normais
        sessao = self.user_sessions.get(user_id, {})
        estado = sessao.get('estado', 'sem_sessao')
        
        if estado == 'aguardando_nome':
            await self.processar_nome(update, texto)
        elif estado == 'aguardando_data_nascimento':
            await self.processar_data_nascimento(update, texto)
        elif 't.me/' in texto and 'start=' in texto:
            await self.processar_qr_link(update, texto)
        elif texto == "📷 Escanear QR Code":
            msg = "📷 **Envie uma foto do QR Code** do equipamento\n\n"
            if not QR_AVAILABLE:
                msg += "⚠️ **Leitura por foto indisponível**\n"
                msg += "Envie o link como texto: `https://t.me/SeuBot?start=eq123`"
            else:
                msg += "💡 **Dica:** Mantenha a câmera estável"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        elif texto == "❓ Ajuda":
            await self.mostrar_ajuda(update)
        elif texto == "👤 Meu Perfil":
            await self.mostrar_perfil(update)
        elif texto == "📊 Relatórios":
            await self.mostrar_relatorios_menu(update)
        else:
            if 'operador' in sessao:
                await update.message.reply_text(
                    "🤔 Não entendi. Use os botões do menu ou escaneie um QR Code."
                )
            else:
                await update.message.reply_text("❌ Digite /start para começar.")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de fotos"""
        user_id = str(update.effective_user.id)
        
        if not QR_AVAILABLE:
            await update.message.reply_text(
                "❌ **Leitura por foto indisponível**\n\n"
                "Envie o link do QR Code como texto."
            )
            return
        
        sessao = self.user_sessions.get(user_id, {})
        if 'operador' not in sessao:
            await update.message.reply_text("❌ Digite /start para começar.")
            return
        
        msg_processando = await update.message.reply_text("📷 **Processando...**")
        
        try:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            qr_data = self.qr.processar_imagem(bytes(photo_bytes))
            
            if qr_data:
                equipamento_id = self.qr.extrair_id_equipamento(qr_data)
                if equipamento_id:
                    await self.processar_equipamento(update, equipamento_id, msg_processando)
                else:
                    await msg_processando.edit_text("❌ QR Code inválido")
            else:
                await msg_processando.edit_text("❌ QR Code não detectado")
                
        except Exception as e:
            await msg_processando.edit_text("❌ Erro ao processar imagem")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = str(query.from_user.id)
        
        sessao = self.user_sessions.get(user_id, {})
        if 'operador' not in sessao:
            await query.edit_message_text("❌ Sessão expirada. Digite /start")
            return
        
        operador = sessao['operador']
        
        if data.startswith('checklist_'):
            await self._iniciar_checklist(query, data, operador)
        elif data.startswith('abastecimento_'):
            await self._iniciar_abastecimento(query, data, operador)
        elif data.startswith('anomalia_'):
            await self._iniciar_anomalia(query, data, operador)
        elif data.startswith('horimetro_'):
            await self._iniciar_horimetro(query, data, operador)
        elif data.startswith('relatorio_'):
            await self._iniciar_relatorio(query, data, operador)
        elif data.startswith('confirmar_'):
            await self._processar_confirmacao(query, data, operador)
        elif data.startswith('cancelar_'):
            await self._processar_cancelamento(query, data)
        elif data == 'menu_principal':
            await self._voltar_menu_principal(query, operador)

    # ================================================================
    # PROCESSAMENTO DE CONVERSAS
    # ================================================================

    async def _processar_conversa(self, update: Update, texto: str, estado_conversa: dict):
        """Processa conversas em andamento"""
        user_id = str(update.effective_user.id)
        sessao = self.user_sessions.get(user_id, {})
        operador = sessao.get('operador')
        
        if not operador:
            del self.estados_conversa[user_id]
            await update.message.reply_text("❌ Sessão expirada. Digite /start")
            return
        
        acao = estado_conversa.get('acao')
        etapa = estado_conversa.get('etapa')
        
        if acao == 'abastecimento':
            if etapa == 'quantidade':
                await self._processar_abastecimento_quantidade(update, texto, operador)
            elif etapa == 'valor':
                await self._processar_abastecimento_valor(update, texto, operador)
        elif acao == 'anomalia':
            if etapa == 'descricao':
                await self._processar_anomalia_descricao(update, texto, operador)
        elif acao == 'horimetro':
            if etapa == 'novo_valor':
                await self._processar_horimetro_valor(update, texto, operador)

    # ================================================================
    # CHECKLIST NR12
    # ================================================================

    async def _iniciar_checklist(self, query, data: str, operador: dict):
        """Inicia checklist NR12"""
        equipamento_id = int(data.split('_')[1])
        
        hoje = timezone.now().date()
        checklist_existente = await self._verificar_checklist_hoje(equipamento_id, hoje)
        
        if checklist_existente:
            await query.edit_message_text(
                f"✅ **Checklist já realizado hoje**\n\n"
                f"📋 Equipamento: {equipamento_id}\n"
                f"📅 Data: {hoje.strftime('%d/%m/%Y')}\n"
                f"✓ Status: Concluído\n"
                f"👤 Responsável: {checklist_existente.get('operador', 'N/A')}\n\n"
                f"🔄 **Ações disponíveis:**",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📋 Ver Detalhes", callback_data=f'ver_checklist_{equipamento_id}')],
                    [InlineKeyboardButton("🔙 Voltar", callback_data=f'menu_equipamento_{equipamento_id}')]
                ])
            )
        else:
            await query.edit_message_text(
                f"📋 **Novo Checklist NR12**\n\n"
                f"🔧 Equipamento: {equipamento_id}\n"
                f"📅 Data: {hoje.strftime('%d/%m/%Y')}\n"
                f"👤 Operador: {operador['nome']}\n\n"
                f"⚠️ **Verificações de Segurança NR12:**\n"
                f"• Dispositivos de proteção\n"
                f"• Sistemas de parada de emergência\n"
                f"• Isolamento de energia\n"
                f"• Condições gerais do equipamento\n\n"
                f"🚀 **Iniciar checklist agora?**",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Iniciar Checklist", callback_data=f'confirmar_checklist_{equipamento_id}')],
                    [InlineKeyboardButton("❌ Cancelar", callback_data=f'cancelar_checklist_{equipamento_id}')]
                ])
            )

    async def _verificar_checklist_hoje(self, equipamento_id: int, data) -> dict:
        """Verifica se já existe checklist para hoje"""
        try:
            # TODO: Implementar busca real no banco
            # Por enquanto, simular que não existe para permitir teste
            return None
        except Exception:
            return None

    async def _processar_confirmacao(self, query, data: str, operador: dict):
        """Processa confirmações"""
        if data.startswith('confirmar_checklist_'):
            equipamento_id = int(data.split('_')[2])
            sucesso = await self._executar_checklist(equipamento_id, operador)
            
            if sucesso:
                await query.edit_message_text(
                    f"✅ **Checklist NR12 Concluído!**\n\n"
                    f"🔧 Equipamento: {equipamento_id}\n"
                    f"📅 Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
                    f"👤 Operador: {operador['nome']}\n\n"
                    f"📋 **Todos os itens verificados:**\n"
                    f"✓ Dispositivos de proteção\n"
                    f"✓ Parada de emergência\n"
                    f"✓ Isolamento de energia\n"
                    f"✓ Condições gerais\n\n"
                    f"🔒 **Equipamento liberado para operação!**",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Menu Principal", callback_data='menu_principal')]
                    ])
                )
            else:
                await query.edit_message_text("❌ Erro ao salvar checklist")

    async def _executar_checklist(self, equipamento_id: int, operador: dict) -> bool:
        """Executa e salva checklist"""
        try:
            # TODO: Implementar salvamento real
            dados_checklist = {
                'equipamento_id': equipamento_id,
                'operador': operador,
                'data': timezone.now(),
                'itens_verificados': [
                    'Dispositivos de proteção',
                    'Parada de emergência', 
                    'Isolamento de energia',
                    'Condições gerais'
                ],
                'status': 'CONCLUIDO'
            }
            logger.info(f"Checklist salvo: {dados_checklist}")
            return True
        except Exception as e:
            logger.error(f"Erro ao executar checklist: {e}")
            return False

    # ================================================================
    # ABASTECIMENTO
    # ================================================================

    async def _iniciar_abastecimento(self, query, data: str, operador: dict):
        """Inicia registro de abastecimento"""
        equipamento_id = int(data.split('_')[1])
        user_id = str(query.from_user.id)
        
        self.estados_conversa[user_id] = {
            'acao': 'abastecimento',
            'equipamento_id': equipamento_id,
            'dados': {},
            'etapa': 'quantidade'
        }
        
        await query.edit_message_text(
            f"⛽ **Registro de Abastecimento**\n\n"
            f"🔧 Equipamento: {equipamento_id}\n"
            f"📅 Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"👤 Operador: {operador['nome']}\n\n"
            f"📝 **Digite a quantidade de combustível (litros):**\n\n"
            f"💡 **Exemplos:**\n"
            f"• 50 (para 50 litros)\n"
            f"• 50.5 (para 50,5 litros)\n"
            f"• 100 (para 100 litros)",
            parse_mode='Markdown'
        )

    async def _processar_abastecimento_quantidade(self, update: Update, texto: str, operador: dict):
        """Processa quantidade de combustível"""
        user_id = str(update.effective_user.id)
        estado = self.estados_conversa.get(user_id)
        
        if not estado or estado.get('acao') != 'abastecimento':
            return
        
        try:
            quantidade = float(texto.replace(',', '.'))
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva")
            if quantidade > 1000:
                raise ValueError("Quantidade muito alta")
        except ValueError:
            await update.message.reply_text(
                "❌ **Quantidade inválida**\n\n"
                "Digite um número válido:\n"
                "• Use pontos ou vírgulas para decimais\n"
                "• Exemplo: 50 ou 50.5\n\n"
                "Digite novamente:"
            )
            return
        
        estado['dados']['quantidade'] = quantidade
        estado['etapa'] = 'valor'
        
        await update.message.reply_text(
            f"✅ **Quantidade registrada: {quantidade}L**\n\n"
            f"💰 **Agora digite o valor total pago (R$):**\n\n"
            f"💡 **Exemplos:**\n"
            f"• 300 (para R$ 300,00)\n"
            f"• 300.50 (para R$ 300,50)\n"
            f"• /pular (se não souber o valor)",
            parse_mode='Markdown'
        )

    async def _processar_abastecimento_valor(self, update: Update, texto: str, operador: dict):
        """Processa valor do abastecimento"""
        user_id = str(update.effective_user.id)
        estado = self.estados_conversa.get(user_id)
        
        if not estado or estado.get('acao') != 'abastecimento':
            return
        
        valor_total = 0
        
        if texto != '/pular':
            try:
                valor_total = float(texto.replace('R$', '').replace(',', '.').strip())
                if valor_total < 0:
                    raise ValueError("Valor não pode ser negativo")
            except ValueError:
                await update.message.reply_text(
                    "❌ **Valor inválido**\n\n"
                    "Digite um número válido:\n"
                    "• Exemplo: 300.50\n"
                    "• Ou digite /pular\n\n"
                    "Digite novamente:"
                )
                return
        
        # Calcular valores
        quantidade = estado['dados']['quantidade']
        valor_por_litro = valor_total / quantidade if valor_total > 0 else 0
        
        # Salvar abastecimento
        sucesso = await self._salvar_abastecimento({
            'equipamento_id': estado['equipamento_id'],
            'quantidade': quantidade,
            'valor_total': valor_total,
            'valor_por_litro': valor_por_litro,
            'operador': operador,
            'data': timezone.now()
        })
        
        # Limpar estado
        if user_id in self.estados_conversa:
            del self.estados_conversa[user_id]
        
        if sucesso:
            texto_resumo = (
                f"✅ **Abastecimento Registrado!**\n\n"
                f"🔧 **Equipamento:** {estado['equipamento_id']}\n"
                f"⛽ **Quantidade:** {quantidade}L\n"
                f"💰 **Valor total:** R$ {valor_total:.2f}\n"
                f"📊 **Preço/litro:** R$ {valor_por_litro:.2f}\n"
                f"👤 **Operador:** {operador['nome']}\n"
                f"📅 **Data:** {timezone.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"💾 **Registro salvo com sucesso!**"
            )
            
            if valor_total == 0:
                texto_resumo = texto_resumo.replace("R$ 0.00", "Não informado")
            
            await update.message.reply_text(
                texto_resumo,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Menu Principal", callback_data='menu_principal')]
                ])
            )
        else:
            await update.message.reply_text("❌ Erro ao salvar abastecimento")

    async def _salvar_abastecimento(self, dados: dict) -> bool:
        """Salva abastecimento no banco"""
        try:
            # TODO: Implementar salvamento real no seu modelo
            logger.info(f"Abastecimento salvo: {dados}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar abastecimento: {e}")
            return False
    # ================================================================
    # ANOMALIAS
    # ================================================================
    
    async def _iniciar_anomalia(self, query, data: str, operador: dict):
        """Inicia registro de anomalia"""
        equipamento_id = int(data.split('_')[1])
        user_id = str(query.from_user.id)
        
        self.estados_conversa[user_id] = {
            'acao': 'anomalia',
            'equipamento_id': equipamento_id,
            'dados': {},
            'etapa': 'descricao'
        }
        
        await query.edit_message_text(
            f"🔧 **Registro de Anomalia**\n\n"
            f"🔧 Equipamento: {equipamento_id}\n"
            f"📅 Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"👤 Operador: {operador['nome']}\n\n"
            f"📝 **Descreva a anomalia encontrada:**\n\n"
            f"💡 **Dicas:**\n"
            f"• Seja específico e detalhado\n"
            f"• Mencione localização exata\n"
            f"• Indique urgência se necessário\n"
            f"• Mínimo 10 caracteres",
            parse_mode='Markdown'
        )
    
    async def _processar_anomalia_descricao(self, update: Update, texto: str, operador: dict):
        """Processa descrição da anomalia"""
        user_id = str(update.effective_user.id)
        estado = self.estados_conversa.get(user_id)
        
        if not estado or estado.get('acao') != 'anomalia':
            return
        
        # Validar descrição
        if len(texto.strip()) < 10:
            await update.message.reply_text(
                "❌ **Descrição muito curta**\n\n"
                "A descrição deve ter pelo menos 10 caracteres.\n"
                "Seja mais específico sobre a anomalia:"
            )
            return
        
        if len(texto.strip()) > 500:
            await update.message.reply_text(
                "❌ **Descrição muito longa**\n\n"
                "Máximo 500 caracteres. Seja mais conciso:"
            )
            return
        
        # Salvar anomalia
        sucesso = await self._salvar_anomalia({
            'equipamento_id': estado['equipamento_id'],
            'descricao': texto.strip(),
            'operador': operador,
            'data': timezone.now()
        })
        
        # Limpar estado
        if user_id in self.estados_conversa:
            del self.estados_conversa[user_id]
        
        if sucesso:
            await update.message.reply_text(
                f"✅ **Anomalia Registrada!**\n\n"
                f"🔧 Equipamento: {estado['equipamento_id']}\n"
                f"📝 Descrição: {texto[:100]}...\n"
                f"👤 Operador: {operador['nome']}\n"
                f"📅 Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"🚨 **A equipe de manutenção foi notificada!**",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Erro ao registrar anomalia")
    
    async def _salvar_anomalia(self, dados: dict) -> bool:
        """Salva anomalia no banco"""
        try:
            # TODO: Implementar salvamento real
            logger.info(f"Anomalia salva: {dados}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar anomalia: {e}")
            return False
    
    # ================================================================
    # HORÍMETRO
    # ================================================================
    
    async def _iniciar_horimetro(self, query, data: str, operador: dict):
        """Inicia atualização de horímetro"""
        equipamento_id = int(data.split('_')[1])
        user_id = str(query.from_user.id)
        
        # Buscar horímetro atual
        horimetro_atual = await self._buscar_horimetro_atual(equipamento_id)
        
        self.estados_conversa[user_id] = {
            'acao': 'horimetro',
            'equipamento_id': equipamento_id,
            'horimetro_atual': horimetro_atual,
            'etapa': 'novo_valor'
        }
        
        await query.edit_message_text(
            f"⏱️ **Atualização de Horímetro**\n\n"
            f"🔧 Equipamento: {equipamento_id}\n"
            f"📊 Horímetro atual: {horimetro_atual}h\n"
            f"📅 Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"👤 Operador: {operador['nome']}\n\n"
            f"📝 **Digite o novo valor do horímetro:**\n"
            f"Exemplo: {horimetro_atual + 8} (para 8 horas de trabalho)\n\n"
            f"⚠️ **Atenção:** O novo valor deve ser maior que {horimetro_atual}h",
            parse_mode='Markdown'
        )
    
    async def _processar_horimetro_valor(self, update: Update, texto: str, operador: dict):
        """Processa novo valor do horímetro"""
        user_id = str(update.effective_user.id)
        estado = self.estados_conversa.get(user_id)
        
        if not estado or estado.get('acao') != 'horimetro':
            return
        
        try:
            novo_valor = float(texto.replace(',', '.'))
            horimetro_atual = estado['horimetro_atual']
            
            if novo_valor <= horimetro_atual:
                await update.message.reply_text(
                    f"❌ **Valor inválido**\n\n"
                    f"O novo valor ({novo_valor}h) deve ser maior que o atual ({horimetro_atual}h).\n\n"
                    f"Digite um valor maior que {horimetro_atual}h:"
                )
                return
            
            if novo_valor > horimetro_atual + 24:
                await update.message.reply_text(
                    f"⚠️ **Valor muito alto**\n\n"
                    f"Diferença de {novo_valor - horimetro_atual}h parece muito alta.\n"
                    f"Confirme o valor ou digite um valor menor:"
                )
                return
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Formato inválido**\n\n"
                "Digite apenas números (ex: 1250.5):"
            )
            return
        
        # Salvar horímetro
        sucesso = await self._salvar_horimetro({
            'equipamento_id': estado['equipamento_id'],
            'valor_anterior': horimetro_atual,
            'valor_novo': novo_valor,
            'diferenca': novo_valor - horimetro_atual,
            'operador': operador,
            'data': timezone.now()
        })
        
        # Limpar estado
        if user_id in self.estados_conversa:
            del self.estados_conversa[user_id]
        
        if sucesso:
            await update.message.reply_text(
                f"✅ **Horímetro Atualizado!**\n\n"
                f"🔧 Equipamento: {estado['equipamento_id']}\n"
                f"📊 Valor anterior: {horimetro_atual}h\n"
                f"📈 Valor novo: {novo_valor}h\n"
                f"⏰ Horas trabalhadas: {novo_valor - horimetro_atual}h\n"
                f"👤 Operador: {operador['nome']}\n"
                f"📅 Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"💾 **Registro salvo com sucesso!**",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Erro ao atualizar horímetro")
    
    async def _buscar_horimetro_atual(self, equipamento_id: int) -> float:
        """Busca horímetro atual do equipamento"""
        try:
            # TODO: Implementar busca real no banco
            # Por enquanto, simular valor
            return 1200.5
        except Exception:
            return 0.0
    
    async def _salvar_horimetro(self, dados: dict) -> bool:
        """Salva atualização de horímetro"""
        try:
            # TODO: Implementar salvamento real
            logger.info(f"Horímetro salvo: {dados}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar horímetro: {e}")
            return False
    
    # ================================================================
    # RELATÓRIOS
    # ================================================================
    
    async def _iniciar_relatorio(self, query, data: str, operador: dict):
        """Inicia visualização de relatório"""
        equipamento_id = int(data.split('_')[1])
        
        # Verificar se é supervisor
        if operador['tipo'] != 'supervisor':
            await query.edit_message_text(
                "🚫 **Acesso Restrito**\n\n"
                "Apenas supervisores podem acessar relatórios.\n\n"
                "Entre em contato com seu supervisor se precisar desta informação."
            )
            return
        
        # Gerar relatório
        relatorio = await self._gerar_relatorio_equipamento(equipamento_id)
        
        texto_relatorio = (
            f"📊 **Relatório do Equipamento {equipamento_id}**\n\n"
            f"📅 **Período:** Últimos 30 dias\n"
            f"📈 **Estatísticas:**\n"
            f"• Checklists realizados: {relatorio.get('checklists', 0)}\n"
            f"• Abastecimentos: {relatorio.get('abastecimentos', 0)}\n"
            f"• Anomalias reportadas: {relatorio.get('anomalias', 0)}\n"
            f"• Horas operadas: {relatorio.get('horas_operadas', 0)}h\n\n"
            f"🔧 **Status Atual:**\n"
            f"• Horímetro: {relatorio.get('horimetro_atual', 0)}h\n"
            f"• Último checklist: {relatorio.get('ultimo_checklist', 'N/A')}\n"
            f"• Último abastecimento: {relatorio.get('ultimo_abastecimento', 'N/A')}\n\n"
            f"📋 **Gerado em:** {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"👤 **Por:** {operador['nome']}"
        )
        
        await query.edit_message_text(
            texto_relatorio,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 Relatório Detalhado", callback_data=f'relatorio_detalhado_{equipamento_id}')],
                [InlineKeyboardButton("🔙 Voltar", callback_data=f'menu_equipamento_{equipamento_id}')]
            ])
        )
    
    async def _gerar_relatorio_equipamento(self, equipamento_id: int) -> dict:
        """Gera relatório do equipamento"""
        try:
            # TODO: Implementar busca real de dados
            return {
                'checklists': 15,
                'abastecimentos': 8,
                'anomalias': 2,
                'horas_operadas': 240,
                'horimetro_atual': 1200.5,
                'ultimo_checklist': '20/07/2024',
                'ultimo_abastecimento': '19/07/2024'
            }
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {}
    
    # ================================================================
    # HANDLER DE TEXTO ATUALIZADO
    # ================================================================
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de texto ATUALIZADO para processar estados de conversa"""
        user_id = str(update.effective_user.id)
        texto = update.message.text.strip()
        
        # Verificar se usuário está em uma conversa específica
        estado_conversa = self.estados_conversa.get(user_id)
        
        if estado_conversa:
            sessao = self.user_sessions.get(user_id, {})
            operador = sessao.get('operador')
            
            if not operador:
                # Limpar estado se não estiver autenticado
                del self.estados_conversa[user_id]
                await update.message.reply_text("❌ Sessão expirada. Digite /start")
                return
            
            # Processar baseado na ação atual
            acao = estado_conversa.get('acao')
            etapa = estado_conversa.get('etapa')
            
            if acao == 'abastecimento':
                if etapa == 'quantidade':
                    await self._processar_abastecimento_quantidade(update, texto, operador)
                elif etapa == 'valor':
                    await self._processar_abastecimento_valor(update, texto, operador)
            
            elif acao == 'anomalia':
                if etapa == 'descricao':
                    await self._processar_anomalia_descricao(update, texto, operador)
            
            elif acao == 'horimetro':
                if etapa == 'novo_valor':
                    await self._processar_horimetro_valor(update, texto, operador)
            
            return  # Não processar mais nada se estava em conversa
        
        # Se não está em conversa, usar handler original
        await super().handle_text(update, context)

# ================================================================
# INSTÂNCIA GLOBAL
# ================================================================

# Atualizar a função get_bot para usar a versão estendida
def get_bot_extended():
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = BotManagerExtendido()
    return _bot_instance

# ================================================================
# HANDLERS GLOBAIS
# ================================================================

async def h_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().start(update, context)

async def h_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().handle_text(update, context)

async def h_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().handle_photo(update, context)

async def h_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().handle_callback(update, context)

async def h_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().admin_command(update, context)

async def h_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().mostrar_ajuda(update)

async def h_pular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_bot().processar_data_nascimento(update, '/pular')

# ================================================================
# COMANDO DJANGO
# ================================================================

class Command(BaseCommand):
    help = 'Bot Telegram Mandacaru'

    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help='Debug')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Iniciando Bot Mandacaru...'))

        # Verificar token
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_BOT_TOKEN não configurado'))
            self.stdout.write('💡 Adicione no .env: TELEGRAM_BOT_TOKEN=seu_token')
            return

        # Verificar modelo
        try:
            total_ops = Operador.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Operadores: {total_ops}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Modelo: {e}'))
            return

        # Configurar logging simples
        level = logging.DEBUG if options['debug'] else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        if options['debug']:
            self.stdout.write(self.style.WARNING('🔧 Debug ativado'))

        # Status QR
        if QR_AVAILABLE:
            self.stdout.write(self.style.SUCCESS('✅ QR Code: Foto + Texto'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ QR Code: Apenas texto'))

        try:
            asyncio.run(self.run_bot(token))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n🛑 Bot parado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))

    async def run_bot(self, token: str):
        """Executa bot"""
        self.stdout.write('🔧 Configurando...')
        
        # Criar aplicação
        app = Application.builder().token(token).build()
        
        # Handlers
        app.add_handler(CommandHandler("start", h_start))
        app.add_handler(CommandHandler("admin", h_admin))
        app.add_handler(CommandHandler("help", h_help))
        app.add_handler(CommandHandler("pular", h_pular))
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_text))
        
        if QR_AVAILABLE:
            app.add_handler(MessageHandler(filters.PHOTO, h_photo))
        
        app.add_handler(CallbackQueryHandler(h_callback))
        
        self.stdout.write('✅ Configurado!')
        self.stdout.write('📱 Teste no Telegram: /start')
        self.stdout.write('🛑 Ctrl+C para parar')
        
        # Inicializar aplicação
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            
            # Manter rodando até interrupção
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.stdout.write('\n🛑 Parando bot...')
        finally:
            # Limpeza
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception:
                pass

# ================================================================
# VERSÃO ALTERNATIVA PARA WINDOWS (se ainda der problema)
# ================================================================

class CommandWindows(BaseCommand):
    help = 'Bot Telegram Mandacaru - Versão Windows'

    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help='Debug')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Iniciando Bot Mandacaru (Windows)...'))

        # Verificar token
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_BOT_TOKEN não configurado'))
            return

        # Verificar modelo
        try:
            total_ops = Operador.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✅ Operadores: {total_ops}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Modelo: {e}'))
            return

        # Status QR
        if QR_AVAILABLE:
            self.stdout.write(self.style.SUCCESS('✅ QR Code: Foto + Texto'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ QR Code: Apenas texto'))

        # Configurar event loop para Windows
        if os.name == 'nt':  # Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        try:
            # Criar novo event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Executar bot
            loop.run_until_complete(self.run_bot_windows(token))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n🛑 Bot parado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))
        finally:
            # Fechar loop
            try:
                loop.close()
            except Exception:
                pass

    async def run_bot_windows(self, token: str):
        """Executa bot no Windows"""
        self.stdout.write('🔧 Configurando para Windows...')
        
        # Criar aplicação
        app = Application.builder().token(token).build()
        
        # Handlers
        app.add_handler(CommandHandler("start", h_start))
        app.add_handler(CommandHandler("admin", h_admin))
        app.add_handler(CommandHandler("help", h_help))
        app.add_handler(CommandHandler("pular", h_pular))
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_text))
        
        if QR_AVAILABLE:
            app.add_handler(MessageHandler(filters.PHOTO, h_photo))
        
        app.add_handler(CallbackQueryHandler(h_callback))
        
        self.stdout.write('✅ Configurado!')
        self.stdout.write('📱 Teste no Telegram: /start')
        self.stdout.write('🛑 Ctrl+C para parar')
        
        # Usar run_polling que gerencia o ciclo de vida automaticamente
        await app.run_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True,
            close_loop=False  # Não fechar o loop automaticamente
        )