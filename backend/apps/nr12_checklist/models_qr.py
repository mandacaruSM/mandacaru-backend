from django.db import models
from .qr_manager import QRCodeManager

class ChecklistQRMixin:
    """Mixin para adicionar funcionalidades de QR PNG aos checklists"""
    
    @property
    def qr_code_png_url(self):
        """URL do QR code PNG se existir"""
        qr_manager = QRCodeManager()
        filename = f"checklist_{self.uuid}_*_medium_*.png"
        
        import glob
        import os
        
        pattern = os.path.join(qr_manager.qr_dir, 'checklists', filename)
        files = glob.glob(pattern)
        
        if files:
            # Retornar o mais recente
            latest_file = max(files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return f"{settings.MEDIA_URL}qr_codes/checklists/{filename}"
        
        return None
    
    def gerar_qr_png(self, tamanho='medium', incluir_logo=True):
        """Gera QR code PNG para este checklist"""
        qr_manager = QRCodeManager()
        return qr_manager.gerar_qr_checklist(self, tamanho, incluir_logo)
    
    def tem_qr_png(self):
        """Verifica se já existe QR code PNG"""
        return self.qr_code_png_url is not None

class EquipamentoQRMixin:
    """Mixin para adicionar funcionalidades de QR PNG aos equipamentos"""
    
    @property
    def qr_code_png_url(self):
        """URL do QR code PNG do equipamento"""
        from django.conf import settings
        filename = f"eq_{self.id}_medium.png"
        filepath = os.path.join(settings.MEDIA_ROOT, 'qr_codes', 'equipamentos', filename)
        
        if os.path.exists(filepath):
            return f"{settings.MEDIA_URL}qr_codes/equipamentos/{filename}"
        
        return None
    
    def gerar_qr_png(self, tamanho='medium'):
        """Gera QR code PNG para este equipamento"""
        qr_manager = QRCodeManager()
        return qr_manager.gerar_qr_equipamento(self, tamanho)
    
    def tem_qr_png(self):
        """Verifica se já existe QR code PNG"""
        return self.qr_code_png_url is not None
