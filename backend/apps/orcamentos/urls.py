# backend/apps/orcamentos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrcamentoViewSet

router = DefaultRouter()
router.register(r'', OrcamentoViewSet)
urlpatterns = router.urls