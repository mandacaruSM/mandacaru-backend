# ===============================================
# backend/apps/operadores/views_bot.py  
# Views específicas para integração com Bot Telegram
# ===============================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date

from .models import Operador


@api_view(['GET'])
@permission_classes([AllowAny])
def operador_por_chat_id(request):
    """
    Busca operador pelo chat_id do Telegram
    """
    try:
        chat_id = request.GET.get('chat_id')
        
        if not chat_id:
            return Response({
                'success': False,
                'error': 'chat_id é obrigatório'
            }, status=400)
        
        # Buscar operador pelo chat_id
        operador = Operador.objects.filter(
            chat_id_telegram=str(chat_id),
            ativo_bot=True,
            status='ATIVO'
        ).first()
        
        if not operador:
            return Response({
                'success': False,
                'error': 'Operador não encontrado para este chat_id'
            }, status=404)
        
        return Response({
            'success': True,
            'operador': operador.get_resumo_para_bot()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def operadores_busca(request):
    """
    Busca operadores por nome (para autenticação do bot)
    """
    try:
        nome = request.GET.get('nome', '').strip()
        codigo = request.GET.get('codigo', '').strip()
        
        if not nome and not codigo:
            return Response({
                'success': False,
                'error': 'nome ou codigo é obrigatório'
            }, status=400)
        
        # Construir queryset
        queryset = Operador.objects.filter(
            ativo_bot=True,
            status='ATIVO'
        )
        
        if nome:
            # Busca por nome (case insensitive, contém)
            queryset = queryset.filter(nome__icontains=nome)
        
        if codigo:
            # Busca exata por código
            queryset = queryset.filter(codigo=codigo)
        
        # Limitar resultados
        operadores = queryset[:10]
        
        # Serializar dados (sem informações sensíveis)
        operadores_data = []
        for operador in operadores:
            operadores_data.append({
                'id': operador.id,
                'nome': operador.nome,
                'codigo': operador.codigo,
                'funcao': operador.funcao,
                'empresa': getattr(operador, 'empresa', {}).get('nome', '') if hasattr(operador, 'empresa') else '',
                'tem_chat_id': bool(operador.chat_id_telegram),
            })
        
        return Response({
            'success': True,
            'count': len(operadores_data),
            'results': operadores_data,
            'search_params': {
                'nome': nome,
                'codigo': codigo,
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def validar_operador_login(request):
    """
    Valida login do operador para o bot
    (nome + data de nascimento ou código)
    """
    try:
        nome = request.data.get('nome', '').strip()
        data_nascimento = request.data.get('data_nascimento', '').strip()
        codigo = request.data.get('codigo', '').strip()
        
        operador = None
        
        # Método 1: Busca por nome
        if nome:
            operadores = Operador.objects.filter(
                nome__icontains=nome,
                ativo_bot=True,
                status='ATIVO'
            )
            
            if operadores.count() == 1:
                operador = operadores.first()
            elif operadores.count() > 1:
                return Response({
                    'success': False,
                    'error': 'Múltiplos operadores encontrados. Use um nome mais específico.',
                    'operadores_encontrados': [
                        {'id': op.id, 'nome': op.nome, 'codigo': op.codigo}
                        for op in operadores[:5]
                    ]
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Nenhum operador encontrado com este nome'
                }, status=404)
        
        # Método 2: Busca por código
        elif codigo:
            try:
                operador = Operador.objects.get(
                    codigo=codigo,
                    ativo_bot=True,
                    status='ATIVO'
                )
            except Operador.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Operador não encontrado com este código'
                }, status=404)
        else:
            return Response({
                'success': False,
                'error': 'nome ou codigo é obrigatório'
            }, status=400)
        
        # Validar data de nascimento se fornecida
        if data_nascimento and hasattr(operador, 'data_nascimento') and operador.data_nascimento:
            try:
                # Converter string para date
                from datetime import datetime
                if '/' in data_nascimento:
                    data_informada = datetime.strptime(data_nascimento, '%d/%m/%Y').date()
                else:
                    data_informada = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
                
                if data_informada != operador.data_nascimento:
                    return Response({
                        'success': False,
                        'error': 'Data de nascimento incorreta'
                    }, status=401)
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Formato de data inválido. Use DD/MM/AAAA ou YYYY-MM-DD'
                }, status=400)
        
        # Login válido - atualizar último acesso
        operador.ultimo_acesso_bot = timezone.now()
        operador.save(update_fields=['ultimo_acesso_bot'])
        
        return Response({
            'success': True,
            'message': 'Login válido',
            'operador': operador.get_resumo_para_bot()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def atualizar_operador(request, operador_id):
    """
    Atualiza dados do operador (usado pelo bot)
    """
    try:
        operador = get_object_or_404(
            Operador, 
            id=operador_id, 
            ativo_bot=True, 
            status='ATIVO'
        )
        
        # Atualizar dados do operador
        chat_id = request.data.get('chat_id_telegram')
        ultimo_acesso = request.data.get('atualizar_ultimo_acesso', False)
        
        if chat_id:
            operador.chat_id_telegram = str(chat_id)
        
        if ultimo_acesso:
            operador.ultimo_acesso_bot = timezone.now()
        
        # Salvar apenas os campos que foram modificados
        update_fields = []
        if chat_id:
            update_fields.append('chat_id_telegram')
        if ultimo_acesso:
            update_fields.append('ultimo_acesso_bot')
            
        if update_fields:
            operador.save(update_fields=update_fields)
        
        return Response({
            'success': True,
            'message': 'Operador atualizado com sucesso',
            'operador': operador.get_resumo_para_bot()
        })
        
    except Operador.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Operador não encontrado ou não autorizado'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)