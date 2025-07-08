from rest_framework.routers import DefaultRouter
from .views import FornecedorViewSet

router = DefaultRouter()
router.register(r'', FornecedorViewSet)

urlpatterns = router.urls
