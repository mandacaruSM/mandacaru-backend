# backend/apps/shared/management/commands/migrar_qr_padronizado.py

from django.core.management.base import BaseCommand
from django.conf import settings
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.shared.qr_manager import UnifiedQRManager
import os

class Command(BaseCommand):
    help = 'Migra QR codes para o padrão unificado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar-antigos',
            action='store_true',
            help='Remove arquivos antigos após migração'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🔄 MIGRAÇÃO PARA PADRÃO UNIFICADO'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        limpar_antigos = options['limpar_antigos']
        qr_manager = UnifiedQRManager()
        
        # 1. Migrar arquivos existentes
        self.stdout.write('\n📁 Migrando arquivos existentes...')
        migrados = qr_manager.migrar_qr_codes_existentes()
        self.stdout.write(f'✅ {migrados} arquivos migrados')
        
        # 2. Atualizar campos nos modelos
        self.stdout.write('\n🔄 Atualizando campos nos modelos...')
        self._atualizar_operadores()
        self._atualizar_equipamentos()
        
        # 3. Gerar QR codes faltantes
        self.stdout.write('\n🔲 Gerando QR codes faltantes...')
        self._gerar_qr_faltantes(qr_manager)
        
        # 4. Limpar arquivos antigos se solicitado
        if limpar_antigos:
            self.stdout.write('\n🧹 Limpando arquivos antigos...')
            self._limpar_arquivos_antigos()
        
        self.stdout.write(self.style.SUCCESS('\n✅ MIGRAÇÃO CONCLUÍDA!'))
        self.stdout.write('\n📊 PADRÃO UNIFICADO:')
        self.stdout.write('   • Operadores: qr_codes/operadores/op_{codigo}_{tamanho}.png')
        self.stdout.write('   • Equipamentos: qr_codes/equipamentos/eq_{id}_{tamanho}.png')
        self.stdout.write('   • Checklists: qr_codes/checklists/check_{uuid}_{tamanho}.png')
    
    def _atualizar_operadores(self):
        """Atualiza campos qr_code dos operadores"""
        operadores = Operador.objects.filter(status='ATIVO')
        atualizados = 0
        
        for operador in operadores:
            # Caminho padronizado
            novo_caminho = f"qr_codes/operadores/op_{operador.codigo}_medium.png"
            
            if hasattr(operador, 'qr_code'):
                operador.qr_code = novo_caminho
                operador.save(update_fields=['qr_code'])
                atualizados += 1
        
        self.stdout.write(f'   👥 Operadores: {atualizados} atualizados')
    
    def _atualizar_equipamentos(self):
        """Atualiza campos qr_code dos equipamentos"""
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        atualizados = 0
        
        for equipamento in equipamentos:
            # Caminho padronizado
            novo_caminho = f"qr_codes/equipamentos/eq_{equipamento.id}_medium.png"
            
            if hasattr(equipamento, 'qr_code'):
                equipamento.qr_code = novo_caminho
                equipamento.save(update_fields=['qr_code'])
                atualizados += 1
        
        self.stdout.write(f'   🔧 Equipamentos: {atualizados} atualizados')
    
    def _gerar_qr_faltantes(self, qr_manager):
        """Gera QR codes que ainda não existem"""
        # Operadores
        operadores = Operador.objects.filter(status='ATIVO')
        gerados_op = 0
        
        for operador in operadores:
            filename = f"op_{operador.codigo}_medium.png"
            filepath = os.path.join(qr_manager.base_dir, 'operadores', filename)
            
            if not os.path.exists(filepath):
                try:
                    qr_manager.gerar_qr_operador(operador, 'medium')
                    gerados_op += 1
                except Exception as e:
                    self.stdout.write(f'   ❌ Erro no operador {operador.codigo}: {e}')
        
        # Equipamentos
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        gerados_eq = 0
        
        for equipamento in equipamentos:
            filename = f"eq_{equipamento.id}_medium.png"
            filepath = os.path.join(qr_manager.base_dir, 'equipamentos', filename)
            
            if not os.path.exists(filepath):
                try:
                    qr_manager.gerar_qr_equipamento(equipamento, 'medium')
                    gerados_eq += 1
                except Exception as e:
                    self.stdout.write(f'   ❌ Erro no equipamento {equipamento.id}: {e}')
        
        self.stdout.write(f'   👥 Operadores gerados: {gerados_op}')
        self.stdout.write(f'   🔧 Equipamentos gerados: {gerados_eq}')
    
    def _limpar_arquivos_antigos(self):
        """Remove arquivos dos caminhos antigos"""
        removidos = 0
        
        # Limpar operadores antigos
        old_operadores_dir = os.path.join(settings.MEDIA_ROOT, 'operadores', 'qrcodes')
        if os.path.exists(old_operadores_dir):
            import shutil
            shutil.rmtree(old_operadores_dir)
            removidos += 1
            self.stdout.write('   👥 Diretório antigo de operadores removido')
        
        # Limpar equipamentos antigos (arquivos individuais)
        old_equipamentos_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        if os.path.exists(old_equipamentos_dir):
            for file in os.listdir(old_equipamentos_dir):
                if file.startswith('qr_equipamento_') and file.endswith('.png'):
                    filepath = os.path.join(old_equipamentos_dir, file)
                    os.remove(filepath)
                    removidos += 1
        
        self.stdout.write(f'   🧹 {removidos} itens antigos removidos')