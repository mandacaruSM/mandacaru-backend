# 2. Criar api_urls.py

from django.urls import path
from .api_views import OperadorAPIView

urlpatterns = [
    path('', OperadorAPIView.as_view(), name='operadores_api'),
    path('<int:pk>/', OperadorAPIView.as_view(), name='operador_detail_api'),
]
