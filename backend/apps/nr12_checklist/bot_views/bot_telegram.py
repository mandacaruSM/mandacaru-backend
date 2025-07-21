# ================================================================
# ARQUIVO CORRIGIDO: backend/apps/nr12_checklist/bot_views/bot_telegram.py
# ================================================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
import json
from datetime import date, datetime
from django.utils import timezone

# Importações dos modelos
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistRealizado


@csrf_exempt
@require_http_methods(["POST"])
def operador_login_qr(request):
    """
    Endpoint para login de operador via QR code
    POST /api/nr12/bot/operador/login/
    
    Body: {
        "qr_code": "código_do_qr",
        "chat_id": "123456789"
    }
    """
    try:
        data = json.loads(request.body)
        qr_code = data.get('qr_code')
        chat_id = data.get('chat_id')
        
        if not qr_code:
            return JsonResponse({
                'success': False, 
                'error': 'QR code é obrigatório'
            }, status=400)
        
        # Verificar QR code do operador
        operador = Operador.verificar_qr_code(qr_code)
        
        if not operador:
            return JsonResponse({
                'success': False,
                'error': 'QR code inválido ou operador não autorizado'
            }, status=404)
        
        # Atualizar último acesso
        operador.atualizar_ultimo_acesso(chat_id)
        
        # Retornar dados do operador
        return JsonResponse({
            'success': True,
            'operador': operador.get_resumo_para_bot(),
            'message': f'Bem-vindo, {operador.nome}!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EquipamentoAcessoBotView(View):
    """
    Endpoint para acesso a equipamento via QR code
    GET/POST /api/nr12/bot/equipamento/{id}/
    """
    
    def get(self, request, equipamento_id):
        """Retorna informações do equipamento para o bot"""
        try:
            equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)
            operador_codigo = request.GET.get('operador')
            
            # Verificar se operador pode acessar
            acesso_permitido = True
            if operador_codigo:
                acesso_permitido = equipamento.pode_ser_acessado_por_operador(operador_codigo)
            
            if not acesso_permitido:
                return JsonResponse({
                    'success': False,
                    'error': 'Acesso negado a este equipamento'
                }, status=403)
            
            # Buscar checklists de hoje
            checklists_hoje = equipamento.get_checklists_hoje()
            
            # Determinar ações disponíveis
            acoes_disponiveis = []
            
            if equipamento.status_operacional in ['DISPONIVEL', 'PARADO']:
                if equipamento.precisa_checklist_hoje():
                    acoes_disponiveis.append('criar_checklist')
                
                for checklist in checklists_hoje:
                    if checklist.status == 'PENDENTE':
                        acoes_disponiveis.append('iniciar_checklist')
                        break
                    elif checklist.status == 'EM_ANDAMENTO':
                        acoes_disponiveis.extend(['continuar_checklist', 'finalizar_checklist'])
                        break
            
            # Ações sempre disponíveis
            acoes_disponiveis.extend([
                'registrar_abastecimento',
                'reportar_anomalia',
                'consultar_relatorio'
            ])
            
            return JsonResponse({
                'success': True,
                'equipamento': {
                    'id': equipamento.id,
                    'codigo': equipamento.codigo,
                    'nome': equipamento.nome,
                    'categoria': equipamento.categoria.nome,
                    'marca': equipamento.marca or 'N/A',
                    'modelo': equipamento.modelo or 'N/A',
                    'status_operacional': equipamento.status_operacional,
                    'horimetro_atual': float(equipamento.horimetro_atual),
                    'cliente': equipamento.cliente.razao_social,
                    'operador_atual': equipamento.operador_atual.nome if equipamento.operador_atual else None,
                    'localizacao_atual': equipamento.localizacao_atual or 'Não informada'
                },
                'checklists_hoje': [{
                    'id': c.id,
                    'uuid': str(c.uuid),
                    'turno': c.turno,
                    'status': c.status,
                    'frequencia': getattr(c, 'frequencia', 'DIARIA'),
                    'responsavel': c.responsavel.first_name if c.responsavel else None,
                    'percentual_conclusao': c.percentual_conclusao
                } for c in checklists_hoje],
                'acoes_disponiveis': acoes_disponiveis,
                'precisa_checklist': equipamento.precisa_checklist_hoje()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)
    
    def post(self, request, equipamento_id):
        """Executa ações no equipamento via bot"""
        try:
            data = json.loads(request.body)
            acao = data.get('acao')
            operador_codigo = data.get('operador_codigo')
            
            equipamento = get_object_or_404(Equipamento, id=equipamento_id, ativo_nr12=True)
            
            # Verificar operador
            operador = None
            if operador_codigo:
                operador = Operador.objects.filter(
                    codigo=operador_codigo, 
                    status='ATIVO', 
                    ativo_bot=True
                ).first()
                
                if not operador:
                    return JsonResponse({
                        'success': False,
                        'error': 'Operador não encontrado ou não autorizado'
                    }, status=403)
                
                if not operador.pode_operar_equipamento(equipamento):
                    return JsonResponse({
                        'success': False,
                        'error': 'Operador não autorizado para este equipamento'
                    }, status=403)
            
            # Executar ação
            if acao == 'criar_checklist':
                return self._criar_checklist(equipamento, operador, data)
            elif acao == 'iniciar_checklist':
                return self._iniciar_checklist(equipamento, operador, data)
            elif acao == 'continuar_checklist':
                return self._continuar_checklist(equipamento, operador, data)
            elif acao == 'finalizar_checklist':
                return self._finalizar_checklist(equipamento, operador, data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Ação "{acao}" não reconhecida'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)
    
    def _criar_checklist(self, equipamento, operador, data):
        """Cria novo checklist para o equipamento"""
        try:
            hoje = date.today()
            turno = data.get('turno', 'MANHA')
            frequencia = data.get('frequencia', 'DIARIA')
            
            # Verificar se já existe checklist hoje
            checklist_existente = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=hoje,
                turno=turno
            ).first()
            
            if checklist_existente:
                return JsonResponse({
                    'success': False,
                    'error': f'Já existe checklist para hoje no turno {turno}'
                }, status=400)
            
            # Criar novo checklist
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
                    'frequencia': checklist.frequencia
                },
                'message': f'Checklist criado para {equipamento.nome}',
                'proxima_acao': 'iniciar_checklist'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao criar checklist: {str(e)}'
            }, status=500)
    
    def _iniciar_checklist(self, equipamento, operador, data):
        """Inicia checklist pendente"""
        try:
            checklist_id = data.get('checklist_id')
            
            if checklist_id:
                checklist = get_object_or_404(ChecklistNR12, id=checklist_id)
            else:
                # Buscar checklist pendente de hoje
                checklist = ChecklistNR12.objects.filter(
                    equipamento=equipamento,
                    data_checklist=date.today(),
                    status='PENDENTE'
                ).first()
            
            if not checklist:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhum checklist pendente encontrado'
                }, status=404)
            
            # Verificar permissão
            if operador and not operador.pode_iniciar_checklist(checklist.id):
                return JsonResponse({
                    'success': False,
                    'error': 'Operador não autorizado a iniciar este checklist'
                }, status=403)
            
            # Iniciar checklist
            checklist.iniciar_checklist(operador.user if operador else None)
            
            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid),
                    'status': checklist.status,
                    'data_inicio': checklist.data_inicio.isoformat() if checklist.data_inicio else None,
                    'total_itens': checklist.itens.count()
                },
                'message': f'Checklist iniciado por {operador.nome if operador else "Sistema"}',
                'proxima_acao': 'continuar_checklist'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao iniciar checklist: {str(e)}'
            }, status=500)
    
    def _continuar_checklist(self, equipamento, operador, data):
        """Retorna itens do checklist para continuação"""
        try:
            checklist = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=date.today(),
                status='EM_ANDAMENTO'
            ).first()
            
            if not checklist:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhum checklist em andamento encontrado'
                }, status=404)
            
            # Buscar itens do checklist
            itens = checklist.itens.select_related('item_padrao').order_by('item_padrao__ordem')
            
            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid),
                    'status': checklist.status,
                    'percentual_conclusao': checklist.percentual_conclusao
                },
                'itens': [{
                    'id': item.id,
                    'item': item.item_padrao.item,
                    'descricao': item.item_padrao.descricao,
                    'criticidade': item.item_padrao.criticidade,
                    'ordem': item.item_padrao.ordem,
                    'status': item.status,
                    'observacao': item.observacao,
                    'verificado_em': item.verificado_em.isoformat() if item.verificado_em else None,
                    'verificado_por': item.verificado_por.first_name if item.verificado_por else None
                } for item in itens],
                'message': f'Checklist com {itens.count()} itens'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao buscar itens: {str(e)}'
            }, status=500)
    
    def _finalizar_checklist(self, equipamento, operador, data):
        """Finaliza checklist em andamento"""
        try:
            checklist = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=date.today(),
                status='EM_ANDAMENTO'
            ).first()
            
            if not checklist:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhum checklist em andamento encontrado'
                }, status=404)
            
            # Verificar permissão
            if operador and not operador.pode_finalizar_checklist(checklist.id):
                return JsonResponse({
                    'success': False,
                    'error': 'Operador não autorizado a finalizar este checklist'
                }, status=403)
            
            # Verificar se há itens pendentes
            itens_pendentes = checklist.itens.filter(status='PENDENTE').count()
            if itens_pendentes > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'Existem {itens_pendentes} itens pendentes. Complete todos os itens antes de finalizar.',
                    'itens_pendentes': itens_pendentes
                }, status=400)
            
            # Finalizar checklist
            checklist.finalizar_checklist()
            
            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid),
                    'status': checklist.status,
                    'data_conclusao': checklist.data_conclusao.isoformat() if checklist.data_conclusao else None,
                    'necessita_manutencao': checklist.necessita_manutencao,
                    'percentual_conclusao': checklist.percentual_conclusao
                },
                'message': f'Checklist finalizado! {"⚠️ Necessita manutenção" if checklist.necessita_manutencao else "✅ Tudo conforme"}',
                'proxima_acao': None
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao finalizar checklist: {str(e)}'
            }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def atualizar_item_checklist(request):
    """
    Endpoint para atualizar item do checklist via bot
    POST /api/nr12/bot/item-checklist/atualizar/
    
    Body: {
        "item_id": 123,
        "status": "OK|NOK|NA",
        "observacao": "texto opcional",
        "operador_codigo": "OP0001"
    }
    """
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        status = data.get('status')
        observacao = data.get('observacao', '')
        operador_codigo = data.get('operador_codigo')
        
        if not item_id or not status:
            return JsonResponse({
                'success': False,
                'error': 'item_id e status são obrigatórios'
            }, status=400)
        
        if status not in ['OK', 'NOK', 'NA']:
            return JsonResponse({
                'success': False,
                'error': 'Status deve ser OK, NOK ou NA'
            }, status=400)
        
        # Buscar item
        item = get_object_or_404(ItemChecklistRealizado, id=item_id)
        
        # Verificar se checklist está em andamento
        if item.checklist.status != 'EM_ANDAMENTO':
            return JsonResponse({
                'success': False,
                'error': 'Checklist não está em andamento'
            }, status=400)
        
        # Buscar operador se fornecido
        operador = None
        if operador_codigo:
            operador = Operador.objects.filter(
                codigo=operador_codigo,
                status='ATIVO',
                ativo_bot=True
            ).first()
            
            if not operador:
                return JsonResponse({
                    'success': False,
                    'error': 'Operador não encontrado'
                }, status=404)
        
        # Atualizar item
        item.status = status
        item.observacao = observacao
        item.verificado_em = timezone.now()
        if operador:
            item.verificado_por = operador.user
        item.save()
        
        return JsonResponse({
            'success': True,
            'item': {
                'id': item.id,
                'status': item.status,
                'observacao': item.observacao,
                'verificado_em': item.verificado_em.isoformat(),
                'verificado_por': operador.nome if operador else None
            },
            'checklist': {
                'percentual_conclusao': item.checklist.percentual_conclusao
            },
            'message': f'Item marcado como {item.get_status_display()}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)