# apps/empreendimentos/urls.py
from rest_framework.routers import DefaultRouter
from .views import EmpreendimentoViewSet

router = DefaultRouter()
router.register(r'', EmpreendimentoViewSet)

urlpatterns = router.urls
