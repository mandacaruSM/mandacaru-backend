from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ChecklistNR12
from .qr_manager import QRCodeManager

def checklist_with_qr(request, checklist_id):
    """View que mostra checklist com QR code"""
    checklist = get_object_or_404(ChecklistNR12, id=checklist_id)
    
    # Gerar QR code se não existir
    if not checklist.tem_qr_png():
        qr_manager = QRCodeManager()
        qr_info = qr_manager.gerar_qr_checklist(checklist)
    else:
        qr_info = {'url': checklist.qr_code_png_url}
    
    context = {
        'checklist': checklist,
        'qr_code_url': qr_info['url']
    }
    
    return render(request, 'checklist_detail.html', context)

def download_qr_codes_zip(request):
    """Download de todos os QR codes em ZIP"""
    import zipfile
    from django.http import HttpResponse
    import os
    
    qr_manager = QRCodeManager()
    
    # Criar ZIP em memória
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
    
    with zipfile.ZipFile(response, 'w') as zip_file:
        # Adicionar QR codes de checklists
        checklists_dir = os.path.join(qr_manager.qr_dir, 'checklists')
        if os.path.exists(checklists_dir):
            for filename in os.listdir(checklists_dir):
                if filename.endswith('.png'):
                    file_path = os.path.join(checklists_dir, filename)
                    zip_file.write(file_path, f"checklists/{filename}")
        
        # Adicionar QR codes de equipamentos
        equipamentos_dir = os.path.join(qr_manager.qr_dir, 'equipamentos')
        if os.path.exists(equipamentos_dir):
            for filename in os.listdir(equipamentos_dir):
                if filename.endswith('.png'):
                    file_path = os.path.join(equipamentos_dir, filename)
                    zip_file.write(file_path, f"equipamentos/{filename}")
    
    return response

