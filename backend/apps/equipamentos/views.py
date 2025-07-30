# backend/apps/equipamentos/views.py
from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from .models import Equipamento
from .serializers import EquipamentoSerializer
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Equipamento

# 🔹 API REST para Equipamentos
class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer

# 🔹 Geração de PDF com QR Code
def gerar_qr_pdf(request, equipamento_id):
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)

    if not equipamento.qr_code:
        raise Http404("QR Code ainda não foi gerado para este equipamento.")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=qr_equipamento_{equipamento.id}.pdf'

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica-Bold", 14)

    y = 27 * cm
    p.drawString(2 * cm, y, "📋 Identificação do Equipamento")
    y -= 1 * cm

    p.setFont("Helvetica", 12)
    p.drawString(2 * cm, y, f"Nome: {equipamento.nome}")
    y -= 0.8 * cm
    p.drawString(2 * cm, y, f"Marca: {equipamento.marca or '---'}")
    y -= 0.8 * cm
    p.drawString(2 * cm, y, f"Modelo: {equipamento.modelo or '---'}")
    y -= 0.8 * cm
    p.drawString(2 * cm, y, f"Nº Série: {equipamento.n_serie or '---'}")
    y -= 0.8 * cm
    p.drawString(2 * cm, y, f"Cliente: {equipamento.cliente.razao_social}")
    y -= 1.2 * cm

    qr_path = equipamento.qr_code.path
    if os.path.exists(qr_path):
        p.drawImage(qr_path, 2 * cm, y - 8 * cm, width=10 * cm, height=10 * cm)
    else:
        p.drawString(2 * cm, y, "⚠️ QR Code não encontrado.")

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(2 * cm, 2 * cm, "Escaneie o QR para acessar o equipamento via bot Mandacarusmbot")

    p.showPage()
    p.save()

    return response

@api_view(['GET'])
def equipamento_por_uuid(request, uuid):
    """Busca equipamento pelo UUID"""
    try:
        equipamento = get_object_or_404(Equipamento, uuid=uuid)
        
        data = {
            'id': equipamento.id,
            'uuid': str(equipamento.uuid),
            'nome': str(equipamento),
            'numero_serie': equipamento.numero_serie,
            'modelo': equipamento.modelo,
            'fabricante': equipamento.fabricante,
            'horimetro_atual': float(equipamento.horimetro_atual or 0),
            'status_operacional': equipamento.status_operacional,
            'ativo_nr12': equipamento.ativo_nr12,
            'cliente': equipamento.cliente.razao_social if equipamento.cliente else None,
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

@api_view(['GET'])
def equipamento_por_uuid(request, uuid):
    """Busca equipamento pelo UUID para QR Code"""
    try:
        equipamento = get_object_or_404(Equipamento, uuid=uuid)
        
        data = {
            'id': equipamento.id,
            'uuid': str(equipamento.uuid),
            'nome': str(equipamento),
            'numero_serie': equipamento.numero_serie,
            'modelo': equipamento.modelo,
            'fabricante': equipamento.fabricante,
            'horimetro_atual': float(equipamento.horimetro_atual or 0),
            'status_operacional': equipamento.status_operacional,
            'ativo_nr12': equipamento.ativo_nr12,
            'cliente': equipamento.cliente.razao_social if equipamento.cliente else None,
            'categoria': equipamento.categoria.nome if equipamento.categoria else None,
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
    from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def equipamento_por_uuid(request, uuid):
    """Busca equipamento pelo UUID para QR Code"""
    try:
        equipamento = get_object_or_404(Equipamento, uuid=uuid)
        
        data = {
            'id': equipamento.id,
            'uuid': str(equipamento.uuid),
            'nome': str(equipamento),
            'numero_serie': equipamento.numero_serie,
            'modelo': equipamento.modelo,
            'fabricante': equipamento.fabricante,
            'horimetro_atual': float(equipamento.horimetro_atual or 0),
            'status_operacional': equipamento.status_operacional,
            'ativo_nr12': equipamento.ativo_nr12,
            'cliente': equipamento.cliente.razao_social if equipamento.cliente else None,
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([AllowAny])
def equipamento_por_uuid(request, uuid):
    """Busca equipamento pelo UUID para QR Code - ACESSO PÚBLICO"""
    try:
        equipamento = get_object_or_404(Equipamento, uuid=uuid)
        
        if not equipamento.ativo_nr12:
            return Response({'error': 'Equipamento não ativo'}, status=404)
        
        data = {
            'id': equipamento.id,
            'uuid': str(equipamento.uuid),
            'nome': str(equipamento),
            'horimetro_atual': float(equipamento.horimetro_atual or 0),
            'status_operacional': equipamento.status_operacional,
            'ativo_nr12': equipamento.ativo_nr12,
        }
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
def get_queryset(self):
    queryset = Operador.objects.all()
    chat_id = self.request.query_params.get('chat_id_telegram', None)
    if chat_id:
        queryset = queryset.filter(chat_id_telegram=chat_id)
    return queryset