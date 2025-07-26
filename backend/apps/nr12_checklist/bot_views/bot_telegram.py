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
from django.db import transaction

from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import (
    ChecklistNR12, 
    ItemChecklistRealizado,
    TipoEquipamentoNR12,
    ItemChecklistPadrao
)

@csrf_exempt
@require_http_methods(["POST"])
def operador_login_qr(request):
    """
    Login de operador via QR Code para o Bot Telegram
    POST /api/nr12/bot/operador/login/
    Body: { "qr_code": "...", "chat_id": "123456789" }
    """
    try:
        data = json.loads(request.body or "{}")
        qr_code = data.get('qr_code')
        chat_id = data.get('chat_id')

        if not qr_code:
            return JsonResponse({
                'success': False, 
                'error': 'QR code é obrigatório'
            }, status=400)

        # Verificar operador pelo QR code
        operador = Operador.verificar_qr_code(qr_code)
        if not operador:
            return JsonResponse({
                'success': False, 
                'error': 'QR code inválido ou operador não autorizado'
            }, status=404)

        # Verificar se operador está ativo para o bot
        if not operador.ativo_bot:
            return JsonResponse({
                'success': False,
                'error': 'Operador não autorizado para uso do bot'
            }, status=403)

        # Atualizar chat_id e último acesso
        operador.atualizar_ultimo_acesso(chat_id)
        
        # Obter resumo do operador
        resumo = operador.get_resumo_para_bot()

        return JsonResponse({
            'success': True,
            'operador': resumo,
            'message': f"Bem-vindo, {operador.nome}!"
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'Dados inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EquipamentoAcessoBotView(View):
    """
    View para acesso a equipamento via Bot Telegram
    GET/POST /api/nr12/bot/equipamento/{id}/
    """
    
    def get(self, request, equipamento_id):
        """Obter informações do equipamento e checklists disponíveis"""
        try:
            # Obter operador
            operador_codigo = request.GET.get('operador')
            if not operador_codigo:
                return JsonResponse({
                    'success': False, 
                    'error': 'Código do operador é obrigatório'
                }, status=400)

            operador = Operador.objects.filter(
                codigo=operador_codigo,
                status='ATIVO',
                ativo_bot=True
            ).first()
            
            if not operador:
                return JsonResponse({
                    'success': False,
                    'error': 'Operador não autorizado'
                }, status=403)

            # Obter equipamento
            equipamento = get_object_or_404(
                Equipamento, 
                id=equipamento_id, 
                ativo_nr12=True
            )

            # Verificar checklists do dia
            hoje = timezone.now().date()
            checklists_hoje = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_realizacao=hoje
            ).order_by('-created_at')

            # Determinar ações disponíveis
            acoes = []
            checklist_em_andamento = checklists_hoje.filter(
                status__in=['INICIADO', 'EM_ANDAMENTO']
            ).first()

            if checklist_em_andamento:
                acoes.append({
                    'acao': 'continuar_checklist',
                    'checklist_id': checklist_em_andamento.id,
                    'texto': f'Continuar checklist {checklist_em_andamento.turno}'
                })
            else:
                # Pode criar novo checklist
                turnos_realizados = list(checklists_hoje.values_list('turno', flat=True))
                turnos_disponiveis = []
                
                for turno_choice in ChecklistNR12.TURNO_CHOICES:
                    if turno_choice[0] not in turnos_realizados:
                        turnos_disponiveis.append({
                            'valor': turno_choice[0],
                            'texto': turno_choice[1]
                        })
                
                if turnos_disponiveis:
                    acoes.append({
                        'acao': 'criar_checklist',
                        'turnos_disponiveis': turnos_disponiveis,
                        'texto': 'Criar novo checklist'
                    })

            # Montar resposta
            equipamento_info = {
                'id': equipamento.id,
                'numero_serie': equipamento.numero_serie,
                'modelo': equipamento.modelo,
                'fabricante': equipamento.fabricante,
                'categoria': getattr(equipamento.categoria, 'nome', None),
                'status_operacional': equipamento.status_operacional,
                'horimetro_atual': float(equipamento.horimetro_atual or 0),
                'cliente': equipamento.cliente.razao_social if equipamento.cliente else None,
            }
            
            checklists_info = []
            for c in checklists_hoje:
                checklists_info.append({
                    'id': c.id,
                    'uuid': str(c.uuid),
                    'turno': c.turno,
                    'status': c.status,
                    'frequencia': c.frequencia,
                    'responsavel': c.responsavel.first_name if c.responsavel else None,
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
            return JsonResponse({
                'success': False,
                'error': f'Erro ao acessar equipamento: {str(e)}'
            }, status=500)

    def post(self, request, equipamento_id):
        """Executar ação no equipamento"""
        try:
            data = json.loads(request.body or "{}")
            acao = data.get('acao')
            operador_codigo = data.get('operador_codigo')

            if not operador_codigo:
                return JsonResponse({
                    'success': False,
                    'error': 'Código do operador é obrigatório'
                }, status=400)

            # Validar operador
            operador = Operador.objects.filter(
                codigo=operador_codigo,
                status='ATIVO',
                ativo_bot=True
            ).first()
            
            if not operador:
                return JsonResponse({
                    'success': False,
                    'error': 'Operador não autorizado'
                }, status=403)

            # Obter equipamento
            equipamento = get_object_or_404(
                Equipamento,
                id=equipamento_id,
                ativo_nr12=True
            )

            # Executar ação
            if acao == 'criar_checklist':
                return self._criar_checklist(equipamento, operador, data)
            elif acao == 'iniciar_checklist':
                return self._iniciar_checklist(data.get('checklist_id'), operador)
            elif acao == 'continuar_checklist':
                return self._continuar_checklist(data.get('checklist_id'), operador)
            elif acao == 'finalizar_checklist':
                return self._finalizar_checklist(data.get('checklist_id'), operador)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Ação "{acao}" não reconhecida'
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Dados inválidos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao executar ação: {str(e)}'
            }, status=500)

    def _criar_checklist(self, equipamento, operador, data):
        """Criar novo checklist"""
        try:
            turno = data.get('turno', 'MANHA')
            frequencia = data.get('frequencia', 'DIARIA')
            
            # Verificar se já existe checklist para este turno hoje
            hoje = timezone.now().date()
            if ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_realizacao=hoje,
                turno=turno
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Já existe checklist para o turno {turno} hoje'
                }, status=400)

            # Obter tipo de equipamento NR12
            tipo_nr12 = equipamento.get_tipo_nr12()
            if not tipo_nr12:
                return JsonResponse({
                    'success': False,
                    'error': 'Equipamento não possui tipo NR12 configurado'
                }, status=400)

            with transaction.atomic():
                # Criar checklist
                checklist = ChecklistNR12.objects.create(
                    equipamento=equipamento,
                    responsavel=operador.user,
                    tipo_equipamento=tipo_nr12,
                    turno=turno,
                    frequencia=frequencia,
                    data_realizacao=hoje,
                    status='PENDENTE'
                )

                # Criar itens do checklist
                itens_padrao = ItemChecklistPadrao.objects.filter(
                    tipo_equipamento=tipo_nr12,
                    ativo=True
                ).order_by('ordem', 'categoria')

                for item_padrao in itens_padrao:
                    ItemChecklistRealizado.objects.create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        ordem=item_padrao.ordem,
                        status='PENDENTE'
                    )

                return JsonResponse({
                    'success': True,
                    'checklist': {
                        'id': checklist.id,
                        'uuid': str(checklist.uuid),
                        'turno': checklist.turno,
                        'total_itens': checklist.total_itens,
                    },
                    'message': f'Checklist {turno} criado com sucesso!'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao criar checklist: {str(e)}'
            }, status=500)

    def _iniciar_checklist(self, checklist_id, operador):
        """Iniciar preenchimento do checklist"""
        try:
            checklist = get_object_or_404(
                ChecklistNR12,
                id=checklist_id,
                status='PENDENTE'
            )

            # Verificar permissão
            if checklist.responsavel != operador.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Você não tem permissão para iniciar este checklist'
                }, status=403)

            # Atualizar status
            checklist.status = 'INICIADO'
            checklist.hora_inicio = timezone.now()
            checklist.save()

            # Obter primeiro item
            primeiro_item = checklist.itens.filter(
                status='PENDENTE'
            ).order_by('ordem').first()

            if primeiro_item:
                item_info = {
                    'id': primeiro_item.id,
                    'descricao': primeiro_item.item_padrao.descricao,
                    'categoria': primeiro_item.item_padrao.categoria,
                    'permite_na': primeiro_item.item_padrao.permite_na,
                    'requer_observacao': primeiro_item.item_padrao.requer_observacao_se_nok,
                }
            else:
                item_info = None

            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'status': checklist.status,
                    'percentual': checklist.percentual_conclusao,
                },
                'proximo_item': item_info,
                'message': 'Checklist iniciado!'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao iniciar checklist: {str(e)}'
            }, status=500)

    def _continuar_checklist(self, checklist_id, operador):
        """Continuar checklist em andamento"""
        try:
            checklist = get_object_or_404(
                ChecklistNR12,
                id=checklist_id,
                status__in=['INICIADO', 'EM_ANDAMENTO']
            )

            # Obter próximo item pendente
            proximo_item = checklist.itens.filter(
                status='PENDENTE'
            ).order_by('ordem').first()

            if not proximo_item:
                return JsonResponse({
                    'success': True,
                    'checklist': {
                        'id': checklist.id,
                        'status': checklist.status,
                        'percentual': 100,
                    },
                    'proximo_item': None,
                    'message': 'Todos os itens foram verificados! Use finalizar_checklist.'
                })

            item_info = {
                'id': proximo_item.id,
                'descricao': proximo_item.item_padrao.descricao,
                'categoria': proximo_item.item_padrao.categoria,
                'permite_na': proximo_item.item_padrao.permite_na,
                'requer_observacao': proximo_item.item_padrao.requer_observacao_se_nok,
                'ordem': proximo_item.ordem,
                'total_itens': checklist.total_itens,
                'itens_verificados': checklist.itens_verificados,
            }

            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'status': checklist.status,
                    'percentual': checklist.percentual_conclusao,
                },
                'proximo_item': item_info,
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao continuar checklist: {str(e)}'
            }, status=500)

    def _finalizar_checklist(self, checklist_id, operador):
        """Finalizar checklist"""
        try:
            checklist = get_object_or_404(
                ChecklistNR12,
                id=checklist_id,
                status__in=['INICIADO', 'EM_ANDAMENTO']
            )

            # Verificar se todos os itens foram verificados
            itens_pendentes = checklist.itens.filter(status='PENDENTE').count()
            if itens_pendentes > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'Ainda existem {itens_pendentes} itens pendentes'
                }, status=400)

            # Finalizar
            checklist.status = 'FINALIZADO'
            checklist.hora_fim = timezone.now()
            checklist.save()

            # Gerar estatísticas
            stats = {
                'total_itens': checklist.total_itens,
                'itens_ok': checklist.itens.filter(status='OK').count(),
                'itens_nok': checklist.itens.filter(status='NOK').count(),
                'itens_na': checklist.itens.filter(status='NA').count(),
                'duracao_minutos': (checklist.hora_fim - checklist.hora_inicio).seconds // 60,
            }

            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid),
                    'status': checklist.status,
                },
                'estatisticas': stats,
                'message': 'Checklist finalizado com sucesso!',
                'pdf_url': f'/api/nr12/checklist/{checklist.id}/pdf/'
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
    Atualizar status de um item do checklist
    POST /api/nr12/bot/item-checklist/atualizar/
    """
    try:
        data = json.loads(request.body or "{}")
        item_id = data.get('item_id')
        status = data.get('status')
        observacao = data.get('observacao', '')
        operador_codigo = data.get('operador_codigo')

        # Validações
        if not all([item_id, status, operador_codigo]):
            return JsonResponse({
                'success': False,
                'error': 'item_id, status e operador_codigo são obrigatórios'
            }, status=400)

        if status not in ['OK', 'NOK', 'NA']:
            return JsonResponse({
                'success': False,
                'error': 'Status deve ser OK, NOK ou NA'
            }, status=400)

        # Verificar operador
        operador = Operador.objects.filter(
            codigo=operador_codigo,
            status='ATIVO',
            ativo_bot=True
        ).first()
        
        if not operador:
            return JsonResponse({
                'success': False,
                'error': 'Operador não autorizado'
            }, status=403)

        # Obter item
        item = get_object_or_404(ItemChecklistRealizado, id=item_id)
        checklist = item.checklist

        # Verificar se pode atualizar
        if checklist.status not in ['INICIADO', 'EM_ANDAMENTO']:
            return JsonResponse({
                'success': False,
                'error': 'Checklist não está em andamento'
            }, status=400)

        # Validar regras do item
        if status == 'NA' and not item.item_padrao.permite_na:
            return JsonResponse({
                'success': False,
                'error': 'Este item não permite N/A'
            }, status=400)

        if status == 'NOK' and item.item_padrao.requer_observacao_se_nok and not observacao:
            return JsonResponse({
                'success': False,
                'error': 'Observação é obrigatória quando status é NOK'
            }, status=400)

        # Atualizar item
        with transaction.atomic():
            item.status = status
            item.observacao = observacao
            item.verificado_por = operador.user
            item.data_verificacao = timezone.now()
            item.save()

            # Atualizar status do checklist se necessário
            if checklist.status == 'INICIADO':
                checklist.status = 'EM_ANDAMENTO'
                checklist.save()

        # Obter próximo item
        proximo_item = checklist.itens.filter(
            status='PENDENTE'
        ).order_by('ordem').first()

        if proximo_item:
            proximo_item_info = {
                'id': proximo_item.id,
                'descricao': proximo_item.item_padrao.descricao,
                'categoria': proximo_item.item_padrao.categoria,
                'permite_na': proximo_item.item_padrao.permite_na,
                'requer_observacao': proximo_item.item_padrao.requer_observacao_se_nok,
            }
        else:
            proximo_item_info = None

        return JsonResponse({
            'success': True,
            'item_atualizado': {
                'id': item.id,
                'status': item.status,
                'observacao': item.observacao,
            },
            'checklist': {
                'id': checklist.id,
                'percentual': checklist.percentual_conclusao,
                'itens_verificados': checklist.itens_verificados,
                'total_itens': checklist.total_itens,
            },
            'proximo_item': proximo_item_info,
            'todos_verificados': proximo_item is None,
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar item: {str(e)}'
        }, status=500)