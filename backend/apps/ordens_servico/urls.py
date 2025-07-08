# backend/apps/ordens_servico/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdemServicoViewSet

router = DefaultRouter()
router.register(r'', OrdemServicoViewSet)
urlpatterns = router.urls