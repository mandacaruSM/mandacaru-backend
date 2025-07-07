from rest_framework.routers import DefaultRouter
from .views import ContaFinanceiraViewSet

router = DefaultRouter()
router.register(r'contas', ContaFinanceiraViewSet)

urlpatterns = router.urls
