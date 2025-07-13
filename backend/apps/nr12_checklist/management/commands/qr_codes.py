
from django.core.management.base import BaseCommand
from backend.apps.nr12_checklist.qr_manager import QRCodeManager

class Command(BaseCommand):
    help = 'Gerencia QR codes PNG do sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'acao',
            choices=['gerar', 'limpar', 'listar', 'equipamentos'],
            help='Ação a ser executada'
        )
        
        parser.add_argument(
            '--checklist-id',
            type=int,
            help='ID do checklist específico'
        )
        
        parser.add_argument(
            '--equipamento-id',
            type=int,
            help='ID do equipamento específico'
        )
        
        parser.add_argument(
            '--tamanho',
            choices=['small', 'medium', 'large'],
            default='medium',
            help='Tamanho do QR code'
        )
        
        parser.add_argument(
            '--dias',
            type=int,
            default=7,
            help='Dias para limpeza de arquivos antigos'
        )
        
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Processar todos os itens'
        )
    
    def handle(self, *args, **options):
        qr_manager = QRCodeManager()
        acao = options['acao']
        
        self.stdout.write(f"🔲 Executando: {acao.upper()}")
        
        try:
            if acao == 'gerar':
                self._gerar_qr_codes(qr_manager, options)
            elif acao == 'limpar':
                self._limpar_qr_codes(qr_manager, options)
            elif acao == 'listar':
                self._listar_qr_codes(qr_manager)
            elif acao == 'equipamentos':
                self._gerar_qr_equipamentos(qr_manager, options)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro: {str(e)}")
            )
    
    def _gerar_qr_codes(self, qr_manager, options):
        """Gera QR codes para checklists"""
        if options['checklist_id']:
            # Checklist específico
            from backend.apps.nr12_checklist.models import ChecklistNR12
            checklist = ChecklistNR12.objects.get(id=options['checklist_id'])
            
            qr_info = qr_manager.gerar_qr_checklist(
                checklist, 
                options['tamanho'], 
                incluir_logo=True
            )
            
            self.stdout.write(f"✅ QR gerado: {qr_info['filename']}")
            self.stdout.write(f"   URL: {qr_info['url']}")
            
        elif options['todos']:
            # Todos os checklists pendentes
            from backend.apps.nr12_checklist.models import ChecklistNR12
            from datetime import date
            
            checklists = ChecklistNR12.objects.filter(
                data_checklist=date.today(),
                status='PENDENTE'
            )
            
            if not checklists.exists():
                self.stdout.write("ℹ️ Nenhum checklist pendente encontrado")
                return
            
            self.stdout.write(f"📋 Gerando QR codes para {checklists.count()} checklists...")
            
            resultados = qr_manager.gerar_batch_qr_codes(
                list(checklists),
                options['tamanho'],
                incluir_logo=True
            )
            
            sucesso = len([r for r in resultados if 'error' not in r])
            self.stdout.write(f"✅ {sucesso}/{len(resultados)} QR codes gerados")
        
        else:
            self.stdout.write("⚠️ Especifique --checklist-id ou --todos")
    
    def _gerar_qr_equipamentos(self, qr_manager, options):
        """Gera QR codes para equipamentos"""
        if options['equipamento_id']:
            # Equipamento específico
            from backend.apps.equipamentos.models import Equipamento
            equipamento = Equipamento.objects.get(id=options['equipamento_id'])
            
            qr_info = qr_manager.gerar_qr_equipamento(equipamento, options['tamanho'])
            
            self.stdout.write(f"✅ QR equipamento gerado: {qr_info['filename']}")
            self.stdout.write(f"   URL: {qr_info['url']}")
            
        elif options['todos']:
            # Todos os equipamentos NR12 ativos
            from backend.apps.equipamentos.models import Equipamento
            
            equipamentos = Equipamento.objects.filter(ativo_nr12=True)
            
            if not equipamentos.exists():
                self.stdout.write("ℹ️ Nenhum equipamento NR12 ativo encontrado")
                return
            
            self.stdout.write(f"🔧 Gerando QR codes para {equipamentos.count()} equipamentos...")
            
            gerados = 0
            for equipamento in equipamentos:
                try:
                    qr_info = qr_manager.gerar_qr_equipamento(equipamento, options['tamanho'])
                    self.stdout.write(f"  ✅ {equipamento.nome}: {qr_info['filename']}")
                    gerados += 1
                except Exception as e:
                    self.stdout.write(f"  ❌ {equipamento.nome}: {str(e)}")
            
            self.stdout.write(f"🎉 {gerados}/{equipamentos.count()} QR codes de equipamentos gerados")
        
        else:
            self.stdout.write("⚠️ Especifique --equipamento-id ou --todos")
    
    def _limpar_qr_codes(self, qr_manager, options):
        """Limpa QR codes antigos"""
        dias = options['dias']
        
        self.stdout.write(f"🧹 Limpando QR codes com mais de {dias} dias...")
        
        removed_count = qr_manager.limpar_qr_antigos(dias)
        
        if removed_count > 0:
            self.stdout.write(f"✅ {removed_count} arquivos removidos")
        else:
            self.stdout.write("ℹ️ Nenhum arquivo antigo encontrado")
    
    def _listar_qr_codes(self, qr_manager):
        """Lista QR codes existentes"""
        self.stdout.write("📋 QR CODES EXISTENTES")
        self.stdout.write("=" * 50)
        
        import os
        from datetime import datetime
        
        # Listar checklists
        checklists_dir = os.path.join(qr_manager.qr_dir, 'checklists')
        if os.path.exists(checklists_dir):
            files = [f for f in os.listdir(checklists_dir) if f.endswith('.png')]
            
            self.stdout.write(f"\n📋 CHECKLISTS ({len(files)} arquivos):")
            for filename in sorted(files):
                filepath = os.path.join(checklists_dir, filename)
                size = os.path.getsize(filepath) / 1024  # KB
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                self.stdout.write(f"  📄 {filename}")
                self.stdout.write(f"     Tamanho: {size:.1f} KB")
                self.stdout.write(f"     Criado: {modified.strftime('%d/%m/%Y %H:%M')}")
        
        # Listar equipamentos
        equipamentos_dir = os.path.join(qr_manager.qr_dir, 'equipamentos')
        if os.path.exists(equipamentos_dir):
            files = [f for f in os.listdir(equipamentos_dir) if f.endswith('.png')]
            
            self.stdout.write(f"\n🔧 EQUIPAMENTOS ({len(files)} arquivos):")
            for filename in sorted(files):
                filepath = os.path.join(equipamentos_dir, filename)
                size = os.path.getsize(filepath) / 1024  # KB
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                self.stdout.write(f"  📄 {filename}")
                self.stdout.write(f"     Tamanho: {size:.1f} KB")
                self.stdout.write(f"     Criado: {modified.strftime('%d/%m/%Y %H:%M')}")

