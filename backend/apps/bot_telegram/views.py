# backend/apps/bot_telegram/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
import json
import logging
from datetime import datetime
from django.utils import timezone

# ✅ IMPORTS CORRIGIDOS
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import (
    ChecklistNR12, 
    ItemChecklistPadrao, 
    ItemChecklistRealizado,
    AlertaManutencao
)

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def qr_code_endpoint(request, uuid_checklist):
    """
    GET /qr/{uuid} - Endpoint que o QR Code chama
    Usa o UUID do checklist para retornar dados
    """
    try:
        logger.info(f"📱 QR Code acessado: {uuid_checklist}")
        
        # Buscar checklist pelo UUID
        try:
            checklist = ChecklistNR12.objects.get(uuid=uuid_checklist)
        except ChecklistNR12.DoesNotExist:
            logger.warning(f"❌ Checklist não encontrado: {uuid_checklist}")
            return JsonResponse({
                'error': 'Checklist não encontrado',
                'uuid': uuid_checklist
            }, status=404)
        
        # Verificar se checklist está pendente ou em andamento
        if checklist.status not in ['PENDENTE', 'EM_ANDAMENTO']:
            return JsonResponse({
                'error': f'Checklist já está {checklist.status.lower()}',
                'status': checklist.status
            }, status=400)
        
        # Buscar itens padrão do tipo de equipamento
        if not hasattr(checklist.equipamento, 'tipo_nr12') or not checklist.equipamento.tipo_nr12:
            return JsonResponse({
                'error': 'Equipamento não possui tipo NR12 configurado',
                'equipment': checklist.equipamento.nome
            }, status=404)
        
        itens_padrao = ItemChecklistPadrao.objects.filter(
            tipo_equipamento=checklist.equipamento.tipo_nr12,
            ativo=True
        ).order_by('ordem')
        
        if not itens_padrao.exists():
            return JsonResponse({
                'error': 'Não há itens de checklist configurados para este tipo de equipamento',
                'equipment_type': checklist.equipamento.tipo_nr12.nome
            }, status=404)
        
        # Montar estrutura para o bot
        items_data = []
        for item in itens_padrao:
            items_data.append({
                'description': f"{item.item} - {item.descricao}" if item.descricao else item.item,
                'reference_image': None  # Adicione se tiver campo de imagem
            })
        
        response_data = {
            'equipment': {
                'id': checklist.equipamento.id,
                'name': checklist.equipamento.nome,
                'code': getattr(checklist.equipamento, 'codigo', str(checklist.equipamento.id)),
                'location': getattr(checklist.equipamento, 'localizacao', 'Não informado')
            },
            'checklist': {
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'name': f"Checklist NR12 - {checklist.data_checklist} - {checklist.turno}",
                'items': items_data
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Dados enviados - Equipamento: {checklist.equipamento.nome}, Itens: {len(items_data)}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint QR: {str(e)}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ChecklistSubmitView(View):
    """
    POST /api/checklist/submit - Recebe dados do checklist do bot
    """
    
    def post(self, request):
        try:
            # Parse do JSON
            dados = json.loads(request.body)
            
            logger.info(f"📊 Checklist recebido do bot: {dados.get('checklist', {}).get('uuid', 'N/A')}")
            
            # Validar dados obrigatórios
            checklist_uuid = dados.get('checklist', {}).get('uuid')
            if not checklist_uuid:
                return JsonResponse({
                    'error': 'UUID do checklist não fornecido',
                    'required': 'checklist.uuid'
                }, status=400)
            
            # Buscar checklist
            try:
                checklist = ChecklistNR12.objects.get(uuid=checklist_uuid)
            except ChecklistNR12.DoesNotExist:
                return JsonResponse({
                    'error': 'Checklist não encontrado',
                    'uuid': checklist_uuid
                }, status=404)
            
            # Iniciar checklist se estiver pendente
            if checklist.status == 'PENDENTE':
                checklist.status = 'EM_ANDAMENTO'
                checklist.data_inicio = timezone.now()
                checklist.save()
                
                # Criar itens baseados no padrão
                itens_padrao = ItemChecklistPadrao.objects.filter(
                    tipo_equipamento=checklist.equipamento.tipo_nr12,
                    ativo=True
                ).order_by('ordem')
                
                for item_padrao in itens_padrao:
                    ItemChecklistRealizado.objects.get_or_create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        defaults={'status': 'PENDENTE'}
                    )
            
            # Processar respostas
            respostas_processadas = 0
            fotos_processadas = 0
            alertas_criados = 0
            
            if dados.get('responses'):
                for i, response in enumerate(dados['responses']):
                    try:
                        # Buscar item correspondente
                        item_realizado = ItemChecklistRealizado.objects.filter(
                            checklist=checklist
                        ).order_by('item_padrao__ordem')[i]
                        
                        # Mapear status
                        status_map = {
                            'ok': 'OK',
                            'nok': 'NOK', 
                            'skip': 'NA'
                        }
                        
                        status_django = status_map.get(response['status'], 'PENDENTE')
                        
                        # Atualizar item
                        item_realizado.status = status_django
                        item_realizado.verificado_em = timezone.now()
                        item_realizado.save()
                        
                        respostas_processadas += 1
                        
                        # Criar alerta se NOK e criticidade alta
                        if status_django == 'NOK' and item_realizado.item_padrao.criticidade in ['ALTA', 'CRITICA']:
                            AlertaManutencao.objects.create(
                                equipamento=checklist.equipamento,
                                tipo='CORRETIVA',
                                titulo=f"Item não conforme: {item_realizado.item_padrao.item}",
                                descricao=f"Item '{item_realizado.item_padrao.item}' marcado como não conforme no checklist via bot.",
                                criticidade=item_realizado.item_padrao.criticidade,
                                data_prevista=timezone.now().date(),
                                checklist_origem=checklist
                            )
                            alertas_criados += 1
                        
                    except IndexError:
                        logger.warning(f"Item {i} não encontrado no checklist")
                        continue
                    except Exception as e:
                        logger.error(f"Erro ao processar resposta {i}: {str(e)}")
                        continue
            
            # Processar fotos (salvar base64 como observação por enquanto)
            if dados.get('photos'):
                for photo in dados['photos']:
                    try:
                        item_index = photo.get('item_index', 0)
                        item_realizado = ItemChecklistRealizado.objects.filter(
                            checklist=checklist
                        ).order_by('item_padrao__ordem')[item_index]
                        
                        # Adicionar foto como observação (você pode melhorar isso depois)
                        observacao_foto = f"Foto capturada via bot - {photo.get('caption', 'Sem legenda')}"
                        if item_realizado.observacao:
                            item_realizado.observacao += f"\n{observacao_foto}"
                        else:
                            item_realizado.observacao = observacao_foto
                        
                        item_realizado.save()
                        fotos_processadas += 1
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar foto: {str(e)}")
                        continue
            
            # Finalizar checklist
            checklist.status = 'CONCLUIDO'
            checklist.data_conclusao = timezone.now()
            
            # Verificar se necessita manutenção
            itens_nok = checklist.itens.filter(status='NOK').count()
            checklist.necessita_manutencao = itens_nok > 0
            
            # Adicionar observações se houver
            if dados.get('observations'):
                checklist.observacoes = dados['observations']
            
            checklist.save()
            
            logger.info(f"✅ Checklist finalizado - ID: {checklist.id}, Respostas: {respostas_processadas}, Fotos: {fotos_processadas}")
            
            # Resposta para o bot
            return JsonResponse({
                'success': True,
                'checklist_id': checklist.id,
                'message': 'Checklist salvo com sucesso!',
                'statistics': {
                    'total_items': respostas_processadas,
                    'ok_items': checklist.itens.filter(status='OK').count(),
                    'nok_items': checklist.itens.filter(status='NOK').count(),
                    'skipped_items': checklist.itens.filter(status='NA').count()
                },
                'alerts_created': alertas_criados,
                'photos_processed': fotos_processadas,
                'needs_maintenance': checklist.necessita_manutencao
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'JSON inválido'
            }, status=400)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar checklist: {str(e)}")
            return JsonResponse({
                'error': 'Erro ao salvar checklist',
                'message': str(e)
            }, status=500)


@require_http_methods(["GET"])
def checklist_list(request):
    """
    GET /api/checklist - Listar checklists executados
    """
    try:
        # Filtros opcionais
        equipment_id = request.GET.get('equipment_id')
        date = request.GET.get('date')
        status = request.GET.get('status')
        
        checklists = ChecklistNR12.objects.select_related('equipamento').prefetch_related('itens')
        
        if equipment_id:
            checklists = checklists.filter(equipamento_id=equipment_id)
        
        if date:
            checklists = checklists.filter(data_checklist=date)
            
        if status:
            checklists = checklists.filter(status=status)
        
        # Ordenar por mais recente
        checklists = checklists.order_by('-data_checklist', '-created_at')[:50]
        
        # Serializar dados
        dados = []
        for checklist in checklists:
            dados.append({
                'id': checklist.id,
                'uuid': str(checklist.uuid),
                'equipment': {
                    'id': checklist.equipamento.id,
                    'name': checklist.equipamento.nome,
                    'code': getattr(checklist.equipamento, 'codigo', str(checklist.equipamento.id))
                },
                'data_checklist': checklist.data_checklist.isoformat(),
                'turno': checklist.turno,
                'status': checklist.status,
                'percentual_conclusao': checklist.percentual_conclusao,
                'necessita_manutencao': checklist.necessita_manutencao,
                'statistics': {
                    'total_items': checklist.itens.count(),
                    'ok_items': checklist.itens.filter(status='OK').count(),
                    'nok_items': checklist.itens.filter(status='NOK').count(),
                    'na_items': checklist.itens.filter(status='NA').count(),
                    'pending_items': checklist.itens.filter(status='PENDENTE').count()
                },
                'data_inicio': checklist.data_inicio.isoformat() if checklist.data_inicio else None,
                'data_conclusao': checklist.data_conclusao.isoformat() if checklist.data_conclusao else None,
                'created_at': checklist.created_at.isoformat()
            })
        
        return JsonResponse({
            'total': len(dados),
            'checklists': dados
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar checklists: {str(e)}")
        return JsonResponse({
            'error': 'Erro ao buscar checklists',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def checklist_detail(request, uuid_checklist):
    """
    GET /api/checklist/{uuid} - Detalhes de um checklist específico
    """
    try:
        checklist = get_object_or_404(ChecklistNR12, uuid=uuid_checklist)
        
        # Serializar itens
        itens_data = []
        for item in checklist.itens.select_related('item_padrao').order_by('item_padrao__ordem'):
            itens_data.append({
                'id': item.id,
                'item': item.item_padrao.item,
                'descricao': item.item_padrao.descricao,
                'criticidade': item.item_padrao.criticidade,
                'status': item.status,
                'observacao': item.observacao,
                'verificado_em': item.verificado_em.isoformat() if item.verificado_em else None,
                'verificado_por': item.verificado_por.first_name if item.verificado_por else None
            })
        
        dados = {
            'id': checklist.id,
            'uuid': str(checklist.uuid),
            'equipment': {
                'id': checklist.equipamento.id,
                'name': checklist.equipamento.nome,
                'code': getattr(checklist.equipamento, 'codigo', str(checklist.equipamento.id)),
                'tipo_nr12': checklist.equipamento.tipo_nr12.nome if checklist.equipamento.tipo_nr12 else None
            },
            'data_checklist': checklist.data_checklist.isoformat(),
            'turno': checklist.turno,
            'status': checklist.status,
            'horimetro_inicial': float(checklist.horimetro_inicial) if checklist.horimetro_inicial else None,
            'horimetro_final': float(checklist.horimetro_final) if checklist.horimetro_final else None,
            'observacoes': checklist.observacoes,
            'necessita_manutencao': checklist.necessita_manutencao,
            'percentual_conclusao': checklist.percentual_conclusao,
            'responsavel': checklist.responsavel.first_name if checklist.responsavel else None,
            'data_inicio': checklist.data_inicio.isoformat() if checklist.data_inicio else None,
            'data_conclusao': checklist.data_conclusao.isoformat() if checklist.data_conclusao else None,
            'itens': itens_data,
            'qr_code_url': checklist.qr_code_url
        }
        
        return JsonResponse(dados)
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar checklist: {str(e)}")
        return JsonResponse({
            'error': 'Erro ao buscar checklist',
            'message': str(e)
        }, status=500)