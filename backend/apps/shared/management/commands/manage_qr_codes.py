# backend/apps/shared/management/commands/manage_qr_codes.py

from django.core.management.base import BaseCommand
from django.conf import settings
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
import os

# Importar o gerenciador
from backend.apps.shared.qr_manager import UnifiedQRManager

class Command(BaseCommand):
    help = 'Gerencia QR codes do sistema (gerar, atualizar, limpar)'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['gerar', 'atualizar', 'limpar', 'status'],
            help='Ação a ser executada'
        )
        parser.add_argument(
            '--tipo',
            choices=['operadores', 'equipamentos', 'todos'],
            default='todos',
            help='Tipo de QR code a processar'
        )
        parser.add_argument(
            '--tamanho',
            choices=['small', 'medium', 'large'],
            default='medium',
            help='Tamanho dos QR codes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força regeneração mesmo que já existam'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🔲 GERENCIADOR DE QR CODES'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        action = options['action']
        tipo = options['tipo']
        tamanho = options['tamanho']
        force = options['force']
        
        self.qr_manager = UnifiedQRManager()
        
        if action == 'gerar':
            self._gerar_qr_codes(tipo, tamanho, force)
        elif action == 'atualizar':
            self._atualizar_qr_codes(tipo, tamanho)
        elif action == 'limpar':
            self._limpar_qr_codes()
        elif action == 'status':
            self._mostrar_status()
    
    def _gerar_qr_codes(self, tipo, tamanho, force):
        """Gera QR codes"""
        self.stdout.write(f'🔲 Gerando QR codes - Tipo: {tipo}, Tamanho: {tamanho}')
        
        if tipo in ['operadores', 'todos']:
            self._gerar_qr_operadores(tamanho, force)
        
        if tipo in ['equipamentos', 'todos']:
            self._gerar_qr_equipamentos(tamanho, force)
        
        self.stdout.write(self.style.SUCCESS('✅ Geração concluída!'))
    
    def _gerar_qr_operadores(self, tamanho, force):
        """Gera QR codes para operadores"""
        self.stdout.write('\n👥 OPERADORES:')
        
        operadores = Operador.objects.filter(status='ATIVO')
        total = operadores.count()
        gerados = 0
        erros = 0
        
        for i, operador in enumerate(operadores, 1):
            try:
                # PADRÃO UNIFICADO: qr_codes/operadores/op_{codigo}_{tamanho}.png
                filename = f"op_{operador.codigo}_{tamanho}.png"
                filepath = os.path.join(self.qr_manager.base_dir, 'operadores', filename)
                
                if os.path.exists(filepath) and not force:
                    self.stdout.write(f'⏭️  {i:2d}/{total} - {operador.codigo} (já existe)')
                    continue
                
                # Gerar QR code
                qr_info = self.qr_manager.gerar_qr_operador(operador, tamanho)
                
                # Atualizar campo no modelo com caminho padronizado
                if hasattr(operador, 'qr_code'):
                    operador.qr_code = qr_info['relative_path']
                    operador.save(update_fields=['qr_code'])
                
                gerados += 1
                self.stdout.write(f'✅ {i:2d}/{total} - {operador.codigo} ({operador.nome[:20]})')
                
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ {i:2d}/{total} - {operador.codigo} - Erro: {e}')
                )
        
        self.stdout.write(f'\n📊 Operadores: {gerados} gerados, {erros} erros')
    
    def _gerar_qr_equipamentos(self, tamanho, force):
        """Gera QR codes para equipamentos"""
        self.stdout.write('\n🔧 EQUIPAMENTOS:')
        
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        total = equipamentos.count()
        gerados = 0
        erros = 0
        
        for i, equipamento in enumerate(equipamentos, 1):
            try:
                # PADRÃO UNIFICADO: qr_codes/equipamentos/eq_{id}_{tamanho}.png
                filename = f"eq_{equipamento.id}_{tamanho}.png"
                filepath = os.path.join(self.qr_manager.base_dir, 'equipamentos', filename)
                
                if os.path.exists(filepath) and not force:
                    self.stdout.write(f'⏭️  {i:2d}/{total} - EQ{equipamento.id:03d} (já existe)')
                    continue
                
                # Gerar QR code
                qr_info = self.qr_manager.gerar_qr_equipamento(equipamento, tamanho)
                
                # Atualizar campo no modelo com caminho padronizado
                if hasattr(equipamento, 'qr_code'):
                    equipamento.qr_code = qr_info['relative_path']
                    equipamento.save(update_fields=['qr_code'])
                
                gerados += 1
                self.stdout.write(f'✅ {i:2d}/{total} - EQ{equipamento.id:03d} ({equipamento.nome[:20]})')
                
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ {i:2d}/{total} - EQ{equipamento.id:03d} - Erro: {e}')
                )
        
        self.stdout.write(f'\n📊 Equipamentos: {gerados} gerados, {erros} erros')
    
    def _atualizar_qr_codes(self, tipo, tamanho):
        """Atualiza QR codes existentes"""
        self.stdout.write(f'🔄 Atualizando QR codes - Tipo: {tipo}')
        self._gerar_qr_codes(tipo, tamanho, force=True)
    
    def _limpar_qr_codes(self):
        """Remove QR codes antigos"""
        self.stdout.write('🧹 Limpando QR codes antigos...')
        
        try:
            removidos = self.qr_manager.limpar_qr_antigos(dias=30)
            self.stdout.write(self.style.SUCCESS(f'✅ {removidos} arquivos removidos'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao limpar: {e}'))
    
    def _mostrar_status(self):
        """Mostra status dos QR codes"""
        self.stdout.write('📊 STATUS DOS QR CODES\n')
        
        # Contar operadores
        operadores_total = Operador.objects.filter(status='ATIVO').count()
        operadores_com_qr = self._contar_arquivos('operadores')
        
        # Contar equipamentos  
        equipamentos_total = Equipamento.objects.filter(ativo_nr12=True).count()
        equipamentos_com_qr = self._contar_arquivos('equipamentos')
        
        # Espaço em disco
        tamanho_total = self._calcular_tamanho_diretorio()
        
        self.stdout.write(f'👥 OPERADORES:')
        self.stdout.write(f'   Total no sistema: {operadores_total}')
        self.stdout.write(f'   Com QR Code: {operadores_com_qr}')
        self.stdout.write(f'   Cobertura: {(operadores_com_qr/operadores_total*100):.1f}%' if operadores_total > 0 else '   Cobertura: 0%')
        
        self.stdout.write(f'\n🔧 EQUIPAMENTOS:')
        self.stdout.write(f'   Total no sistema: {equipamentos_total}')
        self.stdout.write(f'   Com QR Code: {equipamentos_com_qr}')
        self.stdout.write(f'   Cobertura: {(equipamentos_com_qr/equipamentos_total*100):.1f}%' if equipamentos_total > 0 else '   Cobertura: 0%')
        
        self.stdout.write(f'\n💾 ARMAZENAMENTO:')
        self.stdout.write(f'   Diretório: {self.qr_manager.base_dir}')
        self.stdout.write(f'   Tamanho total: {tamanho_total:.2f} MB')
        self.stdout.write(f'   Arquivos totais: {operadores_com_qr + equipamentos_com_qr}')
        
        # Verificar configurações
        self.stdout.write(f'\n⚙️ CONFIGURAÇÕES:')
        self.stdout.write(f'   MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'   MEDIA_URL: {settings.MEDIA_URL}')
        bot_url = getattr(settings, 'TELEGRAM_BOT_URL', 'https://t.me/Mandacarusmbot')
        self.stdout.write(f'   BOT_URL: {bot_url}')
        
    def _contar_arquivos(self, subdir):
        """Conta arquivos em um subdiretório"""
        caminho = os.path.join(self.qr_manager.base_dir, subdir)
        if not os.path.exists(caminho):
            return 0
        return len([f for f in os.listdir(caminho) if f.endswith('.png')])
    
    def _calcular_tamanho_diretorio(self):
        """Calcula tamanho total do diretório em MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.qr_manager.base_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Converter para MB