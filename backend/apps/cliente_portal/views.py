# 1. ATUALIZAR backend/apps/cliente_portal/views.py
# ================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404

from backend.apps.equipamentos.models import Equipamento
from backend.apps.equipamentos.serializers import EquipamentoSerializer
from backend.apps.empreendimentos.models import Empreendimento
from backend.apps.manutencao.models import HistoricoManutencao
from backend.apps.nr12_checklist.models import ChecklistNR12, AlertaManutencao

class ClientePortalPermissionMixin:
    """Garante que cliente só acesse seus próprios dados"""
    
    def get_cliente(self):
        if hasattr(self.request.user, 'cliente') and self.request.user.cliente:
            return self.request.user.cliente
        return None

    def filter_by_cliente(self, queryset):
        cliente = self.get_cliente()
        if cliente:
            return queryset.filter(cliente=cliente)
        return queryset.none()

class DashboardClienteViewSet(ClientePortalPermissionMixin, viewsets.ViewSet):
    """Dashboard principal do cliente"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def resumo(self, request):
        """Resumo geral para dashboard"""
        # Para teste, vamos mostrar dados de todos os clientes
        # Em produção, usar apenas: cliente = self.get_cliente()
        
        hoje = date.today()
        
        # Estatísticas básicas - mostrando todos os dados para teste
        total_equipamentos = Equipamento.objects.count()
        equipamentos_ativos_nr12 = Equipamento.objects.filter(ativo_nr12=True).count()
        
        # Checklists pendentes hoje
        checklists_pendentes = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).count()
        
        # Alertas ativos
        alertas_ativos = AlertaManutencao.objects.filter(
            status__in=['ATIVO', 'NOTIFICADO']
        ).count()
        
        # Alertas críticos (vencimento < 7 dias)
        alertas_criticos = AlertaManutencao.objects.filter(
            status__in=['ATIVO', 'NOTIFICADO'],
            data_prevista__lte=hoje + timedelta(days=7)
        ).count()

        # Últimas manutenções
        ultimas_manutencoes = HistoricoManutencao.objects.order_by('-data')[:5]

        manutencoes_data = []
        for m in ultimas_manutencoes:
            manutencoes_data.append({
                'equipamento': m.equipamento.nome,
                'data': m.data,
                'tipo': m.tipo,
                'tecnico': m.tecnico_responsavel
            })

        # Lista de equipamentos
        equipamentos = Equipamento.objects.all()[:10]  # Primeiros 10
        equipamentos_data = []
        for eq in equipamentos:
            # Status do checklist de hoje
            checklist_hoje = ChecklistNR12.objects.filter(
                equipamento=eq,
                data_checklist=hoje
            ).first()
            
            equipamentos_data.append({
                'id': eq.id,
                'nome': eq.nome,
                'tipo': eq.tipo,
                'marca': eq.marca,
                'modelo': eq.modelo,
                'cliente': eq.cliente.razao_social,
                'empreendimento': eq.empreendimento.nome,
                'ativo_nr12': eq.ativo_nr12,
                'checklist_hoje': {
                    'existe': checklist_hoje is not None,
                    'status': checklist_hoje.status if checklist_hoje else 'PENDENTE',
                    'uuid': str(checklist_hoje.uuid) if checklist_hoje else None
                }
            })

        return Response({
            'estatisticas': {
                'total_equipamentos': total_equipamentos,
                'equipamentos_ativos_nr12': equipamentos_ativos_nr12,
                'checklists_pendentes_hoje': checklists_pendentes,
                'alertas_ativos': alertas_ativos,
                'alertas_criticos': alertas_criticos
            },
            'ultimas_manutencoes': manutencoes_data,
            'equipamentos_recentes': equipamentos_data,
            'data_atual': hoje
        })

    @action(detail=False, methods=['post'])
    def gerar_checklist_teste(self, request):
        """Gera um checklist de teste para demonstração"""
        hoje = date.today()
        
        # Pegar primeiro equipamento
        equipamento = Equipamento.objects.first()
        if not equipamento:
            return Response({'error': 'Nenhum equipamento encontrado'}, status=400)
        
        # Verificar se já existe checklist para hoje
        checklist_existente = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            data_checklist=hoje
        ).first()
        
        if checklist_existente:
            return Response({
                'message': 'Checklist já existe para hoje',
                'checklist_id': checklist_existente.id,
                'uuid': str(checklist_existente.uuid)
            })
        
        # Criar novo checklist
        checklist = ChecklistNR12.objects.create(
            equipamento=equipamento,
            data_checklist=hoje,
            turno='MANHA'
        )
        
        return Response({
            'message': 'Checklist de teste criado com sucesso!',
            'checklist_id': checklist.id,
            'uuid': str(checklist.uuid),
            'qr_code_url': f"/api/nr12/checklist/{checklist.uuid}/",
            'equipamento': equipamento.nome
        })

class EquipamentoClienteViewSet(ClientePortalPermissionMixin, viewsets.ReadOnlyModelViewSet):
    """Equipamentos do cliente"""
    serializer_class = EquipamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Para teste, mostrar todos os equipamentos
        # Em produção: return self.filter_by_cliente(Equipamento.objects.all())
        return Equipamento.objects.all()

    @action(detail=True, methods=['get'])
    def status_checklist(self, request, pk=None):
        """Status atual do checklist do equipamento"""
        equipamento = self.get_object()
        hoje = date.today()
        
        # Checklist de hoje
        checklist_hoje = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            data_checklist=hoje
        ).first()
        
        # Último checklist concluído
        ultimo_checklist = ChecklistNR12.objects.filter(
            equipamento=equipamento,
            status='CONCLUIDO'
        ).order_by('-data_checklist').first()
        
        # Alertas pendentes
        alertas = AlertaManutencao.objects.filter(
            equipamento=equipamento,
            status__in=['ATIVO', 'NOTIFICADO']
        ).order_by('-criticidade', 'data_prevista')
        
        alertas_data = []
        for alerta in alertas:
            dias_restantes = (alerta.data_prevista - hoje).days
            alertas_data.append({
                'id': alerta.id,
                'tipo': alerta.tipo,
                'titulo': alerta.titulo,
                'criticidade': alerta.criticidade,
                'dias_restantes': dias_restantes,
                'urgente': dias_restantes <= 3
            })
        
        return Response({
            'equipamento': {
                'id': equipamento.id,
                'nome': equipamento.nome,
                'marca': equipamento.marca,
                'modelo': equipamento.modelo,
                'cliente': equipamento.cliente.razao_social,
                'empreendimento': equipamento.empreendimento.nome
            },
            'checklist_hoje': {
                'existe': checklist_hoje is not None,
                'status': checklist_hoje.status if checklist_hoje else None,
                'uuid': str(checklist_hoje.uuid) if checklist_hoje else None,
                'pendente': checklist_hoje.status == 'PENDENTE' if checklist_hoje else True,
                'qr_code_url': f"/api/nr12/checklist/{checklist_hoje.uuid}/" if checklist_hoje else None
            },
            'ultimo_checklist': {
                'data': ultimo_checklist.data_checklist if ultimo_checklist else None,
                'status': ultimo_checklist.status if ultimo_checklist else None
            },
            'alertas': alertas_data,
            'total_alertas': len(alertas_data),
            'alertas_urgentes': len([a for a in alertas_data if a['urgente']])
        })
