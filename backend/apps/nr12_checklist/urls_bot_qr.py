# backend/apps/nr12_checklist/urls_bot_qr.py
# URLs específicas para o novo fluxo QR → Checklist

from django.urls import path
from backend.apps.nr12_checklist.bot_views import bot_qrcode_novas

urlpatterns = [
    # ================================================================
    # NOVAS APIS PARA FLUXO QR → CHECKLIST
    # ================================================================
    
    # Buscar equipamento por código/série
    path('equipamentos/buscar/', 
         bot_qrcode_novas.buscar_equipamento_por_codigo, 
         name='buscar-equipamento-codigo'),
    
    # Acesso a equipamento via QR (nova versão)
    path('equipamento-qr/<int:equipamento_id>/', 
         bot_qrcode_novas.EquipamentoAcessoQRView.as_view(), 
         name='acesso-equipamento-qr'),
    
    # Criar novo checklist para equipamento
    path('equipamento/<int:equipamento_id>/checklist-novo/', 
         bot_qrcode_novas.CriarChecklistView.as_view(), 
         name='criar-checklist-novo'),
    
    # Detalhes completos do checklist
    path('checklist-detalhes/<int:checklist_id>/', 
         bot_qrcode_novas.ChecklistDetalhesView.as_view(), 
         name='checklist-detalhes-novo'),
]