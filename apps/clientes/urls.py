from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, EmpreendimentoViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'empreendimentos', EmpreendimentoViewSet)

urlpatterns = router.urls
