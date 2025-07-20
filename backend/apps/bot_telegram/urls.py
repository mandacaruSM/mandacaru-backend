# backend/apps/bot_telegram/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # QR Code access routes
    path('qr/<uuid:checklist_uuid>/', views.checklist_qr_redirect, name='checklist-qr-redirect'),
    path('equipamento/<int:equipamento_id>/', views.equipamento_qr_redirect, name='equipamento-qr-redirect'),
    
    # Bot webhook
    path('webhook/telegram/', views.telegram_webhook, name='telegram-webhook'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]