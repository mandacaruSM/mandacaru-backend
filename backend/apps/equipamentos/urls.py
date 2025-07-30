# backend/apps/equipamentos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipamentoViewSet, gerar_qr_pdf
from django.urls import path
from . import views



router = DefaultRouter()
router.register(r'', EquipamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:equipamento_id>/qr-pdf/', gerar_qr_pdf, name='qr_code_pdf'),
    path('por-uuid/<uuid:uuid>/', views.equipamento_por_uuid, name='equipamento-por-uuid'),
    
     
]
