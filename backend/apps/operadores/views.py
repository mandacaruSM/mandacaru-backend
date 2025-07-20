from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, FileResponse
from django.conf import settings
from .models import Operador
import os

class OperadorListView(ListView):
    model = Operador
    template_name = 'operadores/lista.html'
    context_object_name = 'operadores'

class OperadorDetailView(DetailView):
    model = Operador
    template_name = 'operadores/detalhe.html'
    context_object_name = 'operador'

def gerar_qr_code_operador(request, operador_id):
    operador = get_object_or_404(Operador, id=operador_id)
    operador.gerar_qr_code()
    return JsonResponse({'success': True})

def download_qr_code(request, operador_id):
    operador = get_object_or_404(Operador, id=operador_id)
    if operador.qr_code and operador.qr_code.path:
        return FileResponse(open(operador.qr_code.path, 'rb'), as_attachment=True)
    return JsonResponse({'error': 'QR Code não encontrado'}, status=404)

def verificar_operador_qr(request):
    codigo = request.GET.get('codigo')
    if not codigo:
        return JsonResponse({'valid': False, 'message': 'Código não informado'}, status=400)
    
    operador = Operador.objects.filter(qr_code_data=codigo).first()
    if operador:
        return JsonResponse({
            'valid': True,
            'nome': operador.nome,
            'codigo': operador.codigo,
            'status': operador.status
        })
    return JsonResponse({'valid': False, 'message': 'Operador não encontrado'}, status=404)
