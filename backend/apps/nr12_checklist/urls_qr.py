from django.urls import path
from . import qr_manager

urlpatterns = [
    # Geração de QR codes
    path('qr/checklist/<int:checklist_id>/gerar/', qr_manager.gerar_qr_checklist_view, name='gerar_qr_checklist'),
    path('qr/equipamento/<int:equipamento_id>/gerar/', qr_manager.gerar_qr_equipamento_view, name='gerar_qr_equipamento'),
    path('qr/batch/gerar/', qr_manager.gerar_qr_batch_view, name='gerar_qr_batch'),
    
    # Gestão de QR codes
    path('qr/listar/', qr_manager.listar_qr_codes_view, name='listar_qr_codes'),
    path('qr/limpar/', qr_manager.limpar_qr_antigos_view, name='limpar_qr_antigos'),
]
