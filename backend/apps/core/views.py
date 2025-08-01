# ===============================================
# ARQUIVO: backend/apps/core/views.py
# Endpoint de health check para o bot
# ===============================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """
    Endpoint simples de health check para verificar se a API está funcionando
    GET /api/health/
    """
    
    def get(self, request):
        """Retorna status da API"""
        try:
            return JsonResponse({
                'status': 'ok',
                'message': 'API Mandacaru funcionando',
                'timestamp': '2025-07-31T19:00:00Z'
            })
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
