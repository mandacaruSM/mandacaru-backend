# ================================================================
# ARQUIVO: backend/apps/nr12_checklist/management/commands/gerar_qr_codes.py
# ================================================================

from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.models import ChecklistNR12
from datetime import date, timedelta
import os

class Command(BaseCommand):
    help = 'Gera QR Codes para checklists NR12'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data-inicio',
            type=str,
            help='Data inicial (YYYY-MM-DD). Padrão: hoje',
        )
        parser.add_argument(
            '--data-fim', 
            type=str,
            help='Data final (YYYY-MM-DD). Padrão: hoje',
        )
        parser.add_argument(
            '--salvar-arquivos',
            action='store_true',
            help='Salvar QR codes como arquivos PNG',
        )
        parser.add_argument(
            '--mostrar-url',
            action='store_true', 
            help='Mostrar URLs geradas',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🔗 Gerando QR Codes para checklists NR12...")
        
        # Verificar se qr_generator existe
        try:
            from backend.apps.nr12_checklist.qr_generator import gerar_qr_code_base64
        except ImportError:
            self.stderr.write("❌ Arquivo qr_generator.py não encontrado!")
            self.stdout.write("💡 Crie o arquivo backend/apps/nr12_checklist/qr_generator.py com sua função")
            return
        
        # Determinar período
        if options['data_inicio']:
            try:
                data_inicio = date.fromisoformat(options['data_inicio'])
            except ValueError:
                self.stderr.write("❌ Formato de data inválido. Use YYYY-MM-DD")
                return
        else:
            data_inicio = date.today()
        
        if options['data_fim']:
            try:
                data_fim = date.fromisoformat(options['data_fim'])
            except ValueError:
                self.stderr.write("❌ Formato de data inválido. Use YYYY-MM-DD")
                return
        else:
            data_fim = data_inicio
        
        # Buscar checklists
        checklists = ChecklistNR12.objects.filter(
            data_checklist__range=[data_inicio, data_fim]
        ).order_by('data_checklist', 'turno')
        
        if not checklists.exists():
            self.stdout.write("❌ Nenhum checklist encontrado no período especificado")
            self.stdout.write(f"📅 Período pesquisado: {data_inicio} a {data_fim}")
            
            # Mostrar checklists disponíveis
            total_checklists = ChecklistNR12.objects.count()
            if total_checklists > 0:
                self.stdout.write(f"💡 Existem {total_checklists} checklists no sistema")
                ultimo_checklist = ChecklistNR12.objects.last()
                self.stdout.write(f"📋 Último checklist: {ultimo_checklist.data_checklist}")
            else:
                self.stdout.write("💡 Nenhum checklist encontrado no sistema")
                self.stdout.write("   Execute: python manage.py gerar_checklists_diarios")
            return
        
        self.stdout.write(f"📋 Encontrados {checklists.count()} checklists no período")
        
        # Criar diretório para arquivos se necessário
        if options['salvar_arquivos']:
            diretorio = 'media/qr_codes/'
            os.makedirs(diretorio, exist_ok=True)
            self.stdout.write(f"📁 Diretório criado: {diretorio}")
        
        gerados = 0
        salvos = 0
        erros = 0
        
        for checklist in checklists:
            try:
                # Gerar QR Code usando sua função
                qr_data = gerar_qr_code_base64(checklist)
                gerados += 1
                
                equipamento = qr_data.get('equipamento', 'N/A')
                data_checklist = qr_data.get('data', 'N/A')
                turno = qr_data.get('turno', 'N/A')
                
                self.stdout.write(f"  ✅ {equipamento} - {data_checklist} - {turno}")
                
                if options['mostrar_url']:
                    self.stdout.write(f"     🔗 {qr_data['url']}")
                
                # Salvar arquivo se solicitado
                if options['salvar_arquivos']:
                    try:
                        # Converter base64 para bytes e salvar
                        import base64
                        img_data = qr_data['qr_code_base64'].split(',')[1]
                        img_bytes = base64.b64decode(img_data)
                        
                        # Nome do arquivo
                        equipamento_nome = str(equipamento).replace(' ', '_').replace('/', '_')
                        filename = f"qr_{equipamento_nome}_{data_checklist}_{turno}_{checklist.uuid}.png"
                        filepath = os.path.join(diretorio, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(img_bytes)
                        
                        salvos += 1
                        self.stdout.write(f"     💾 Salvo: {filename}")
                        
                    except Exception as e:
                        self.stdout.write(f"     ❌ Erro ao salvar arquivo: {str(e)}")
                
            except Exception as e:
                erros += 1
                self.stdout.write(f"  ❌ Erro no checklist {checklist.id}: {str(e)}")
        
        # Resumo final
        self.stdout.write(f"\n📊 RESUMO:")
        self.stdout.write(f"  📅 Período: {data_inicio} a {data_fim}")
        self.stdout.write(f"  📋 Checklists processados: {checklists.count()}")
        self.stdout.write(f"  🔗 QR Codes gerados: {gerados}")
        
        if options['salvar_arquivos']:
            self.stdout.write(f"  💾 Arquivos salvos: {salvos}")
            if salvos > 0:
                self.stdout.write(f"  📁 Local: {os.path.abspath(diretorio)}")
        
        if erros > 0:
            self.stdout.write(f"  ❌ Erros: {erros}")
        
        # Mensagem final
        if gerados > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ {gerados} QR Code(s) gerado(s) com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING("\n⚠️ Nenhum QR Code foi gerado"))
        
        # Dicas de uso
        if gerados > 0 and not options['mostrar_url']:
            self.stdout.write("\n💡 Dicas:")
            self.stdout.write("   Use --mostrar-url para ver as URLs geradas")
            if not options['salvar_arquivos']:
                self.stdout.write("   Use --salvar-arquivos para salvar como PNG")