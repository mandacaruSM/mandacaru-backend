# apps/manutencao/urls.py

from rest_framework.routers import DefaultRouter
from .views import HistoricoManutencaoViewSet

router = DefaultRouter()
router.register(r"", HistoricoManutencaoViewSet)

urlpatterns = router.urls
