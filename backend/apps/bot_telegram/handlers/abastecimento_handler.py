# ----------------------------------------------------------------
# 7. INTEGRAÇÃO COM BOT TELEGRAM
# backend/apps/bot_telegram/handlers/abastecimento_handler.py
# ----------------------------------------------------------------

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from backend.apps.equipamentos.models import Equipamento
from backend.apps.abastecimento.models import RegistroAbastecimento, TipoCombustivel
from backend.apps.almoxarifado.models import EstoqueCombustivel
from backend.apps.operadores.models import Operador
from datetime import datetime
from decimal import Decimal


class AbastecimentoHandler:
    def __init__(self, user_sessions):
        self.sessions = user_sessions

    async def iniciar_fluxo(self, update: Update, context: ContextTypes.DEFAULT_TYPE, equipamento: Equipamento):
        """Inicia fluxo de abastecimento"""
        chat_id = update.effective_chat.id
        self.sessions[chat_id]["equipamento_id"] = equipamento.id
        self.sessions[chat_id]["estado"] = "abastecimento_escolher_origem"
        
        # Verificar se há combustíveis disponíveis no almoxarifado
        combustiveis_almoxarifado = await self._get_combustiveis_almoxarifado()
        
        keyboard = []
        
        # Sempre permitir posto externo
        keyboard.append([InlineKeyboardButton("⛽ Posto Externo", callback_data="origem_posto")])
        
        # Só mostrar almoxarifado se houver combustíveis disponíveis
        if combustiveis_almoxarifado:
            keyboard.append([InlineKeyboardButton("🏪 Almoxarifado", callback_data="origem_almoxarifado")])
        
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⛽ **Abastecimento - {equipamento.nome}**\n\n"
            f"Escolha a origem do combustível:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def processar_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa callbacks do fluxo de abastecimento"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat.id
        data = query.data
        
        if data == "origem_posto":
            await self._escolher_origem_posto(query, chat_id)
        elif data == "origem_almoxarifado":
            await self._escolher_origem_almoxarifado(query, chat_id)
        elif data.startswith("combustivel_"):
            await self._escolher_combustivel(query, chat_id, data)
        elif data == "cancelar":
            await self._cancelar_fluxo(query, chat_id)

    async def _escolher_origem_posto(self, query, chat_id):
        """Fluxo para posto externo"""
        self.sessions[chat_id]["origem"] = "POSTO_EXTERNO"
        self.sessions[chat_id]["estado"] = "abastecimento_escolher_combustivel"
        
        # Listar todos os combustíveis ativos
        combustiveis = await sync_to_async(list)(
            TipoCombustivel.objects.filter(ativo=True)
        )
        
        keyboard = []
        for combustivel in combustiveis:
            keyboard.append([
                InlineKeyboardButton(
                    f"⛽ {combustivel.nome}",
                    callback_data=f"combustivel_{combustivel.id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_origem")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⛽ **Posto Externo Selecionado**\n\n"
            "Escolha o tipo de combustível:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _escolher_origem_almoxarifado(self, query, chat_id):
        """Fluxo para almoxarifado"""
        self.sessions[chat_id]["origem"] = "ALMOXARIFADO"
        self.sessions[chat_id]["estado"] = "abastecimento_escolher_combustivel"
        
        # Listar apenas combustíveis disponíveis no almoxarifado
        combustiveis_disponiveis = await self._get_combustiveis_almoxarifado()
        
        if not combustiveis_disponiveis:
            await query.edit_message_text(
                "🚫 **Almoxarifado Indisponível**\n\n"
                "Nenhum combustível disponível no almoxarifado no momento.\n"
                "Utilize posto externo ou entre em contato com o almoxarifado.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_origem")
                ]])
            )
            return
        
        keyboard = []
        texto = "🏪 **Almoxarifado Selecionado**\n\nCombustíveis disponíveis:\n\n"
        
        for combustivel, estoque in combustiveis_disponiveis:
            # Indicador visual de estoque
            if estoque.abaixo_do_minimo:
                status_icon = "🔴"
                status_text = f"BAIXO ({estoque.quantidade_em_estoque}L)"
            elif estoque.quantidade_em_estoque < (estoque.estoque_minimo * 2):
                status_icon = "🟡"
                status_text = f"MÉDIO ({estoque.quantidade_em_estoque}L)"
            else:
                status_icon = "🟢"
                status_text = f"OK ({estoque.quantidade_em_estoque}L)"
            
            texto += f"{status_icon} **{combustivel.nome}**: {status_text}\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {combustivel.nome} ({estoque.quantidade_em_estoque}L)",
                    callback_data=f"combustivel_{combustivel.id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_origem")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            texto,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def _escolher_combustivel(self, query, chat_id, data):
        """Processa escolha do combustível"""
        combustivel_id = int(data.split("_")[1])
        combustivel = await sync_to_async(TipoCombustivel.objects.get)(id=combustivel_id)
        
        self.sessions[chat_id]["combustivel_id"] = combustivel_id
        self.sessions[chat_id]["estado"] = "abastecimento_quantidade"
        
        # Informações específicas baseadas na origem
        if self.sessions[chat_id]["origem"] == "ALMOXARIFADO":
            estoque = await sync_to_async(combustivel.get_estoque_almoxarifado)()
            max_disponivel = estoque.quantidade_em_estoque if estoque else 0
            
            texto = (
                f"🏪 **Combustível Selecionado: {combustivel.nome}**\n\n"
                f"📊 **Estoque Disponível:** {max_disponivel}L\n"
                f"💰 **Preço:** R$ {estoque.valor_compra}/L\n\n"
                f"Digite a quantidade em litros (máximo {max_disponivel}L):"
            )
        else:
            texto = (
                f"⛽ **Combustível Selecionado: {combustivel.nome}**\n\n"
                f"💰 **Preço Médio:** R$ {combustivel.preco_medio}/L\n\n"
                f"Digite a quantidade em litros:"
            )
        
        await query.edit_message_text(texto, parse_mode='Markdown')

    async def processar_mensagem(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto no fluxo"""
        chat_id = update.effective_chat.id
        texto = update.message.text.strip()
        estado = self.sessions[chat_id].get("estado")
        
        if estado == "abastecimento_quantidade":
            await self._processar_quantidade(update, texto, chat_id)
        elif estado == "abastecimento_preco":
            await self._processar_preco(update, texto, chat_id)
        elif estado == "abastecimento_horimetro":
            await self._processar_horimetro(update, texto, chat_id)
        elif estado == "abastecimento_local":
            await self._processar_local(update, texto, chat_id)

    async def _processar_quantidade(self, update, texto, chat_id):
        """Processa quantidade informada"""
        try:
            quantidade = float(texto.replace(",", "."))
            
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser maior que zero")
            
            # Validar quantidade se for almoxarifado
            if self.sessions[chat_id]["origem"] == "ALMOXARIFADO":
                combustivel_id = self.sessions[chat_id]["combustivel_id"]
                combustivel = await sync_to_async(TipoCombustivel.objects.get)(id=combustivel_id)
                estoque = await sync_to_async(combustivel.get_estoque_almoxarifado)()
                
                if quantidade > estoque.quantidade_em_estoque:
                    await update.message.reply_text(
                        f"❌ **Quantidade Inválida**\n\n"
                        f"Solicitado: {quantidade}L\n"
                        f"Disponível: {estoque.quantidade_em_estoque}L\n\n"
                        f"Digite uma quantidade menor:",
                        parse_mode='Markdown'
                    )
                    return
                
                # Verificar se ficará abaixo do mínimo
                restante = estoque.quantidade_em_estoque - Decimal(str(quantidade))
                if restante <= estoque.estoque_minimo:
                    await update.message.reply_text(
                        f"⚠️ **Alerta de Estoque**\n\n"
                        f"Após este abastecimento o estoque ficará em {restante}L\n"
                        f"(Mínimo: {estoque.estoque_minimo}L)\n\n"
                        f"Prosseguir mesmo assim?",
                        parse_mode='Markdown'
                    )
            
            self.sessions[chat_id]["quantidade"] = quantidade
            
            # Se for almoxarifado, pular preço (usar preço cadastrado)
            if self.sessions[chat_id]["origem"] == "ALMOXARIFADO":
                combustivel_id = self.sessions[chat_id]["combustivel_id"]
                combustivel = await sync_to_async(TipoCombustivel.objects.get)(id=combustivel_id)
                estoque = await sync_to_async(combustivel.get_estoque_almoxarifado)()
                
                self.sessions[chat_id]["preco_litro"] = float(estoque.valor_compra)
                self.sessions[chat_id]["estado"] = "abastecimento_horimetro"
                
                valor_total = quantidade * float(estoque.valor_compra)
                
                await update.message.reply_text(
                    f"✅ **Quantidade:** {quantidade}L\n"
                    f"💰 **Preço:** R$ {estoque.valor_compra}/L\n"
                    f"💵 **Total:** R$ {valor_total:.2f}\n\n"
                    f"Agora informe o horímetro atual do equipamento:",
                    parse_mode='Markdown'
                )
            else:
                self.sessions[chat_id]["estado"] = "abastecimento_preco"
                await update.message.reply_text(
                    f"✅ **Quantidade:** {quantidade}L\n\n"
                    f"Agora informe o preço por litro (ex: 5.85):",
                    parse_mode='Markdown'
                )
                
        except ValueError:
            await update.message.reply_text(
                "❌ Quantidade inválida. Digite apenas números (ex: 45.5)"
            )

    async def _processar_preco(self, update, texto, chat_id):
        """Processa preço informado (apenas posto externo)"""
        try:
            preco = float(texto.replace(",", "."))
            
            if preco <= 0:
                raise ValueError("Preço deve ser maior que zero")
            
            self.sessions[chat_id]["preco_litro"] = preco
            self.sessions[chat_id]["estado"] = "abastecimento_horimetro"
            
            quantidade = self.sessions[chat_id]["quantidade"]
            valor_total = quantidade * preco
            
            await update.message.reply_text(
                f"✅ **Preço:** R$ {preco:.2f}/L\n"
                f"💵 **Total:** R$ {valor_total:.2f}\n\n"
                f"Agora informe o horímetro atual do equipamento:",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ Preço inválido. Digite apenas números (ex: 5.85)"
            )

    async def _processar_horimetro(self, update, texto, chat_id):
        """Processa horímetro informado"""
        try:
            horimetro = float(texto.replace(",", "."))
            
            if horimetro < 0:
                raise ValueError("Horímetro não pode ser negativo")
            
            self.sessions[chat_id]["horimetro"] = horimetro
            self.sessions[chat_id]["estado"] = "abastecimento_local"
            
            await update.message.reply_text(
                f"✅ **Horímetro:** {horimetro}h\n\n"
                f"Informe o local do abastecimento (ex: Posto Shell - BR-101):",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ Horímetro inválido. Digite apenas números (ex: 2847.5)"
            )

    async def _processar_local(self, update, texto, chat_id):
        """Processa local e finaliza abastecimento"""
        self.sessions[chat_id]["local"] = texto
        await self._salvar_abastecimento(update, chat_id)

    async def _salvar_abastecimento(self, update, chat_id):
        """Salva o registro de abastecimento"""
        try:
            sessao = self.sessions[chat_id]
            
            # Buscar entidades
            equipamento = await sync_to_async(Equipamento.objects.get)(id=sessao["equipamento_id"])
            combustivel = await sync_to_async(TipoCombustivel.objects.get)(id=sessao["combustivel_id"])
            operador_id = sessao.get("operador_id")
            operador = await sync_to_async(Operador.objects.get)(id=operador_id) if operador_id else None
            
            # Criar registro
            registro = await sync_to_async(RegistroAbastecimento.objects.create)(
                equipamento=equipamento,
                origem_combustivel=sessao["origem"],
                data_abastecimento=datetime.now(),
                tipo_combustivel=combustivel,
                quantidade_litros=Decimal(str(sessao["quantidade"])),
                preco_litro=Decimal(str(sessao["preco_litro"])),
                medicao_atual=Decimal(str(sessao["horimetro"])),
                posto_combustivel=sessao["local"],
                cidade="Não informada",  # Poderia capturar localização
                registrado_via_bot=True,
                chat_id_telegram=str(chat_id),
                operador_codigo=operador.codigo if operador else "",
                criado_por_id=1,  # ID do usuário sistema/bot
                observacoes="Registrado via Bot Telegram"
            )
            
            # Preparar mensagem de confirmação
            origem_icon = "🏪" if sessao["origem"] == "ALMOXARIFADO" else "⛽"
            origem_text = "Almoxarifado" if sessao["origem"] == "ALMOXARIFADO" else "Posto Externo"
            
            valor_total = sessao["quantidade"] * sessao["preco_litro"]
            
            confirmacao = (
                f"✅ **Abastecimento Registrado**\n\n"
                f"📋 **Número:** {registro.numero}\n"
                f"🚜 **Equipamento:** {equipamento.nome}\n"
                f"{origem_icon} **Origem:** {origem_text}\n"
                f"⛽ **Combustível:** {combustivel.nome}\n"
                f"📊 **Quantidade:** {sessao['quantidade']}L\n"
                f"💰 **Preço/L:** R$ {sessao['preco_litro']:.2f}\n"
                f"💵 **Total:** R$ {valor_total:.2f}\n"
                f"⏱️ **Horímetro:** {sessao['horimetro']}h\n"
                f"📍 **Local:** {sessao['local']}\n\n"
            )
            
            # Adicionar informações específicas do almoxarifado
            if sessao["origem"] == "ALMOXARIFADO":
                if registro.estoque_depois_abastecimento is not None:
                    confirmacao += (
                        f"📦 **Controle de Estoque:**\n"
                        f"• Antes: {registro.estoque_antes_abastecimento}L\n"
                        f"• Depois: {registro.estoque_depois_abastecimento}L\n"
                        f"• Baixa: -{sessao['quantidade']}L\n\n"
                    )
                
                # Verificar se ficou com estoque baixo
                estoque = await sync_to_async(combustivel.get_estoque_almoxarifado)()
                if estoque and estoque.abaixo_do_minimo:
                    confirmacao += "🚨 **ALERTA:** Estoque ficou abaixo do mínimo!\n\n"
            
            confirmacao += "🔔 Supervisão será notificada para aprovação."
            
            await update.message.reply_text(confirmacao, parse_mode='Markdown')
            
            # Limpar sessão
            self.sessions[chat_id]["estado"] = None
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ **Erro ao registrar abastecimento:**\n{str(e)}\n\n"
                f"Tente novamente ou entre em contato com o suporte."
            )

    async def _get_combustiveis_almoxarifado(self):
        """Retorna combustíveis disponíveis no almoxarifado"""
        try:
            estoques = await sync_to_async(list)(
                EstoqueCombustivel.objects.filter(
                    ativo=True,
                    quantidade_em_estoque__gt=0
                ).select_related('tipo_combustivel')
            )
            
            return [(estoque.tipo_combustivel, estoque) for estoque in estoques]
            
        except Exception:
            return []

    async def _cancelar_fluxo(self, query, chat_id):
        """Cancela o fluxo de abastecimento"""
        self.sessions[chat_id]["estado"] = None
        await query.edit_message_text(
            "❌ Abastecimento cancelado.\n\nUse o menu principal para outras opções."
        )

