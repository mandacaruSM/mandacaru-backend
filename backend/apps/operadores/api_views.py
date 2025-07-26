# backend/apps/operadores/api_urls.py
from django.urls import path
from .api_views import OperadorListAPIView

app_name = 'api_operadores'

urlpatterns = [
    # GET  /api/operadores/?search=...
    path('', OperadorListAPIView.as_view(), name='list'),
]

