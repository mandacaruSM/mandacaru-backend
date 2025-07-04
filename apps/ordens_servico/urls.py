from rest_framework.routers import DefaultRouter
from .views import OrdemServicoViewSet

router = DefaultRouter()
router.register(r'', OrdemServicoViewSet)

urlpatterns = router.urls
