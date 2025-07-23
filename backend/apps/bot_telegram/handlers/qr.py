# ================================================================
# ARQUIVO: backend/apps/bot_telegram/handlers/qr.py
# Implementação do leitor de QR Code baseado no easy-qr-scan-bot
# ================================================================

import io
import logging
from typing import Optional, Dict, Any
from telegram import Update, PhotoSize
from telegram.ext import ContextTypes
from PIL import Image
import cv2
import numpy as np
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import json
import re
from asgiref.sync import sync_to_async
from django.conf import settings

# Importações dos modelos
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12

logger = logging.getLogger(__name__)


class QRCodeReader:
    """Classe para leitura e processamento de QR Codes"""
    
    def __init__(self):
        self.max_file_size = 20 * 1024 * 1024  # 20MB
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'WEBP']
    
    async def process_photo(self, photo: PhotoSize) -> Optional[str]:
        """Processa uma foto do Telegram e extrai QR Code"""
        try:
            # Baixar arquivo
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Verificar tamanho
            if len(photo_bytes) > self.max_file_size:
                raise ValueError("Arquivo muito grande (máx 20MB)")
            
            # Converter para imagem
            image = Image.open(io.BytesIO(photo_bytes))
            
            # Tentar múltiplos métodos de detecção
            qr_data = await self._detect_qr_multiple_methods(image)
            
            return qr_data
            
        except Exception as e:
            logger.error(f"Erro ao processar foto: {e}")
            return None
    
    async def _detect_qr_multiple_methods(self, image: Image) -> Optional[str]:
        """Tenta detectar QR Code usando múltiplos métodos"""
        
        # Método 1: Detecção direta
        qr_data = self._detect_qr_direct(image)
        if qr_data:
            return qr_data
        
        # Método 2: Com pré-processamento
        qr_data = self._detect_qr_preprocessed(image)
        if qr_data:
            return qr_data
        
        # Método 3: Com rotações
        qr_data = self._detect_qr_rotated(image)
        if qr_data:
            return qr_data
        
        return None
    
    def _detect_qr_direct(self, image: Image) -> Optional[str]:
        """Detecção direta de QR Code"""
        try:
            # Converter para array numpy
            img_array = np.array(image)
            
            # Detectar QR codes
            decoded_objects = pyzbar.decode(img_array, symbols=[ZBarSymbol.QRCODE])
            
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            logger.debug(f"Erro na detecção direta: {e}")
        
        return None
    
    def _detect_qr_preprocessed(self, image: Image) -> Optional[str]:
        """Detecção com pré-processamento da imagem"""
        try:
            # Converter para escala de cinza
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Aplicar threshold adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Detectar QR codes
            decoded_objects = pyzbar.decode(thresh, symbols=[ZBarSymbol.QRCODE])
            
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            logger.debug(f"Erro no pré-processamento: {e}")
        
        return None
    
    def _detect_qr_rotated(self, image: Image) -> Optional[str]:
        """Detecção com rotações da imagem"""
        try:
            for angle in [0, 90, 180, 270]:
                rotated = image.rotate(angle, expand=True)
                decoded_objects = pyzbar.decode(
                    np.array(rotated), 
                    symbols=[ZBarSymbol.QRCODE]
                )
                
                if decoded_objects:
                    return decoded_objects[0].data.decode('utf-8')
        except Exception as e:
            logger.debug(f"Erro na rotação: {e}")
        
        return None


class QRCodeProcessor:
    """Processa dados extraídos do QR Code"""
    
    def __init__(self):
        self.reader = QRCodeReader()
    
    async def process_qr_data(self, qr_data: str) -> Dict[str, Any]:
        """Processa e identifica o tipo de QR Code"""
        
        # Tentar JSON primeiro
        try:
            data = json.loads(qr_data)
            return await self._process_json_qr(data)
        except json.JSONDecodeError:
            pass
        
        # Processar como string
        return await self._process_string_qr(qr_data)
    
    async def _process_json_qr(self, data: dict) -> Dict[str, Any]:
        """Processa QR Code em formato JSON"""
        
        qr_type = data.get('tipo', data.get('type'))
        
        if qr_type == 'operador':
            return {
                'tipo': 'operador',
                'codigo': data.get('codigo'),
                'nome': data.get('nome'),
                'dados': data
            }
        elif qr_type == 'equipamento':
            return {
                'tipo': 'equipamento',
                'id': data.get('id'),
                'codigo': data.get('codigo'),
                'dados': data
            }
        elif qr_type == 'checklist':
            return {
                'tipo': 'checklist',
                'uuid': data.get('uuid'),
                'dados': data
            }
        else:
            return {
                'tipo': 'desconhecido',
                'dados': data
            }
    
    async def _process_string_qr(self, qr_data: str) -> Dict[str, Any]:
        """Processa QR Code em formato string"""
        
        # Padrões para identificar tipos
        patterns = {
            'operador': [
                r'^OP\d+$',  # OP0001
                r'^OPERADOR:\d+$',  # OPERADOR:123
                r'^O-\d+$',  # O-123
            ],
            'equipamento': [
                r'^EQ\d+$',  # EQ0001
                r'^E-\d+$',  # E-123
                r'^EQUIP:\d+$',  # EQUIP:123
                r'equipamento[/_-](\d+)',  # equipamento/123
            ],
            'checklist': [
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',  # UUID
                r'^CL-\d+$',  # CL-123
            ],
            'url': [
                r'^https?://',  # URLs
                r'^t\.me/',  # Links do Telegram
            ]
        }
        
        # Verificar cada padrão
        for tipo, padroes in patterns.items():
            for padrao in padroes:
                if re.match(padrao, qr_data, re.IGNORECASE):
                    return {
                        'tipo': tipo,
                        'valor': qr_data,
                        'padrao': padrao
                    }
        
        # Se for URL do sistema
        if 'mandacaru' in qr_data.lower() or settings.BASE_URL in qr_data:
            return await self._process_system_url(qr_data)
        
        return {
            'tipo': 'texto',
            'valor': qr_data
        }
    
    async def _process_system_url(self, url: str) -> Dict[str, Any]:
        """Processa URLs do sistema Mandacaru"""
        
        # Extrair informações da URL
        patterns = {
            r'/equipamento/(\d+)': ('equipamento', 'id'),
            r'/operador/(\w+)': ('operador', 'codigo'),
            r'/checklist/([0-9a-f-]+)': ('checklist', 'uuid'),
            r'start=eq(\d+)': ('equipamento', 'id'),
            r'start=op(\w+)': ('operador', 'codigo'),
        }
        
        for pattern, (tipo, campo) in patterns.items():
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return {
                    'tipo': tipo,
                    campo: match.group(1),
                    'url_original': url
                }
        
        return {
            'tipo': 'url',
            'valor': url
        }


# Handler principal para fotos
async def handle_qr_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para processar fotos com QR Code"""
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Mensagem de processamento
    processing_msg = await update.message.reply_text(
        "🔍 Processando QR Code...",
        reply_to_message_id=update.message.message_id
    )
    
    try:
        # Obter a foto de maior resolução
        photo = update.message.photo[-1]
        
        # Processar QR Code
        processor = QRCodeProcessor()
        qr_data = await processor.reader.process_photo(photo)
        
        if not qr_data:
            await processing_msg.edit_text(
                "❌ Não foi possível detectar um QR Code na imagem.\n\n"
                "💡 Dicas:\n"
                "• Certifique-se que o QR Code está bem visível\n"
                "• Evite reflexos e sombras\n"
                "• Mantenha a câmera estável\n"
                "• Tente aproximar ou afastar a câmera"
            )
            return
        
        # Processar dados do QR
        qr_info = await processor.process_qr_data(qr_data)
        
        # Processar conforme o tipo
        if qr_info['tipo'] == 'operador':
            await _process_operador_qr(update, context, qr_info, processing_msg)
        elif qr_info['tipo'] == 'equipamento':
            await _process_equipamento_qr(update, context, qr_info, processing_msg)
        elif qr_info['tipo'] == 'checklist':
            await _process_checklist_qr(update, context, qr_info, processing_msg)
        else:
            await processing_msg.edit_text(
                f"📋 QR Code detectado!\n\n"
                f"Tipo: {qr_info['tipo']}\n"
                f"Dados: `{qr_data[:100]}{'...' if len(qr_data) > 100 else ''}`\n\n"
                f"⚠️ Este tipo de QR Code ainda não é suportado."
            )
    
    except Exception as e:
        logger.error(f"Erro ao processar QR Code: {e}")
        await processing_msg.edit_text(
            "❌ Erro ao processar a imagem.\n"
            "Por favor, tente novamente."
        )


async def _process_operador_qr(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              qr_info: dict, processing_msg):
    """Processa QR Code de operador"""
    
    from backend.apps.bot_telegram.utils.sessions import save_session, get_session
    
    try:
        # Extrair código do operador
        codigo = qr_info.get('codigo') or qr_info.get('valor', '').replace('OP', '')
        
        # Buscar operador no banco
        operador = await sync_to_async(Operador.objects.filter(
            codigo=codigo,
            status='ATIVO',
            ativo_bot=True
        ).first)()
        
        if not operador:
            await processing_msg.edit_text(
                "❌ Operador não encontrado ou não autorizado.\n\n"
                "Verifique se:\n"
                "• O QR Code está correto\n"
                "• Você está ativo no sistema\n"
                "• Tem permissão para usar o bot"
            )
            return
        
        # Salvar na sessão
        chat_id = str(update.effective_chat.id)
        save_session(chat_id, {
            'operador_id': operador.id,
            'operador_codigo': operador.codigo,
            'operador_nome': operador.nome,
            'operador_funcao': operador.funcao,
            'autenticado': True
        })
        
        # Atualizar último acesso
        await sync_to_async(operador.atualizar_ultimo_acesso)(chat_id)
        
        # Mensagem de sucesso
        await processing_msg.edit_text(
            f"✅ **Login realizado com sucesso!**\n\n"
            f"👤 Operador: {operador.nome}\n"
            f"💼 Função: {operador.funcao}\n"
            f"🏢 Setor: {operador.setor}\n\n"
            f"📱 **Agora você pode:**\n"
            f"• Escanear QR de equipamentos\n"
            f"• Realizar checklists NR12\n"
            f"• Registrar abastecimentos\n"
            f"• Reportar anomalias\n\n"
            f"🔧 Escaneie o QR de um equipamento para começar!"
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar operador: {e}")
        await processing_msg.edit_text(
            "❌ Erro ao processar login do operador.\n"
            "Por favor, tente novamente."
        )


async def _process_equipamento_qr(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 qr_info: dict, processing_msg):
    """Processa QR Code de equipamento"""
    
    from backend.apps.bot_telegram.utils.sessions import get_session
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    try:
        # Verificar se operador está logado
        chat_id = str(update.effective_chat.id)
        session = get_session(chat_id)
        
        if not session or not session.get('autenticado'):
            await processing_msg.edit_text(
                "❌ Você precisa fazer login primeiro!\n\n"
                "📷 Escaneie o QR Code do seu cartão de operador."
            )
            return
        
        # Extrair ID do equipamento
        equip_id = qr_info.get('id') or qr_info.get('valor', '').replace('EQ', '')
        
        # Buscar equipamento
        equipamento = await sync_to_async(Equipamento.objects.filter(
            id=equip_id,
            ativo_nr12=True
        ).first)()
        
        if not equipamento:
            await processing_msg.edit_text(
                "❌ Equipamento não encontrado ou não está ativo para NR12."
            )
            return
        
        # Verificar permissão do operador
        operador_id = session.get('operador_id')
        operador = await sync_to_async(Operador.objects.get)(id=operador_id)
        
        pode_operar = await sync_to_async(operador.pode_operar_equipamento)(equipamento)
        
        if not pode_operar:
            await processing_msg.edit_text(
                f"❌ Você não tem permissão para operar:\n"
                f"🔧 {equipamento.nome}\n\n"
                f"Entre em contato com seu supervisor."
            )
            return
        
        # Salvar equipamento na sessão
        session['equipamento_atual'] = {
            'id': equipamento.id,
            'nome': equipamento.nome,
            'codigo': equipamento.codigo
        }
        save_session(chat_id, session)
        
        # Criar menu de opções
        keyboard = [
            [InlineKeyboardButton("📋 Checklist NR12", callback_data=f"checklist_{equipamento.id}")],
            [InlineKeyboardButton("⛽ Abastecimento", callback_data=f"abastecimento_{equipamento.id}")],
            [InlineKeyboardButton("⚠️ Reportar Anomalia", callback_data=f"anomalia_{equipamento.id}")],
            [InlineKeyboardButton("📊 Ver Histórico", callback_data=f"historico_{equipamento.id}")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Mensagem com informações do equipamento
        await processing_msg.edit_text(
            f"🔧 **Equipamento Identificado**\n\n"
            f"📌 Nome: {equipamento.nome}\n"
            f"🏷️ Código: {equipamento.codigo}\n"
            f"🏭 Marca: {equipamento.marca}\n"
            f"📐 Modelo: {equipamento.modelo}\n"
            f"🏢 Cliente: {equipamento.cliente.razao_social if equipamento.cliente else 'N/A'}\n\n"
            f"❓ **O que deseja fazer?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar equipamento: {e}")
        await processing_msg.edit_text(
            "❌ Erro ao processar equipamento.\n"
            "Por favor, tente novamente."
        )


async def _process_checklist_qr(update: Update, context: ContextTypes.DEFAULT_TYPE,
                               qr_info: dict, processing_msg):
    """Processa QR Code de checklist"""
    
    try:
        # Extrair UUID do checklist
        checklist_uuid = qr_info.get('uuid') or qr_info.get('valor')
        
        # Buscar checklist
        checklist = await sync_to_async(ChecklistNR12.objects.filter(
            uuid=checklist_uuid
        ).select_related('equipamento', 'operador').first)()
        
        if not checklist:
            await processing_msg.edit_text(
                "❌ Checklist não encontrado."
            )
            return
        
        # Formatar status
        status_emoji = {
            'PENDENTE': '⏳',
            'EM_ANDAMENTO': '🔄',
            'CONCLUIDO': '✅',
            'CANCELADO': '❌'
        }
        
        # Informações do checklist
        await processing_msg.edit_text(
            f"📋 **Checklist NR12**\n\n"
            f"🔧 Equipamento: {checklist.equipamento.nome}\n"
            f"👤 Operador: {checklist.operador.nome}\n"
            f"📅 Data: {checklist.data_checklist.strftime('%d/%m/%Y')}\n"
            f"🕐 Turno: {checklist.get_turno_display()}\n"
            f"📊 Status: {status_emoji.get(checklist.status, '❓')} {checklist.get_status_display()}\n\n"
            f"🔗 Link web: {settings.BASE_URL}/api/nr12/checklist/{checklist.uuid}/\n\n"
            f"💡 Use o link acima para visualizar o checklist completo no navegador."
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar checklist: {e}")
        await processing_msg.edit_text(
            "❌ Erro ao processar checklist.\n"
            "Por favor, tente novamente."
        )