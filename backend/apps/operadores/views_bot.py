from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Operador


@api_view(['PATCH'])
@permission_classes([AllowAny])
def atualizar_operador(request, operador_id):
    """Atualiza chat_id do operador"""
    try:
        operador = get_object_or_404(Operador, id=operador_id)
        
        chat_id = request.data.get('chat_id_telegram')
        if chat_id:
            operador.chat_id_telegram = chat_id
            operador.save(update_fields=['chat_id_telegram'])
        
        return Response({
            'success': True,
            'message': 'Operador atualizado',
            'operador': {
                'id': operador.id,
                'nome': operador.nome,
                'chat_id_telegram': getattr(operador, 'chat_id_telegram', None),
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
