# 3. ATUALIZAR backend/apps/auth_cliente/views.py
# ================================================================

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .serializers import LoginSerializer, UsuarioClienteSerializer, PerfilClienteSerializer
from .models import UsuarioCliente

@api_view(['POST'])
@permission_classes([AllowAny])
def login_cliente(request):
    """Login para clientes e admins"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        response_data = {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_cliente': user.is_cliente,
            'is_admin': user.is_admin_mandacaru
        }
        
        # Adicionar dados do cliente se for um usuário cliente
        if user.is_cliente:
            response_data.update({
                'cliente_id': user.cliente.id,
                'cliente_nome': user.cliente.razao_social,
                'cliente_fantasia': user.cliente.nome_fantasia,
                'cliente_cnpj': user.cliente.cnpj
            })
        
        return Response(response_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_cliente(request):
    """Logout do sistema"""
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Logout realizado com sucesso'})
    except Token.DoesNotExist:
        return Response({'error': 'Token não encontrado'}, status=400)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def atualizar_perfil(request):
    """Ver e atualizar perfil do usuário"""
    if request.method == 'GET':
        serializer = UsuarioClienteSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PerfilClienteSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vincular_telegram(request):
    """Vincular conta do Telegram"""
    telegram_chat_id = request.data.get('telegram_chat_id')
    
    if not telegram_chat_id:
        return Response({'error': 'telegram_chat_id é obrigatório'}, status=400)
    
    # Verificar se já está vinculado a outro usuário
    if UsuarioCliente.objects.filter(telegram_chat_id=telegram_chat_id).exclude(id=request.user.id).exists():
        return Response({'error': 'Este Telegram já está vinculado a outro usuário'}, status=400)
    
    request.user.telegram_chat_id = telegram_chat_id
    request.user.save()
    
    return Response({'message': 'Telegram vinculado com sucesso'})

class UsuarioClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usuários clientes"""
    queryset = UsuarioCliente.objects.all()
    serializer_class = UsuarioClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Clientes só veem seu próprio usuário
        if self.request.user.is_cliente:
            return UsuarioCliente.objects.filter(id=self.request.user.id)
        # Admins veem todos
        return super().get_queryset()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna dados do usuário logado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
