# backend/apps/ordens_servico/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrdemServicoViewSet

router = DefaultRouter()
router.register(r'', OrdemServicoViewSet, basename='ordemservico')

urlpatterns = router.urls
