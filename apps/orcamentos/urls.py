from rest_framework.routers import DefaultRouter
from .views import OrcamentoViewSet

router = DefaultRouter()
router.register(r'', OrcamentoViewSet)

urlpatterns = router.urls
