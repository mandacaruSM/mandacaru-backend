# 2. Criar api_urls.py

from django.urls import path, re_path
from .api_views import OperadorAPIView

urlpatterns = [
    path('', OperadorAPIView.as_view(), name='operador-list'),
    re_path(r'^(?P<pk>\d+)/$', OperadorAPIView.as_view(), name='operador-detail'),
]