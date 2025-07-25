from django.urls import path
from backend.apps.nr12_checklist.bot_views import bot_api, bot_qrcode_views, bot_telegram


urlpatterns = [
    # Acesso rápido via QR Code UUID
    path('checklist/<uuid:checklist_uuid>/', bot_api.checklist_por_uuid, name='checklist-uuid'),

    path('api/nr12/bot/', include('backend.apps.nr12_checklist.urls_bot')),

    # HTML de visualização do checklist
    path('checklist/<int:pk>/pdf/', bot_api.visualizar_checklist_html, name='checklist-nr12-html'),

    # API para abrir o menu de ações do equipamento via QR code (bot)
    path('equipamento/<int:equipamento_id>/', bot_qrcode_views.EquipamentoAcessoView.as_view(), name='acesso-equipamento'),

    # API para registrar anomalia via bot
    path('equipamento/<int:equipamento_id>/registrar-anomalia/', bot_qrcode_views.RegistrarAnomaliaView.as_view(), name='registrar-anomalia'),

    # API para consultar relatório completo via bot
    path('equipamento/<int:equipamento_id>/relatorio/', bot_qrcode_views.RelatorioEquipamentoView.as_view(), name='relatorio-equipamento'),
]
