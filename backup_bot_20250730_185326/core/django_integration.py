# =====================
# core/django_integration.py
# =====================

"""
Módulo para integração específica com o sistema Django Mandacaru
"""

import httpx
from typing import Dict, Any, List, Optional
from core.config import API_BASE_URL, EMPRESA_NOME
from core.db import fazer_requisicao_api, APIError
import logging

logger = logging.getLogger(__name__)

class MandacaruAPI:
    """Classe para interação específica com a API do Mandacaru"""
    
    @staticmethod
    async def buscar_operador_completo(nome: str) -> List[Dict[str, Any]]:
        """
        Busca operador com informações completas
        """
        try:
            params = {"search": nome, "expand": "setor,cargo"}
            data = await fazer_requisicao_api("GET", "/operadores/", params=params)
            return data.get('results', []) if data else []
        except APIError as e:
            logger.error(f"Erro ao buscar operador completo: {e}")
            return []
    
    @staticmethod
    async def obter_veiculos_operador(operador_id: int) -> List[Dict[str, Any]]:
        """
        Obtém veículos associados ao operador
        """
        try:
            params = {"operador": operador_id}
            data = await fazer_requisicao_api("GET", "/veiculos/", params=params)
            return data.get('results', []) if data else []
        except APIError as e:
            logger.error(f"Erro ao obter veículos do operador {operador_id}: {e}")
            return []
    
    @staticmethod
    async def obter_checklists_pendentes(operador_id: int) -> List[Dict[str, Any]]:
        """
        Obtém checklists pendentes do operador
        """
        try:
            params = {
                "operador": operador_id,
                "status": "pendente",
                "ordering": "-data_criacao"
            }
            data = await fazer_requisicao_api("GET", "/checklists/", params=params)
            return data.get('results', []) if data else []
        except APIError as e:
            logger.error(f"Erro ao obter checklists pendentes: {e}")
            return []
    
    @staticmethod
    async def criar_checklist_nr12(dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Cria checklist específico para NR12
        """
        try:
            # Adicionar campos específicos do NR12
            dados_nr12 = {
                **dados,
                "tipo": "nr12",
                "empresa": EMPRESA_NOME,
                "norma_aplicavel": "NR12",
                "is_obrigatorio": True
            }
            return await fazer_requisicao_api("POST", "/checklists/", json_data=dados_nr12)
        except APIError as e:
            logger.error(f"Erro ao criar checklist NR12: {e}")
            return None
    
    @staticmethod
    async def obter_os_operador(operador_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém ordens de serviço do operador
        """
        try:
            params = {"operador": operador_id, "ordering": "-data_criacao"}
            if status:
                params["status"] = status
            
            data = await fazer_requisicao_api("GET", "/ordens-servico/", params=params)
            return data.get('results', []) if data else []
        except APIError as e:
            logger.error(f"Erro ao obter OS do operador {operador_id}: {e}")
            return []
    
    @staticmethod
    async def criar_os(dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Cria nova ordem de serviço
        """
        try:
            return await fazer_requisicao_api("POST", "/ordens-servico/", json_data=dados)
        except APIError as e:
            logger.error(f"Erro ao criar OS: {e}")
            return None
    
    @staticmethod
    async def registrar_abastecimento(dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Registra novo abastecimento
        """
        try:
            return await fazer_requisicao_api("POST", "/abastecimentos/", json_data=dados)
        except APIError as e:
            logger.error(f"Erro ao registrar abastecimento: {e}")
            return None
    
    @staticmethod
    async def obter_historico_abastecimento(veiculo_id: int, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém histórico de abastecimento de um veículo
        """
        try:
            params = {
                "veiculo": veiculo_id,
                "ordering": "-data_abastecimento",
                "limit": limite
            }
            data = await fazer_requisicao_api("GET", "/abastecimentos/", params=params)
            return data.get('results', []) if data else []
        except APIError as e:
            logger.error(f"Erro ao obter histórico de abastecimento: {e}")
            return []
    
    @staticmethod
    async def obter_relatorio_financeiro(operador_id: int, periodo: str = "mensal") -> Optional[Dict[str, Any]]:
        """
        Obtém relatório financeiro do operador
        """
        try:
            params = {"operador": operador_id, "periodo": periodo}
            data = await fazer_requisicao_api("GET", "/relatorios/financeiro/", params=params)
            return data
        except APIError as e:
            logger.error(f"Erro ao obter relatório financeiro: {e}")
            return None
    
    @staticmethod
    async def gerar_qrcode_veiculo(veiculo_id: int) -> Optional[Dict[str, Any]]:
        """
        Gera QR Code para um veículo
        """
        try:
            dados = {"veiculo_id": veiculo_id, "tipo": "veiculo"}
            return await fazer_requisicao_api("POST", "/qrcodes/", json_data=dados)
        except APIError as e:
            logger.error(f"Erro ao gerar QR Code: {e}")
            return None
    
    @staticmethod
    async def validar_qrcode(codigo: str) -> Optional[Dict[str, Any]]:
        """
        Valida um QR Code
        """
        try:
            params = {"codigo": codigo}
            data = await fazer_requisicao_api("GET", "/qrcodes/validar/", params=params)
            return data
        except APIError as e:
            logger.error(f"Erro ao validar QR Code: {e}")
            return None

class NotificacaoMandacaru:
    """Classe para notificações específicas do sistema Mandacaru"""
    
    @staticmethod
    async def notificar_checklist_vencendo(operador_id: int, checklist_id: int) -> bool:
        """
        Notifica sobre checklist vencendo
        """
        try:
            dados = {
                "tipo": "checklist_vencendo",
                "operador": operador_id,
                "checklist": checklist_id,
                "canal": "telegram"
            }
            result = await fazer_requisicao_api("POST", "/notificacoes/", json_data=dados)
            return result is not None
        except APIError:
            return False
    
    @staticmethod
    async def notificar_os_atualizada(operador_id: int, os_id: int, novo_status: str) -> bool:
        """
        Notifica sobre atualização de OS
        """
        try:
            dados = {
                "tipo": "os_atualizada",
                "operador": operador_id,
                "ordem_servico": os_id,
                "status": novo_status,
                "canal": "telegram"
            }
            result = await fazer_requisicao_api("POST", "/notificacoes/", json_data=dados)
            return result is not None
        except APIError:
            return False

class UtilsMandacaru:
    """Utilitários específicos do Mandacaru"""
    
    @staticmethod
    def calcular_prazo_checklist(tipo_checklist: str) -> int:
        """
        Calcula prazo em horas baseado no tipo de checklist
        """
        prazos = {
            "diario": 24,
            "semanal": 168,  # 7 dias
            "mensal": 720,   # 30 dias
            "nr12": 8,       # 8 horas para NR12
            "veiculo": 24,
            "equipamento": 48
        }
        return prazos.get(tipo_checklist.lower(), 24)
    
    @staticmethod
    def formatar_placa_veiculo(placa: str) -> str:
        """
        Formata placa de veículo brasileiro
        """
        placa = placa.upper().replace("-", "").replace(" ", "")
        if len(placa) == 7:
            return f"{placa[:3]}-{placa[3:]}"
        return placa
    
    @staticmethod
    def validar_nr12_compliance(checklist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida conformidade com NR12
        """
        resultado = {
            "conforme": True,
            "alertas": [],
            "bloqueios": []
        }
        
        # Verificar itens obrigatórios
        itens_obrigatorios = [
            "dispositivos_seguranca",
            "sinalizacao",
            "treinamento_operador"
        ]
        
        for item in itens_obrigatorios:
            if not checklist_data.get(item, False):
                resultado["conforme"] = False
                resultado["bloqueios"].append(f"Item obrigatório não conforme: {item}")
        
        return resultado

# Classe principal para facilitar o uso
class MandacaruBot:
    """Classe principal que combina todas as funcionalidades"""
    
    def __init__(self):
        self.api = MandacaruAPI()
        self.notificacao = NotificacaoMandacaru()
        self.utils = UtilsMandacaru()
    
    async def autenticar_operador(self, nome: str, data_nascimento: str) -> Optional[Dict[str, Any]]:
        """
        Processo completo de autenticação do operador
        """
        try:
            # Buscar operador
            operadores = await self.api.buscar_operador_completo(nome)
            if not operadores:
                return None
            
            operador = operadores[0]
            
            # Validar data de nascimento
            from core.db import validar_data_nascimento
            if await validar_data_nascimento(operador["id"], data_nascimento):
                # Carregar informações adicionais
                operador["veiculos"] = await self.api.obter_veiculos_operador(operador["id"])
                operador["checklists_pendentes"] = await self.api.obter_checklists_pendentes(operador["id"])
                return operador
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return None