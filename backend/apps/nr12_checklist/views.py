# backend/apps/nr12_checklist/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from backend.apps.operadores.models import Operador
from backend.apps.nr12_checklist.models import ChecklistNR12
from rest_framework.permissions import IsAuthenticated
from .models import ItemChecklistRealizado
from .serializers import ItemChecklistRealizadoSerializer

class ItemChecklistAtualizarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            item = ItemChecklistRealizado.objects.get(id=request.data['id'])
            if item.checklist.status not in ['PENDENTE', 'EM_ANDAMENTO']:
                return Response({'error': 'Checklist já foi finalizado'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ItemChecklistRealizadoSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": True, "detail": "Item atualizado com sucesso"}, status=status.HTTP_200_OK)
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ItemChecklistRealizado.DoesNotExist:
            return Response({"success": False, "error": "Item não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ChecklistsAbertosPorChatView(APIView):
    def get(self, request):
        chat_id = request.query_params.get('chat_id')
        codigo  = request.query_params.get('operador_codigo')

        op = None
        if chat_id:
            op = Operador.objects.filter(chat_id_telegram=str(chat_id)).first()
        if not op and codigo:
            op = Operador.objects.filter(codigo=codigo).first()
        if not op:
            return Response({"success": False, "error": "Operador não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        qs = op.get_checklists_abertos()
        data = ChecklistNR12Serializer(qs, many=True).data
        return Response({"success": True, "count": qs.count(), "results": data}, status=200)