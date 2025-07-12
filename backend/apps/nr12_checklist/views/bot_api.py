
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from datetime import date, datetime
import json

class EquipamentoAcessoView(View):
    """API para acesso ao equipamento via QR Code escaneado pelo bot"""
    
    def get(self, request, equipamento_id):
        try:
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12
            
            equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)
            
            # Verificar se existe checklist para hoje
            hoje = date.today()
            checklist_hoje = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=hoje
            ).first()
            
            # Informações do equipamento
            dados_equipamento = {
                'id': equipamento.id,
                'nome': equipamento.nome,
                'codigo': getattr(equipamento, 'codigo', 'N/A'),
                'tipo': getattr(equipamento.tipo_nr12, 'nome', 'N/A') if hasattr(equipamento, 'tipo_nr12') and equipamento.tipo_nr12 else 'N/A',
                'horimetro_atual': getattr(equipamento, 'horimetro_atual', 0),
                'status_operacional': getattr(equipamento, 'status_operacional', 'ATIVO'),
            }
            
            # Informações do checklist
            checklist_info = None
            if checklist_hoje:
                checklist_info = {
                    'id': checklist_hoje.id,
                    'uuid': str(checklist_hoje.uuid),
                    'status': checklist_hoje.status,
                    'turno': checklist_hoje.turno,
                    'data': checklist_hoje.data_checklist,
                    'responsavel': checklist_hoje.responsavel.first_name if checklist_hoje.responsavel else None,
                    'total_itens': checklist_hoje.itens.count(),
                    'itens_pendentes': checklist_hoje.itens.filter(status='PENDENTE').count(),
                    'itens_ok': checklist_hoje.itens.filter(status='OK').count(),
                    'itens_nok': checklist_hoje.itens.filter(status='NOK').count(),
                    'percentual_conclusao': checklist_hoje.percentual_conclusao,
                }
            
            # Ações disponíveis
            acoes_disponiveis = [
                'atualizar_horimetro',
                'registrar_abastecimento',
                'registrar_anomalia',
                'consultar_relatorio'
            ]
            
            if checklist_hoje:
                if checklist_hoje.status == 'PENDENTE':
                    acoes_disponiveis.append('iniciar_checklist')
                elif checklist_hoje.status == 'EM_ANDAMENTO':
                    acoes_disponiveis.append('continuar_checklist')
                    acoes_disponiveis.append('finalizar_checklist')
            else:
                acoes_disponiveis.append('criar_checklist')
            
            return JsonResponse({
                'success': True,
                'abastecimento': {
                    'id': abastecimento.id,
                    'tipo_combustivel': abastecimento.tipo_combustivel,
                    'quantidade_litros': float(abastecimento.quantidade_litros),
                    'valor_total': float(abastecimento.valor_total) if abastecimento.valor_total else None,
                    'horimetro': float(abastecimento.horimetro) if abastecimento.horimetro else None,
                    'data': abastecimento.data_abastecimento.isoformat()
                },
                'message': f'Abastecimento registrado: {abastecimento.quantidade_litros}L de {abastecimento.get_tipo_combustivel_display()}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RegistrarAnomaliaView(View):
    """API para registrar anomalia"""
    
    def post(self, request, equipamento_id):
        try:
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import Anomalia
            
            data = json.loads(request.body)
            equipamento = get_object_or_404(Equipamento, id=equipamento_id)
            
            anomalia = Anomalia.objects.create(
                equipamento=equipamento,
                tipo=data.get('tipo', 'OUTRAS'),
                severidade=data.get('severidade', 'MEDIA'),
                titulo=data.get('titulo', ''),
                descricao=data.get('descricao', ''),
                componente_afetado=data.get('componente_afetado', ''),
                horimetro_deteccao=float(data.get('horimetro_deteccao', 0)) if data.get('horimetro_deteccao') else None,
                identificado_por=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({
                'success': True,
                'anomalia': {
                    'numero_anomalia': anomalia.numero_anomalia,
                    'tipo': anomalia.tipo,
                    'severidade': anomalia.severidade,
                    'titulo': anomalia.titulo,
                    'status': anomalia.status,
                    'data_identificacao': anomalia.data_identificacao.isoformat()
                },
                'message': f'Anomalia {anomalia.numero_anomalia} registrada com severidade {anomalia.get_severidade_display()}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class RelatorioEquipamentoView(View):
    """API para consultar relatório do equipamento"""
    
    def get(self, request, equipamento_id):
        try:
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12, Abastecimento, Anomalia, HistoricoHorimetro
            from datetime import timedelta
            
            equipamento = get_object_or_404(Equipamento, id=equipamento_id)
            
            # Período para relatório (últimos 30 dias)
            data_inicio = date.today() - timedelta(days=30)
            data_fim = date.today()
            
            # Checklists no período
            checklists = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist__range=[data_inicio, data_fim]
            ).order_by('-data_checklist')
            
            # Abastecimentos no período
            abastecimentos = Abastecimento.objects.filter(
                equipamento=equipamento,
                data_abastecimento__date__range=[data_inicio, data_fim]
            ).order_by('-data_abastecimento')
            
            # Anomalias no período
            anomalias = Anomalia.objects.filter(
                equipamento=equipamento,
                data_identificacao__date__range=[data_inicio, data_fim]
            ).order_by('-data_identificacao')
            
            # Histórico de horímetro
            historico_horimetro = HistoricoHorimetro.objects.filter(
                equipamento=equipamento,
                data_registro__date__range=[data_inicio, data_fim]
            ).order_by('-data_registro')[:10]
            
            # Estatísticas
            stats = {
                'checklists': {
                    'total': checklists.count(),
                    'concluidos': checklists.filter(status='CONCLUIDO').count(),
                    'com_problemas': checklists.filter(necessita_manutencao=True).count(),
                    'taxa_conclusao': 0
                },
                'abastecimentos': {
                    'total': abastecimentos.count(),
                    'total_litros': sum(float(a.quantidade_litros) for a in abastecimentos),
                    'total_valor': sum(float(a.valor_total) for a in abastecimentos if a.valor_total),
                },
                'anomalias': {
                    'total': anomalias.count(),
                    'abertas': anomalias.filter(status__in=['ABERTA', 'EM_ANALISE', 'EM_REPARO']).count(),
                    'criticas': anomalias.filter(severidade='CRITICA').count(),
                },
                'horimetro': {
                    'atual': getattr(equipamento, 'horimetro_atual', 0),
                    'horas_trabalhadas_periodo': sum(float(h.horas_trabalhadas) for h in historico_horimetro),
                }
            }
            
            if stats['checklists']['total'] > 0:
                stats['checklists']['taxa_conclusao'] = (
                    stats['checklists']['concluidos'] / stats['checklists']['total']
                ) * 100
            
            return JsonResponse({
                'success': True,
                'equipamento': {
                    'id': equipamento.id,
                    'nome': equipamento.nome,
                    'codigo': getattr(equipamento, 'codigo', 'N/A'),
                    'tipo': getattr(equipamento.tipo_nr12, 'nome', 'N/A') if hasattr(equipamento, 'tipo_nr12') and equipamento.tipo_nr12 else 'N/A',
                },
                'periodo': {
                    'inicio': data_inicio.isoformat(),
                    'fim': data_fim.isoformat()
                },
                'estatisticas': stats,
                'resumo': {
                    'checklists_recentes': [
                        {
                            'data': c.data_checklist.isoformat(),
                            'turno': c.turno,
                            'status': c.status,
                            'problemas': c.necessita_manutencao
                        } for c in checklists[:5]
                    ],
                    'abastecimentos_recentes': [
                        {
                            'data': a.data_abastecimento.isoformat(),
                            'quantidade': float(a.quantidade_litros),
                            'tipo': a.tipo_combustivel,
                            'valor': float(a.valor_total) if a.valor_total else None
                        } for a in abastecimentos[:5]
                    ],
                    'anomalias_recentes': [
                        {
                            'numero': an.numero_anomalia,
                            'titulo': an.titulo,
                            'severidade': an.severidade,
                            'status': an.status,
                            'data': an.data_identificacao.isoformat()
                        } for an in anomalias[:5]
                    ]
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
