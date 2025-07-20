from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import OperadorViewSet

router = DefaultRouter()
router.register(r'', OperadorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
