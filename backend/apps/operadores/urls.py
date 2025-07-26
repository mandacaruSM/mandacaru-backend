# backend/apps/operadores/urls.py
from django.urls import path
from . import views

app_name = 'operadores'

urlpatterns = [
    path('', views.OperadorListView.as_view(), name='lista'),
    path('<int:pk>/', views.OperadorDetailView.as_view(), name='detalhe'),
    path('<int:operador_id>/gerar-qr/', views.gerar_qr_code_operador, name='gerar_qr'),
    path('<int:operador_id>/download-qr/', views.download_qr_code, name='download_qr'),
    path('api/verificar-qr/', views.verificar_operador_qr, name='verificar_qr'),
]
