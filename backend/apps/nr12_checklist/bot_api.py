import json
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import get_object_or_404

from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado

@csrf_exempt
def equipamento_api(request, equipamento_id):
    """
    GET  -> retorna lista de ações disponíveis para hoje
    POST -> recebe JSON { action: str, ... } e executa:
      - criar_checklist
      - iniciar_checklist
      - continuar_checklist
      - marcar_item (item_id, status, [photo])
      - finalizar_checklist
    """
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    hoje = timezone.now().date()
    checklist = ChecklistNR12.objects.filter(
        equipamento=equipamento,
        data_checklist=hoje
    ).first()

    if request.method == 'GET':
        if not checklist:
            acoes = ['criar_checklist']
        elif checklist.status == 'PENDENTE':
            acoes = ['iniciar_checklist']
        elif checklist.status == 'EM_ANDAMENTO':
            acoes = ['continuar_checklist', 'finalizar_checklist']
        else:
            acoes = []
        return JsonResponse({'actions': acoes})

    # POST
    data = json.loads(request.body or '{}')
    action = data.get('action')

    # 1) criar_checklist
    if action == 'criar_checklist':
        freq = data.get('frequencia', 'DIARIA')
        ChecklistNR12.objects.create(
            equipamento=equipamento,
            data_checklist=hoje,
            turno='MANHA',
            status='PENDENTE',
            frequencia=freq
        )
        return JsonResponse({'message': 'Checklist criado', 'next': ['iniciar_checklist']})

    if not checklist:
        return JsonResponse({'error': 'Nenhum checklist encontrado'}, status=400)

    # 2) iniciar_checklist
    if action == 'iniciar_checklist':
        checklist.status = 'EM_ANDAMENTO'
        checklist.save()
        return JsonResponse({'message': 'Checklist iniciado', 'next': ['continuar_checklist', 'finalizar_checklist']})

    # 3) continuar_checklist
    if action == 'continuar_checklist':
        itens = checklist.itemchecklistrealizado_set.all().order_by('item_padrao__ordem')
        resposta = [
            {'id': i.id, 'descricao': i.item_padrao.item, 'status': i.status}
            for i in itens
        ]
        return JsonResponse({'items': resposta})

    # 4) marcar_item
    if action == 'marcar_item':
        item_id = data.get('item_id')
        status = data.get('status')
        photo = data.get('photo')  # se vier base64 ou URL
        item = get_object_or_404(ItemChecklistRealizado, id=item_id)
        item.status = status
        item.verificado_em = timezone.now()
        if status == 'NOK' and photo:
            item.foto_antes = photo  # ou foto_depois
        item.save()
        return JsonResponse({'message': 'Item atualizado', 'item': {'id': item.id, 'status': item.status}})

    # 5) finalizar_checklist
    if action == 'finalizar_checklist':
        pendentes = checklist.itemchecklistrealizado_set.filter(status='PENDENTE')
        if pendentes.exists():
            return JsonResponse({'error': 'Existem itens pendentes'}, status=400)

        # opcional: itens NA → OK
        checklist.itemchecklistrealizado_set.filter(status='NA').update(status='OK')

        checklist.status = 'CONCLUIDO'
        checklist.data_hora_finalizacao = timezone.now()
        checklist.save()
        return JsonResponse({'message': 'Checklist finalizado'})

    return JsonResponse({'error': 'Ação inválida'}, status=400)
