# backend/apps/orcamentos/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrcamentoViewSet

router = DefaultRouter()
router.register(r'', OrcamentoViewSet, basename='orcamentos')

urlpatterns = router.urls
