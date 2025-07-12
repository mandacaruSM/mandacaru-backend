from django.core.management.base import BaseCommand
from django.conf import settings
import os
import base64

class Command(BaseCommand):
    help = 'Gera QR Codes para todos os equipamentos NR12'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--salvar-arquivos',
            action='store_true',
            help='Salvar QR codes como arquivos PNG',
        )
        parser.add_argument(
            '--equipamento-id',
            type=int,
            help='ID específico do equipamento',
        )
        parser.add_argument(
            '--diretorio',
            type=str,
            default='media/qr_equipamentos/',
            help='Diretório para salvar os QR codes',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🔗 Gerando QR Codes para equipamentos...")
        
        try:
            from backend.apps.nr12_checklist.qr_generator import gerar_qr_code_equipamento, gerar_qr_codes_todos_equipamentos
            from backend.apps.equipamentos.models import Equipamento
        except ImportError as e:
            self.stderr.write(f"❌ Erro de importação: {e}")
            return
        
        # Buscar equipamentos
        if options['equipamento_id']:
            try:
                equipamentos = [Equipamento.objects.get(id=options['equipamento_id'])]
            except Equipamento.DoesNotExist:
                self.stderr.write(f"❌ Equipamento ID {options['equipamento_id']} não encontrado")
                return
        else:
            equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        
        if not equipamentos:
            self.stdout.write("❌ Nenhum equipamento NR12 ativo encontrado")
            return
        
        self.stdout.write(f"📋 Encontrados {len(equipamentos)} equipamento(s)")
        
        # Criar diretório se necessário
        if options['salvar_arquivos']:
            diretorio = options['diretorio']
            os.makedirs(diretorio, exist_ok=True)
            self.stdout.write(f"📁 Diretório criado: {diretorio}")
        
        gerados = 0
        salvos = 0
        
        for equipamento in equipamentos:
            try:
                # Gerar QR Code
                qr_data = gerar_qr_code_equipamento(equipamento)
                gerados += 1
                
                nome = qr_data['equipamento']['nome']
                codigo = qr_data['equipamento']['codigo']
                
                self.stdout.write(f"  ✅ {nome} ({codigo})")
                self.stdout.write(f"     🔗 {qr_data['url']}")
                
                # Salvar arquivo se solicitado
                if options['salvar_arquivos']:
                    # Converter base64 para bytes
                    img_data = qr_data['qr_code_base64'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    
                    # Nome do arquivo
                    nome_arquivo = nome.replace(' ', '_').replace('/', '_')
                    filename = f"qr_equipamento_{codigo}_{nome_arquivo}.png"
                    filepath = os.path.join(diretorio, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_bytes)
                    
                    salvos += 1
                    self.stdout.write(f"     💾 Salvo: {filename}")
                
            except Exception as e:
                self.stdout.write(f"  ❌ Erro no equipamento {equipamento.id}: {str(e)}")
        
        # Resumo
        self.stdout.write(f"\n📊 RESUMO:")
        self.stdout.write(f"  🔗 QR Codes gerados: {gerados}")
        if options['salvar_arquivos']:
            self.stdout.write(f"  💾 Arquivos salvos: {salvos}")
            if salvos > 0:
                self.stdout.write(f"  📁 Local: {os.path.abspath(options['diretorio'])}")
        
        if gerados > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ {gerados} QR Code(s) de equipamentos gerado(s)!"))
            self.stdout.write("\n💡 PRÓXIMO PASSO:")
            self.stdout.write("   Imprima os QR codes e cole em cada equipamento")
            self.stdout.write("   Operadores escanearão para acessar via bot")
        else:
            self.stdout.write(self.style.WARNING("\n⚠️ Nenhum QR Code foi gerado"))