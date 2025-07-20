from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
import json


class EquipamentoAcessoView(View):
    def get(self, request, equipamento_id):
        try:
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12

            equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)
            hoje = date.today()
            checklist_hoje = ChecklistNR12.objects.filter(equipamento=equipamento, data_checklist=hoje).first()

            dados_equipamento = {
                'id': equipamento.id,
                'nome': equipamento.nome,
                'codigo': getattr(equipamento, 'codigo', 'N/A'),
                'tipo': getattr(equipamento.tipo_nr12, 'nome', 'N/A') if equipamento.tipo_nr12 else 'N/A',
                'horimetro_atual': getattr(equipamento, 'horimetro_atual', 0),
                'status_operacional': getattr(equipamento, 'status_operacional', 'ATIVO'),
            }

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

            acoes_disponiveis = ['atualizar_horimetro', 'registrar_abastecimento', 'registrar_anomalia', 'consultar_relatorio']
            if checklist_hoje:
                if checklist_hoje.status == 'PENDENTE':
                    acoes_disponiveis.append('iniciar_checklist')
                elif checklist_hoje.status == 'EM_ANDAMENTO':
                    acoes_disponiveis.extend(['continuar_checklist', 'finalizar_checklist'])
            else:
                acoes_disponiveis.append('criar_checklist')

            return JsonResponse({
                'success': True,
                'equipamento': dados_equipamento,
                'checklist': checklist_info,
                'acoes_disponiveis': acoes_disponiveis
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RegistrarAnomaliaView(View):
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
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class RelatorioEquipamentoView(View):
    def get(self, request, equipamento_id):
        try:
            from backend.apps.equipamentos.models import Equipamento
            from backend.apps.nr12_checklist.models import ChecklistNR12, Abastecimento, Anomalia, HistoricoHorimetro

            equipamento = get_object_or_404(Equipamento, id=equipamento_id)
            data_inicio = date.today() - timedelta(days=30)
            data_fim = date.today()

            checklists = ChecklistNR12.objects.filter(equipamento=equipamento, data_checklist__range=[data_inicio, data_fim])
            abastecimentos = Abastecimento.objects.filter(equipamento=equipamento, data_abastecimento__date__range=[data_inicio, data_fim])
            anomalias = Anomalia.objects.filter(equipamento=equipamento, data_identificacao__date__range=[data_inicio, data_fim])
            historico_horimetro = HistoricoHorimetro.objects.filter(equipamento=equipamento, data_registro__date__range=[data_inicio, data_fim])[:10]

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
                    'tipo': getattr(equipamento.tipo_nr12, 'nome', 'N/A') if equipamento.tipo_nr12 else 'N/A',
                },
                'periodo': {
                    'inicio': data_inicio.isoformat(),
                    'fim': data_fim.isoformat()
                },
                'estatisticas': stats
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
