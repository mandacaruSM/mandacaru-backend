# backend/apps/nr12_checklist/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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