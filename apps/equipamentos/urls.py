from rest_framework.routers import DefaultRouter
from .views import EquipamentoViewSet

router = DefaultRouter()
router.register(r'', EquipamentoViewSet)

urlpatterns = router.urls
