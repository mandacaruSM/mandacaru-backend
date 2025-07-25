# backend/apps/nr12_checklist/bot_views/bot_telegram.py

import json
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.utils import timezone

from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado

@csrf_exempt
@require_http_methods(["POST"])
def operador_login_qr(request):
    """
    POST /api/nr12/bot/operador/login/
    Body: { "qr_code": "...", "chat_id": "123456789" }
    """
    try:
        data = json.loads(request.body or "{}")
        qr_code = data.get('qr_code')
        chat_id = data.get('chat_id')

        if not qr_code:
            return JsonResponse({'success': False, 'error': 'QR code é obrigatório'}, status=400)

        operador = Operador.verificar_qr_code(qr_code)
        if not operador:
            return JsonResponse({'success': False, 'error': 'QR code inválido ou operador não autorizado'}, status=404)

        operador.atualizar_ultimo_acesso(chat_id)
        resumo = operador.get_resumo_para_bot()

        return JsonResponse({
            'success': True,
            'operador': resumo,
            'message': f"Bem-vindo, {operador.nome}!"
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {e}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EquipamentoAcessoBotView(View):
    """
    GET  /api/nr12/bot/equipamento/<id>/?operador_codigo=...
    POST /api/nr12/bot/equipamento/<id>/
    """

    def get(self, request, equipamento_id):
        try:
            equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)
            operador_codigo = request.GET.get('operador_codigo')

            # Verifica permissão de acesso
            if operador_codigo:
                if not equipamento.pode_ser_acessado_por_operador(operador_codigo):
                    return JsonResponse({'success': False, 'error': 'Acesso negado'}, status=403)

            # Lista todos os checklists de hoje
            hoje = date.today()
            checklists_qs = ChecklistNR12.objects.filter(equipamento=equipamento, data_checklist=hoje)
            checklists_hoje = list(checklists_qs)

            # Define ações possíveis
            acoes = []
            if not checklists_hoje:
                acoes.append('criar_checklist')
            else:
                primeiro = checklists_hoje[0]
                if primeiro.status == 'PENDENTE':
                    acoes.append('iniciar_checklist')
                elif primeiro.status == 'EM_ANDAMENTO':
                    acoes += ['continuar_checklist', 'finalizar_checklist']

            # Ações sempre disponíveis
            acoes += ['registrar_abastecimento', 'reportar_anomalia', 'consultar_relatorio']

            # Monta resposta
            equipamento_info = {
                'id': equipamento.id,
                'codigo': equipamento.codigo,
                'nome': equipamento.nome,
                'categoria': getattr(equipamento.categoria, 'nome', None),
                'status_operacional': getattr(equipamento, 'status_operacional', None),
                'horimetro_atual': float(equipamento.horimetro_atual or 0),
                'cliente': equipamento.cliente.razao_social,
            }
            checklists_info = []
            for c in checklists_hoje:
                checklists_info.append({
                    'id': c.id,
                    'uuid': str(c.uuid),
                    'turno': c.turno,
                    'status': c.status,
                    'frequencia': c.frequencia,
                    'responsavel': getattr(c.responsavel, 'first_name', None),
                    'percentual_conclusao': c.percentual_conclusao,
                })

            return JsonResponse({
                'success': True,
                'equipamento': equipamento_info,
                'checklists_hoje': checklists_info,
                'acoes_disponiveis': acoes,
                'precisa_criar': not bool(checklists_hoje),
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro interno: {e}'}, status=500)

    def post(self, request, equipamento_id):
        try:
            data = json.loads(request.body or "{}")
            acao = data.get('acao')
            operador_codigo = data.get('operador_codigo')

            equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)

            operador = None
            if operador_codigo:
                operador = Operador.objects.filter(codigo=operador_codigo, status='ATIVO', ativo_bot=True).first()
                if not operador:
                    return JsonResponse({'success': False, 'error': 'Operador não autorizado'}, status=403)

            # Dispatcheia para método específico
            if acao == 'criar_checklist':
                return self._criar_checklist(equipamento, operador, data)
            elif acao == 'iniciar_checklist':
                return self._iniciar_checklist(equipamento, operador, data)
            elif acao == 'continuar_checklist':
                return self._continuar_checklist(equipamento, operador)
            elif acao == 'finalizar_checklist':
                return self._finalizar_checklist(equipamento, operador)
            else:
                return JsonResponse({'success': False, 'error': f'Ação "{acao}" desconhecida'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro interno: {e}'}, status=500)

    def _criar_checklist(self, equipamento, operador, data):
        hoje = date.today()
        turno = data.get('turno', 'MANHA')
        frequencia = data.get('frequencia', 'DIARIA')

        if ChecklistNR12.objects.filter(equipamento=equipamento, data_checklist=hoje, turno=turno).exists():
            return JsonResponse({'success': False, 'error': f'Checklist já existe para hoje ({turno})'}, status=400)

        checklist = ChecklistNR12.objects.create(
            equipamento=equipamento,
            data_checklist=hoje,
            turno=turno,
            frequencia=frequencia,
            status='PENDENTE'
        )
        return JsonResponse({
            'success': True,
            'checklist': {
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'turno': checklist.turno,
                'status': checklist.status,
            },
            'proxima_acao': 'iniciar_checklist'
        })

    def _iniciar_checklist(self, equipamento, operador, data):
        hoje = date.today()
        checklist = ChecklistNR12.objects.filter(
            equipamento=equipamento, data_checklist=hoje, status='PENDENTE'
        ).first()

        if not checklist:
            return JsonResponse({'success': False, 'error': 'Nenhum checklist pendente encontrado'}, status=404)

        if operador and not operador.pode_iniciar_checklist(checklist.id):
            return JsonResponse({'success': False, 'error': 'Sem permissão para iniciar'}, status=403)

        checklist.iniciar_checklist(usuario=operador.user if operador else None)
        return JsonResponse({
            'success': True,
            'checklist': {
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'status': checklist.status,
                'data_inicio': checklist.data_inicio.isoformat() if checklist.data_inicio else None,
            },
            'proxima_acao': 'continuar_checklist'
        })

    def _continuar_checklist(self, equipamento, operador):
        hoje = date.today()
        checklist = ChecklistNR12.objects.filter(
            equipamento=equipamento, data_checklist=hoje, status='EM_ANDAMENTO'
        ).first()

        if not checklist:
            return JsonResponse({'success': False, 'error': 'Nenhum checklist em andamento'}, status=404)

        itens = checklist.itens.select_related('item_padrao').order_by('item_padrao__ordem')
        payload = [{
            'id': i.id,
            'item': i.item_padrao.item,
            'status': i.status,
        } for i in itens]

        return JsonResponse({
            'success': True,
            'itens': payload,
            'percentual_conclusao': checklist.percentual_conclusao
        })

    def _finalizar_checklist(self, equipamento, operador):
        hoje = date.today()
        checklist = ChecklistNR12.objects.filter(
            equipamento=equipamento, data_checklist=hoje, status='EM_ANDAMENTO'
        ).first()

        if not checklist:
            return JsonResponse({'success': False, 'error': 'Nenhum checklist em andamento'}, status=404)

        pendentes = checklist.itens.filter(status='PENDENTE').count()
        if pendentes:
            return JsonResponse({
                'success': False,
                'error': f'Existem {pendentes} itens pendentes'
            }, status=400)

        checklist.finalizar_checklist()
        return JsonResponse({
            'success': True,
            'status': checklist.status,
            'percentual_conclusao': checklist.percentual_conclusao,
        })


@csrf_exempt
@require_http_methods(["POST"])
def atualizar_item_checklist(request):
    """
    POST /api/nr12/bot/item-checklist/atualizar/
    Body: { "item_id": 1, "status": "OK|NOK|NA", "observacao": "...", "operador_codigo": "OP001" }
    """
    try:
        data = json.loads(request.body or "{}")
        item_id = data.get('item_id')
        status = data.get('status')
        observacao = data.get('observacao', '')
        operador_codigo = data.get('operador_codigo')

        if not item_id or status not in ['OK','NOK','NA']:
            return JsonResponse({'success': False, 'error': 'Campos inválidos'}, status=400)

        item = get_object_or_404(ItemChecklistRealizado, id=item_id)
        if item.checklist.status != 'EM_ANDAMENTO':
            return JsonResponse({'success': False, 'error': 'Checklist não está em andamento'}, status=400)

        operador = None
        if operador_codigo:
            operador = Operador.objects.filter(codigo=operador_codigo, status='ATIVO', ativo_bot=True).first()

        item.status = status
        item.observacao = observacao
        item.verificado_em = timezone.now()
        if operador:
            item.verificado_por = operador.user
        item.save()

        return JsonResponse({
            'success': True,
            'percentual_conclusao': item.checklist.percentual_conclusao
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
