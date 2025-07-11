 # 2. ATUALIZAR backend/apps/cliente_portal/urls.py
# ================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'dashboard', views.DashboardClienteViewSet, basename='dashboard')
router.register(r'equipamentos', views.EquipamentoClienteViewSet, basename='cliente-equipamentos')

urlpatterns = [
    path('', include(router.urls)),
]
