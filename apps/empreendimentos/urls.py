from rest_framework.routers import DefaultRouter
from .views import EmpreendimentoViewSet

router = DefaultRouter()
router.register(r'empreendimentos', EmpreendimentoViewSet)

urlpatterns = router.urls
