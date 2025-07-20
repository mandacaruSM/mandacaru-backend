# backend/apps/equipamentos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipamentoViewSet, gerar_qr_pdf

router = DefaultRouter()
router.register(r'', EquipamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:equipamento_id>/qr-pdf/', gerar_qr_pdf, name='qr_code_pdf'),
]
