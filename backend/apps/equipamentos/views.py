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

