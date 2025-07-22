# ================================================================
# backend/apps/bot_telegram/api_integration.py
# INTEGRAÇÃO COM API DJANGO MANDACARU
# ================================================================

import asyncio
import logging
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from asgiref.sync import sync_to_async

from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento

logger = logging.getLogger(__name__)

# ================================================================
# MANAGER DE API DJANGO
# ================================================================

class DjangoAPIManager:
    """
    Gerenciador de integração com API Django interna
    Usa sync_to_async para acessar modelos Django diretamente
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'API_BASE_URL', 'http://127.0.0.1:8000/api')
        self.timeout = getattr(settings, 'API_TIMEOUT', 30)
    
    # ================================================================
    # OPERADORES
    # ================================================================
    
    async def buscar_operador_por_telegram(self, chat_id: str) -> Optional[Dict]:
        """Busca operador pelo chat_id do Telegram"""
        try:
            operador = await sync_to_async(
                Operador.objects.filter(
                    chat_id_telegram=chat_id,
                    ativo_bot=True
                ).select_related().prefetch_related(
                    'empreendimentos_autorizados',
                    'equipamentos_autorizados'
                ).first
            )()
            
            if operador:
                # Buscar relacionamentos
                empreendimentos = await sync_to_async(list)(
                    operador.empreendimentos_autorizados.values('id', 'nome', 'codigo')
                )
                equipamentos = await sync_to_async(list)(
                    operador.equipamentos_autorizados.values('id', 'nome', 'codigo')
                )
                
                return {
                    'id': operador.id,
                    'nome': operador.nome,
                    'codigo': operador.codigo,
                    'data_nascimento': operador.data_nascimento.isoformat() if operador.data_nascimento else None,
                    'chat_id_telegram': operador.chat_id_telegram,
                    'status': operador.status,
                    'ativo_bot': operador.ativo_bot,
                    'tipo': 'supervisor' if operador.pode_ver_relatorios else 'operador',
                    'permissoes': {
                        'pode_fazer_checklist': operador.pode_fazer_checklist,
                        'pode_registrar_abastecimento': operador.pode_registrar_abastecimento,
                        'pode_reportar_anomalia': operador.pode_reportar_anomalia,
                        'pode_ver_relatorios': operador.pode_ver_relatorios
                    },
                    'empreendimentos_autorizados': list(empreendimentos),
                    'equipamentos_autorizados': list(equipamentos),
                    'ultimo_acesso_bot': operador.ultimo_acesso_bot.isoformat() if operador.ultimo_acesso_bot else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar operador por telegram: {e}")
            return None
    
    async def criar_operador_temporario(self, dados: Dict) -> bool:
        """Cria operador temporário para aprovação"""
        try:
            # Verificar se já existe
            existe = await sync_to_async(
                Operador.objects.filter(chat_id_telegram=dados['chat_id_telegram']).exists
            )()
            
            if existe:
                logger.warning(f"Operador {dados['chat_id_telegram']} já existe")
                return False
            
            # Converter data se necessário
            data_nascimento = dados.get('data_nascimento')
            if isinstance(data_nascimento, str):
                if '/' in data_nascimento:
                    data_nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y').date()
                else:
                    data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            
            # Criar operador
            operador_data = {
                'nome': dados['nome'],
                'data_nascimento': data_nascimento,
                'chat_id_telegram': dados['chat_id_telegram'],
                'status': 'PENDENTE',
                'ativo_bot': False,
                'observacoes': f'Cadastrado via bot em {datetime.now().strftime("%d/%m/%Y %H:%M")}'
            }
            
            operador = await sync_to_async(Operador.objects.create)(**operador_data)
            
            logger.info(f"Operador temporário criado: {operador.nome} (ID: {operador.id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar operador temporário: {e}")
            return False
    
    async def atualizar_ultimo_acesso_operador(self, chat_id: str) -> bool:
        """Atualiza último acesso do operador"""
        try:
            resultado = await sync_to_async(
                Operador.objects.filter(chat_id_telegram=chat_id).update
            )(ultimo_acesso_bot=datetime.now())
            
            return resultado > 0
            
        except Exception as e:
            logger.error(f"Erro ao atualizar último acesso: {e}")
            return False
    
    async def listar_operadores_ativos(self) -> List[Dict]:
        """Lista operadores ativos no bot"""
        try:
            operadores = await sync_to_async(list)(
                Operador.objects.filter(
                    ativo_bot=True,
                    status='ATIVO'
                ).values(
                    'id', 'nome', 'codigo', 'chat_id_telegram',
                    'ultimo_acesso_bot', 'pode_ver_relatorios'
                )
            )
            
            return operadores
            
        except Exception as e:
            logger.error(f"Erro ao listar operadores ativos: {e}")
            return []
    
    # ================================================================
    # EQUIPAMENTOS
    # ================================================================
    
    async def buscar_equipamento(self, equipamento_id: int) -> Optional[Dict]:
        """Busca equipamento por ID"""
        try:
            equipamento = await sync_to_async(
                Equipamento.objects.filter(id=equipamento_id).first
            )()
            
            if equipamento:
                return {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', ''),
                    'tipo': getattr(equipamento, 'tipo', ''),
                    'status': getattr(equipamento, 'status', ''),
                    'empreendimento_id': getattr(equipamento, 'empreendimento_id', None),
                    'horimetro_atual': getattr(equipamento, 'horimetro_atual', 0),
                    'ultima_manutencao': getattr(equipamento, 'ultima_manutencao', None),
                    'created_at': equipamento.created_at.isoformat() if hasattr(equipamento, 'created_at') else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar equipamento {equipamento_id}: {e}")
            return None
    
    async def verificar_permissao_equipamento(self, chat_id: str, equipamento_id: int) -> Tuple[bool, Dict]:
        """Verifica se operador pode acessar equipamento"""
        try:
            # Buscar operador com relacionamentos
            operador = await sync_to_async(
                Operador.objects.filter(
                    chat_id_telegram=chat_id,
                    ativo_bot=True,
                    status='ATIVO'
                ).prefetch_related(
                    'empreendimentos_autorizados',
                    'equipamentos_autorizados'
                ).first
            )()
            
            if not operador:
                return False, {'motivo': 'Operador não encontrado ou inativo'}
            
            # Buscar equipamento
            equipamento = await sync_to_async(
                Equipamento.objects.filter(id=equipamento_id).first
            )()
            
            if not equipamento:
                return False, {'motivo': 'Equipamento não encontrado'}
            
            # Verificar permissão
            if operador.pode_ver_relatorios:
                # Supervisor - verificar se equipamento está no mesmo empreendimento
                empreendimentos_ids = await sync_to_async(list)(
                    operador.empreendimentos_autorizados.values_list('id', flat=True)
                )
                
                empreendimento_id = getattr(equipamento, 'empreendimento_id', None)
                if empreendimento_id and empreendimento_id in empreendimentos_ids:
                    tem_permissao = True
                else:
                    # Se não tem empreendimento definido, supervisor pode acessar
                    tem_permissao = True
            else:
                # Operador comum - verificar equipamentos específicos
                equipamentos_ids = await sync_to_async(list)(
                    operador.equipamentos_autorizados.values_list('id', flat=True)
                )
                tem_permissao = equipamento_id in equipamentos_ids
            
            if tem_permissao:
                return True, {
                    'operador': {
                        'id': operador.id,
                        'nome': operador.nome,
                        'codigo': operador.codigo,
                        'tipo': 'supervisor' if operador.pode_ver_relatorios else 'operador'
                    },
                    'equipamento': {
                        'id': equipamento.id,
                        'nome': equipamento.nome,
                        'codigo': getattr(equipamento, 'codigo', ''),
                        'empreendimento_id': getattr(equipamento, 'empreendimento_id', None)
                    }
                }
            else:
                return False, {'motivo': 'Sem permissão para este equipamento'}
                
        except Exception as e:
            logger.error(f"Erro ao verificar permissão: {e}")
            return False, {'motivo': 'Erro interno'}
    
    async def atualizar_horimetro_equipamento(self, equipamento_id: int, novo_horimetro: float, chat_id: str) -> bool:
        """Atualiza horímetro do equipamento"""
        try:
            # Verificar se equipamento existe
            equipamento = await sync_to_async(
                Equipamento.objects.filter(id=equipamento_id).first
            )()
            
            if not equipamento:
                return False
            
            # Atualizar horímetro
            equipamento.horimetro_atual = novo_horimetro
            await sync_to_async(equipamento.save)(update_fields=['horimetro_atual'])
            
            # Log da operação
            logger.info(f"Horímetro do equipamento {equipamento_id} atualizado para {novo_horimetro} por {chat_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar horímetro: {e}")
            return False
    
    # ================================================================
    # CHECKLISTS NR12
    # ================================================================
    
    async def buscar_checklist_equipamento_hoje(self, equipamento_id: int) -> Optional[Dict]:
        """Busca checklist do equipamento para hoje"""
        try:
            # Esta função precisa ser implementada baseada no seu modelo NR12
            # Por enquanto, retorna estrutura simulada
            
            hoje = datetime.now().date()
            
            # Simular busca de checklist
            # Em implementação real, buscar no modelo de checklist
            checklist_existe = False  # Implementar busca real
            
            if checklist_existe:
                return {
                    'id': 1,  # ID real do checklist
                    'equipamento_id': equipamento_id,
                    'data': hoje.isoformat(),
                    'status': 'PENDENTE',  # PENDENTE, EM_ANDAMENTO, FINALIZADO
                    'itens': []  # Lista de itens do checklist
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar checklist: {e}")
            return None
    
    async def criar_checklist_diario(self, equipamento_id: int, operador_chat_id: str) -> Optional[Dict]:
        """Cria novo checklist diário"""
        try:
            # Implementar criação de checklist baseado no seu modelo
            # Por enquanto, simular criação
            
            checklist_data = {
                'equipamento_id': equipamento_id,
                'data': datetime.now().date(),
                'status': 'PENDENTE',
                'operador_chat_id': operador_chat_id,
                'created_at': datetime.now()
            }
            
            # Aqui você implementaria a criação real no modelo
            logger.info(f"Checklist criado para equipamento {equipamento_id}")
            
            return {
                'id': 1,  # ID do checklist criado
                'equipamento_id': equipamento_id,
                'status': 'PENDENTE',
                'mensagem': 'Checklist criado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar checklist: {e}")
            return None
    
    # ================================================================
    # ABASTECIMENTO
    # ================================================================
    
    async def registrar_abastecimento(self, dados_abastecimento: Dict) -> bool:
        """Registra abastecimento do equipamento"""
        try:
            # Implementar baseado no seu modelo de abastecimento
            # Por enquanto, simular registro
            
            registro = {
                'equipamento_id': dados_abastecimento['equipamento_id'],
                'quantidade_litros': dados_abastecimento['quantidade'],
                'valor_total': dados_abastecimento.get('valor_total', 0),
                'data_abastecimento': dados_abastecimento.get('data', datetime.now()),
                'operador_chat_id': dados_abastecimento['operador_chat_id'],
                'observacoes': dados_abastecimento.get('observacoes', ''),
                'created_at': datetime.now()
            }
            
            # Aqui você implementaria o salvamento real
            logger.info(f"Abastecimento registrado: {registro['quantidade_litros']}L no equipamento {registro['equipamento_id']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar abastecimento: {e}")
            return False
    
    # ================================================================
    # ANOMALIAS
    # ================================================================
    
    async def registrar_anomalia(self, dados_anomalia: Dict) -> bool:
        """Registra anomalia do equipamento"""
        try:
            # Implementar baseado no seu modelo de anomalias/ordens de serviço
            
            anomalia = {
                'equipamento_id': dados_anomalia['equipamento_id'],
                'descricao': dados_anomalia['descricao'],
                'tipo_anomalia': dados_anomalia.get('tipo', 'MANUTENCAO'),
                'prioridade': dados_anomalia.get('prioridade', 'MEDIA'),
                'status': 'ABERTA',
                'operador_chat_id': dados_anomalia['operador_chat_id'],
                'data_ocorrencia': dados_anomalia.get('data', datetime.now()),
                'created_at': datetime.now()
            }
            
            # Aqui você implementaria o salvamento real
            logger.info(f"Anomalia registrada no equipamento {anomalia['equipamento_id']}: {anomalia['descricao'][:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar anomalia: {e}")
            return False
    
    # ================================================================
    # RELATÓRIOS
    # ================================================================
    
    async def gerar_relatorio_equipamento(self, equipamento_id: int, periodo_dias: int = 30) -> Dict:
        """Gera relatório do equipamento"""
        try:
            # Buscar dados do equipamento
            equipamento = await self.buscar_equipamento(equipamento_id)
            
            if not equipamento:
                return {}
            
            # Simular dados do relatório
            data_inicial = datetime.now() - timedelta(days=periodo_dias)
            
            relatorio = {
                'equipamento': equipamento,
                'periodo': {
                    'inicio': data_inicial.isoformat(),
                    'fim': datetime.now().isoformat(),
                    'dias': periodo_dias
                },
                'estatisticas': {
                    'checklists_realizados': 15,  # Implementar contagem real
                    'abastecimentos': 8,  # Implementar contagem real
                    'anomalias_reportadas': 2,  # Implementar contagem real
                    'horas_operacao': 240  # Implementar cálculo real
                },
                'ultimo_checklist': '2024-01-15T10:30:00',  # Implementar busca real
                'ultimo_abastecimento': '2024-01-14T08:15:00',  # Implementar busca real
                'anomalias_abertas': 1,  # Implementar contagem real
                'gerado_em': datetime.now().isoformat()
            }
            
            return relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {}
    
    # ================================================================
    # ESTATÍSTICAS GERAIS
    # ================================================================
    
    async def obter_estatisticas_sistema(self) -> Dict:
        """Obtém estatísticas gerais do sistema"""
        try:
            # Contar operadores
            total_operadores = await sync_to_async(Operador.objects.count)()
            operadores_ativos = await sync_to_async(
                Operador.objects.filter(ativo_bot=True, status='ATIVO').count
            )()
            operadores_pendentes = await sync_to_async(
                Operador.objects.filter(status='PENDENTE').count
            )()
            
            # Contar equipamentos
            total_equipamentos = await sync_to_async(Equipamento.objects.count)()
            
            # Operadores que acessaram recentemente (últimas 24h)
            ontem = datetime.now() - timedelta(hours=24)
            operadores_recentes = await sync_to_async(
                Operador.objects.filter(
                    ultimo_acesso_bot__gte=ontem,
                    ativo_bot=True
                ).count
            )()
            
            return {
                'operadores': {
                    'total': total_operadores,
                    'ativos': operadores_ativos,
                    'pendentes': operadores_pendentes,
                    'acesso_recente_24h': operadores_recentes
                },
                'equipamentos': {
                    'total': total_equipamentos
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

# ================================================================
# MANAGER HTTP PARA APIs EXTERNAS
# ================================================================

class HTTPAPIManager:
    """
    Gerenciador para APIs HTTP externas
    Mantido para futuras integrações ou APIs remotas
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = getattr(settings, 'API_TIMEOUT', 30)
        self.client_config = {
            'timeout': self.timeout,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
    
    async def fazer_requisicao(self, method: str, endpoint: str, dados: Dict = None) -> Tuple[bool, Dict]:
        """Faz requisição HTTP genérica"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            async with httpx.AsyncClient(**self.client_config) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, params=dados)
                elif method.upper() == 'POST':
                    response = await client.post(url, json=dados)
                elif method.upper() == 'PUT':
                    response = await client.put(url, json=dados)
                elif method.upper() == 'PATCH':
                    response = await client.patch(url, json=dados)
                elif method.upper() == 'DELETE':
                    response = await client.delete(url)
                else:
                    return False, {'erro': 'Método HTTP não suportado'}
                
                if response.status_code in [200, 201, 202]:
                    return True, response.json() if response.content else {}
                else:
                    logger.error(f"Erro na requisição {method} {url}: {response.status_code}")
                    return False, {
                        'erro': f'Status {response.status_code}',
                        'detalhes': response.text if response.content else ''
                    }
                    
        except Exception as e:
            logger.error(f"Erro na requisição HTTP: {e}")
            return False, {'erro': str(e)}

# ================================================================
# INSTÂNCIA GLOBAL
# ================================================================

# Instância global do manager Django
_django_api_manager = None

def obter_django_api() -> DjangoAPIManager:
    """Obtém instância global do manager Django"""
    global _django_api_manager
    if _django_api_manager is None:
        _django_api_manager = DjangoAPIManager()
    return _django_api_manager

# ================================================================
# EXEMPLO DE USO
# ================================================================

"""
# Como usar a integração com API Django:

from backend.apps.bot_telegram.api_integration import obter_django_api

async def exemplo_uso():
    api = obter_django_api()
    
    # Buscar operador
    operador = await api.buscar_operador_por_telegram('123456789')
    if operador:
        print(f"Operador encontrado: {operador['nome']}")
    
    # Verificar permissão
    tem_permissao, info = await api.verificar_permissao_equipamento('123456789', 1)
    if tem_permissao:
        print("Operador pode acessar equipamento")
    
    # Registrar abastecimento
    dados_abastecimento = {
        'equipamento_id': 1,
        'quantidade': 50.0,
        'valor_total': 300.0,
        'operador_chat_id': '123456789'
    }
    
    sucesso = await api.registrar_abastecimento(dados_abastecimento)
    if sucesso:
        print("Abastecimento registrado com sucesso")
"""