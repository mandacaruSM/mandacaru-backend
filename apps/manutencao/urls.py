from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoricoManutencaoViewSet

router = DefaultRouter()
router.register(r'', HistoricoManutencaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
