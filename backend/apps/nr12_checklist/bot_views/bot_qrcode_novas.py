# backend/apps/nr12_checklist/bot_views/bot_qrcode_novas.py
# Arquivo com as novas views para o fluxo QR → Checklist

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

from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import (
    ChecklistNR12, 
    ItemChecklistRealizado,
    TipoEquipamentoNR12,
    ItemChecklistPadrao
)

@csrf_exempt
@require_http_methods(["GET"])
def buscar_equipamento_por_codigo(request):
    """
    Busca equipamento por código/número de série
    GET /api/nr12/equipamentos/buscar/?codigo={codigo}
    """
    try:
        codigo = request.GET.get('codigo', '').strip()
        
        if not codigo:
            return JsonResponse({
                'success': False,
                'error': 'Código é obrigatório'
            }, status=400)
        
        # Buscar por diferentes campos
        equipamento = None
        
        # Primeiro, tentar por ID direto se for número
        if codigo.isdigit():
            try:
                equipamento = Equipamento.objects.get(id=int(codigo))
            except Equipamento.DoesNotExist:
                pass
        
        # Se não achou, buscar por número de série
        if not equipamento:
            equipamento = Equipamento.objects.filter(
                numero_serie__iexact=codigo
            ).first()
        
        # Se ainda não achou, buscar por outros campos possíveis
        if not equipamento:
            # Adapte conforme os campos do seu modelo Equipamento
            equipamento = Equipamento.objects.filter(
                nome__icontains=codigo
            ).first()
        
        if not equipamento:
            return JsonResponse({
                'success': False,
                'error': 'Equipamento não encontrado'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'id': equipamento.id,
            'nome': equipamento.nome,
            'numero_serie': getattr(equipamento, 'numero_serie', None),
            'modelo': getattr(equipamento, 'modelo', None),
            'fabricante': getattr(equipamento, 'fabricante', None)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EquipamentoAcessoQRView(View):
    """
    API NOVA para acesso a equipamento via QR code
    Retorna informações do equipamento e checklists disponíveis
    GET /api/nr12/equipamento-qr/{equipamento_id}/
    """
    
    def get(self, request, equipamento_id):
        """Retorna informações do equipamento e ações disponíveis"""
        try:
            # Buscar equipamento
            equipamento = get_object_or_404(Equipamento, id=equipamento_id)
            
            # Buscar checklists de hoje
            hoje = date.today()
            checklists_hoje = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=hoje
            )
            
            # Verificar ações disponíveis
            acoes = []
            
            # Verificar se há checklist em andamento
            checklist_em_andamento = checklists_hoje.filter(
                status__in=['INICIADO', 'EM_ANDAMENTO']
            ).first()

            if checklist_em_andamento:
                acoes.append({
                    'acao': 'continuar_checklist',
                    'checklist_id': checklist_em_andamento.id,
                    'texto': f'Continuar checklist {checklist_em_andamento.turno}',
                    'turno': checklist_em_andamento.turno,
                    'status': checklist_em_andamento.status
                })
            else:
                # Verificar turnos disponíveis
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
                'nome': equipamento.nome,
                'numero_serie': getattr(equipamento, 'numero_serie', None),
                'modelo': getattr(equipamento, 'modelo', None),
                'fabricante': getattr(equipamento, 'fabricante', None),
                'categoria': getattr(equipamento.categoria, 'nome', None) if hasattr(equipamento, 'categoria') else None,
                'status_operacional': getattr(equipamento, 'status_operacional', 'ATIVO'),
                'horimetro_atual': float(getattr(equipamento, 'horimetro_atual', 0) or 0),
                'cliente': equipamento.cliente.razao_social if hasattr(equipamento, 'cliente') and equipamento.cliente else None,
            }
            
            return JsonResponse({
                'success': True,
                'equipamento': equipamento_info,
                'acoes': acoes,
                'resumo_hoje': {
                    'total_checklists': checklists_hoje.count(),
                    'concluidos': checklists_hoje.filter(status='CONCLUIDO').count(),
                    'em_andamento': checklists_hoje.filter(status__in=['INICIADO', 'EM_ANDAMENTO']).count()
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CriarChecklistView(View):
    """
    API para criar novo checklist
    POST /api/nr12/equipamento/{equipamento_id}/checklist-novo/
    """
    
    def post(self, request, equipamento_id):
        """Cria um novo checklist para o equipamento"""
        try:
            data = json.loads(request.body or '{}')
            turno = data.get('turno')
            operador_id = data.get('operador_id')
            
            if not turno:
                return JsonResponse({
                    'success': False,
                    'error': 'Turno é obrigatório'
                }, status=400)
            
            # Buscar equipamento
            equipamento = get_object_or_404(Equipamento, id=equipamento_id)
            
            # Verificar se já existe checklist para este turno hoje
            hoje = date.today()
            checklist_existente = ChecklistNR12.objects.filter(
                equipamento=equipamento,
                data_checklist=hoje,
                turno=turno
            ).first()
            
            if checklist_existente:
                return JsonResponse({
                    'success': False,
                    'error': f'Já existe checklist para o turno {turno} hoje'
                }, status=400)
            
            # Buscar tipo NR12 (adapte conforme sua estrutura)
            tipo_nr12 = None
            if hasattr(equipamento, 'categoria'):
                try:
                    tipo_nr12 = TipoEquipamentoNR12.objects.filter(
                        categoria_equipamento=equipamento.categoria
                    ).first()
                except:
                    pass
            
            if not tipo_nr12:
                # Se não tem tipo específico, usar o primeiro disponível
                tipo_nr12 = TipoEquipamentoNR12.objects.first()
                
            if not tipo_nr12:
                return JsonResponse({
                    'success': False,
                    'error': 'Nenhum tipo NR12 configurado no sistema'
                }, status=400)
            
            with transaction.atomic():
                # Criar checklist
                checklist = ChecklistNR12.objects.create(
                    equipamento=equipamento,
                    tipo_equipamento_nr12=tipo_nr12,
                    data_checklist=hoje,
                    turno=turno,
                    status='INICIADO'
                )
                
                # Se foi passado operador_id, tentar definir
                if operador_id:
                    try:
                        from backend.apps.operadores.models import Operador
                        operador = Operador.objects.get(id=operador_id)
                        # Adapte conforme o campo correto do seu modelo
                        if hasattr(checklist, 'operador_responsavel'):
                            checklist.operador_responsavel = operador
                            checklist.save()
                    except:
                        pass  # Ignorar se não conseguir definir operador
                
                # Buscar itens padrão do tipo
                itens_padrao = ItemChecklistPadrao.objects.filter(
                    tipo_equipamento=tipo_nr12
                ).order_by('ordem')
                
                # Criar itens realizados
                itens_criados = []
                for item_padrao in itens_padrao:
                    item_realizado = ItemChecklistRealizado.objects.create(
                        checklist=checklist,
                        item_padrao=item_padrao,
                        status='PENDENTE'
                    )
                    itens_criados.append({
                        'id': item_realizado.id,
                        'descricao': item_padrao.descricao,
                        'observacoes': getattr(item_padrao, 'observacoes', ''),
                        'ordem': item_padrao.ordem,
                        'status': item_realizado.status
                    })
                
                return JsonResponse({
                    'success': True,
                    'checklist': {
                        'id': checklist.id,
                        'uuid': str(checklist.uuid),
                        'titulo': f"Checklist {equipamento.nome} - {turno}",
                        'data_checklist': checklist.data_checklist.isoformat(),
                        'turno': checklist.turno,
                        'status': checklist.status,
                        'equipamento': {
                            'id': equipamento.id,
                            'nome': equipamento.nome,
                            'numero_serie': getattr(equipamento, 'numero_serie', None)
                        },
                        'itens': itens_criados,
                        'total_itens': len(itens_criados)
                    }
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
class ChecklistDetalhesView(View):
    """
    API para obter detalhes completos do checklist
    GET /api/nr12/checklist-detalhes/{checklist_id}/
    """
    
    def get(self, request, checklist_id):
        """Retorna detalhes completos do checklist"""
        try:
            checklist = get_object_or_404(ChecklistNR12, id=checklist_id)
            
            # Buscar itens do checklist
            itens = ItemChecklistRealizado.objects.filter(
                checklist=checklist
            ).select_related('item_padrao').order_by('item_padrao__ordem')
            
            itens_data = []
            for item in itens:
                itens_data.append({
                    'id': item.id,
                    'descricao': item.item_padrao.descricao,
                    'observacoes': getattr(item.item_padrao, 'observacoes', ''),
                    'ordem': item.item_padrao.ordem,
                    'status': item.status,
                    'resultado': getattr(item, 'resultado', None),
                    'observacoes_item': getattr(item, 'observacoes', ''),
                    'data_verificacao': item.data_verificacao.isoformat() if hasattr(item, 'data_verificacao') and item.data_verificacao else None
                })
            
            return JsonResponse({
                'success': True,
                'checklist': {
                    'id': checklist.id,
                    'uuid': str(checklist.uuid),
                    'titulo': f"Checklist {checklist.equipamento.nome} - {checklist.turno}",
                    'data_checklist': checklist.data_checklist.isoformat(),
                    'turno': checklist.turno,
                    'status': checklist.status,
                    'equipamento': {
                        'id': checklist.equipamento.id,
                        'nome': checklist.equipamento.nome,
                        'numero_serie': getattr(checklist.equipamento, 'numero_serie', None),
                        'modelo': getattr(checklist.equipamento, 'modelo', None)
                    },
                    'itens': itens_data,
                    'total_itens': len(itens_data),
                    'itens_concluidos': len([i for i in itens_data if i['status'] == 'CONCLUIDO']),
                    'itens_pendentes': len([i for i in itens_data if i['status'] == 'PENDENTE'])
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)