# COMANDO PARA GERAR QR CODES
# ARQUIVO: backend/apps/nr12_checklist/management/commands/gerar_qr_codes.py
# ================================================================

from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.models import ChecklistNR12
from datetime import date, timedelta
import qrcode
import io
import base64
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Gera QR Codes para checklists NR12'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data-inicio',
            type=str,
            help='Data inicial (formato: YYYY-MM-DD). Padrão: hoje',
        )
        parser.add_argument(
            '--data-fim',
            type=str,
            help='Data final (formato: YYYY-MM-DD). Padrão: hoje',
        )
        parser.add_argument(
            '--salvar-arquivos',
            action='store_true',
            help='Salvar arquivos PNG dos QR codes',
        )
        parser.add_argument(
            '--diretorio',
            type=str,
            default='qr_codes',
            help='Diretório para salvar os QR codes',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🔗 Gerando QR Codes para checklists...")
        
        # Determinar período
        if options['data_inicio']:
            data_inicio = date.fromisoformat(options['data_inicio'])
        else:
            data_inicio = date.today()
        
        if options['data_fim']:
            data_fim = date.fromisoformat(options['data_fim'])
        else:
            data_fim = data_inicio
        
        # Buscar checklists no período
        checklists = ChecklistNR12.objects.filter(
            data_checklist__range=[data_inicio, data_fim]
        ).order_by('data_checklist', 'equipamento__nome', 'turno')
        
        if not checklists.exists():
            self.stdout.write("ℹ️  Nenhum checklist encontrado no período especificado")
            return
        
        # Criar diretório se necessário
        if options['salvar_arquivos']:
            qr_dir = os.path.join(settings.MEDIA_ROOT, options['diretorio'])
            os.makedirs(qr_dir, exist_ok=True)
        
        gerados = 0
        
        for checklist in checklists:
            # Gerar URL do checklist
            base_url = getattr(settings, 'BASE_URL', 'https://seu-dominio.com')
            checklist_url = f"{base_url}/checklist/{checklist.uuid}/"
            
            # Gerar QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(checklist_url)
            qr.make(fit=True)
            
            # Criar imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Salvar arquivo se solicitado
            if options['salvar_arquivos']:
                filename = f"checklist_{checklist.uuid}_{checklist.data_checklist}_{checklist.turno}.png"
                filepath = os.path.join(qr_dir, filename)
                img.save(filepath)
            
            gerados += 1
            
            # Mostrar progresso a cada 10 itens
            if gerados % 10 == 0:
                self.stdout.write(f"  📱 {gerados} QR codes gerados...")
        
        self.stdout.write(f"\n✅ {gerados} QR Codes gerados com sucesso!")
        
        if options['salvar_arquivos']:
            self.stdout.write(f"📁 Arquivos salvos em: {qr_dir}")
        
        # Estatísticas
        self.stdout.write(f"\n📊 ESTATÍSTICAS:")
        self.stdout.write(f"  📅 Período: {data_inicio} a {data_fim}")
        self.stdout.write(f"  📋 Checklists processados: {checklists.count()}")
        self.stdout.write(f"  🔗 QR Codes gerados: {gerados}")

