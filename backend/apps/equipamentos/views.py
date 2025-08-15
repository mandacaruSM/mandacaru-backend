# backend/apps/equipamentos/views.py
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os

from .models import Equipamento
from .serializers import EquipamentoSerializer


# \U0001f512 APIs protegidas (requerem autenticação)

class EquipamentoViewSet(viewsets.ModelViewSet):
    """CRUD de equipamentos (API protegida)."""

    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer


def gerar_qr_pdf(request, equipamento_id):
    """Gera um PDF com as informações e o QR Code do equipamento."""

    equipamento = get_object_or_404(Equipamento, id=equipamento_id)

    if not equipamento.qr_code:
        raise Http404("QR Code ainda não foi gerado para este equipamento.")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"attachment; filename=qr_equipamento_{equipamento.id}.pdf"
    )

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica-Bold", 14)

    y = 27 * cm
    p.drawString(2 * cm, y, "\U0001f4cb Identificação do Equipamento")
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
        p.drawString(2 * cm, y, "\u26a0\ufe0f QR Code não encontrado.")

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(
        2 * cm,
        2 * cm,
        "Escaneie o QR para acessar o equipamento via bot Mandacarusmbot",
    )

    p.showPage()
    p.save()

    return response


# \U0001f310 APIs públicas

@api_view(["GET"])
@permission_classes([AllowAny])
def equipamento_por_uuid(request, uuid):
    """Retorna dados básicos do equipamento identificado pelo UUID."""

    equipamento = get_object_or_404(Equipamento, uuid=uuid)

    if not equipamento.ativo_nr12:
        return Response({"error": "Equipamento não ativo"}, status=404)

    data = {
        "id": equipamento.id,
        "uuid": str(equipamento.uuid),
        "nome": str(equipamento),
        "horimetro_atual": float(equipamento.horimetro_atual or 0),
        "status_operacional": equipamento.status_operacional,
        "ativo_nr12": equipamento.ativo_nr12,
    }
    return Response(data)