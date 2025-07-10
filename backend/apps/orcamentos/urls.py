# backend/apps/orcamentos/urls.py
from rest_framework import routers
from .views import OrcamentoViewSet

router = routers.DefaultRouter()
router.register(r'orcamentos', OrcamentoViewSet, basename='orcamento')

urlpatterns = router.urls