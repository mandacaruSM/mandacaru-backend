# backend/apps/shared/management/commands/padronizar_tudo.py

from django.core.management.base import BaseCommand
from django.conf import settings
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.shared.qr_manager import UnifiedQRManager
import os

class Command(BaseCommand):
    help = 'Padroniza TUDO - QR codes, caminhos e estrutura'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tamanho',
            choices=['small', 'medium', 'large', 'todos'],
            default='medium',
            help='Tamanho dos QR codes'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🎯 PADRONIZAÇÃO TOTAL DO SISTEMA'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        tamanho = options['tamanho']
        qr_manager = UnifiedQRManager()
        
        # 1. Verificar e corrigir configurações
        self.stdout.write('\n⚙️  Verificando configurações...')
        self._verificar_configuracoes()
        
        # 2. Limpar estrutura antiga
        self.stdout.write('\n🧹 Limpando estrutura antiga...')
        self._limpar_estrutura_antiga()
        
        # 3. Criar estrutura padronizada
        self.stdout.write('\n📁 Criando estrutura padronizada...')
        qr_manager.ensure_directories()
        
        # 4. Gerar QR codes em todos os tamanhos ou tamanho específico
        if tamanho == 'todos':
            for size in ['small', 'medium', 'large']:
                self.stdout.write(f'\n🔲 Gerando QR codes - Tamanho: {size}')
                self._gerar_qr_codes(qr_manager, size)
        else:
            self.stdout.write(f'\n🔲 Gerando QR codes - Tamanho: {tamanho}')
            self._gerar_qr_codes(qr_manager, tamanho)
        
        # 5. Atualizar modelos
        self.stdout.write('\n🔄 Atualizando modelos...')
        self._atualizar_modelos()
        
        # 6. Relatório final
        self.stdout.write('\n📊 RELATÓRIO FINAL:')
        self._relatorio_final(qr_manager)
        
        self.stdout.write(self.style.SUCCESS('\n✅ PADRONIZAÇÃO COMPLETA! 🎉'))
    
    def _verificar_configuracoes(self):
        """Verifica se as configurações estão corretas"""
        # Verificar MEDIA_ROOT
        media_root = str(settings.MEDIA_ROOT)
        if 'media\\media' in media_root or 'media/media' in media_root:
            self.stdout.write(self.style.WARNING('   ⚠️  MEDIA_ROOT tem duplicação!'))
            self.stdout.write('   💡 Corrija no settings.py: MEDIA_ROOT = BASE_DIR / "media"')
        else:
            self.stdout.write('   ✅ MEDIA_ROOT configurado corretamente')
        
        # Verificar URLs do bot
        bot_url = getattr(settings, 'TELEGRAM_BOT_URL', None)
        if bot_url:
            self.stdout.write(f'   ✅ Bot URL: {bot_url}')
        else:
            self.stdout.write('   ⚠️  TELEGRAM_BOT_URL não configurado')
    
    def _limpar_estrutura_antiga(self):
        """Remove estrutura antiga"""
        import shutil
        removidos = 0
        
        # Caminhos antigos
        caminhos_antigos = [
            os.path.join(settings.MEDIA_ROOT, 'operadores', 'qrcodes'),
            os.path.join(settings.MEDIA_ROOT, 'abastecimento', 'qr_codes'),
        ]
        
        for caminho in caminhos_antigos:
            if os.path.exists(caminho):
                shutil.rmtree(caminho)
                removidos += 1
                self.stdout.write(f'   🗑️  Removido: {os.path.basename(caminho)}')
        
        # Arquivos soltos na pasta qr_codes
        qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        if os.path.exists(qr_codes_dir):
            for arquivo in os.listdir(qr_codes_dir):
                if arquivo.endswith('.png') and os.path.isfile(os.path.join(qr_codes_dir, arquivo)):
                    os.remove(os.path.join(qr_codes_dir, arquivo))
                    removidos += 1
        
        self.stdout.write(f'   ✅ {removidos} itens antigos removidos')
    
    def _gerar_qr_codes(self, qr_manager, tamanho):
        """Gera QR codes no tamanho especificado"""
        # Operadores
        operadores = Operador.objects.filter(status='ATIVO')
        gerados_op = 0
        for operador in operadores:
            try:
                qr_manager.gerar_qr_operador(operador, tamanho)
                gerados_op += 1
            except Exception as e:
                self.stdout.write(f'   ❌ Erro operador {operador.codigo}: {e}')
        
        # Equipamentos
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        gerados_eq = 0
        for equipamento in equipamentos:
            try:
                qr_manager.gerar_qr_equipamento(equipamento, tamanho)
                gerados_eq += 1
            except Exception as e:
                self.stdout.write(f'   ❌ Erro equipamento {equipamento.id}: {e}')
        
        self.stdout.write(f'   👥 Operadores: {gerados_op} QR codes gerados')
        self.stdout.write(f'   🔧 Equipamentos: {gerados_eq} QR codes gerados')
    
    def _atualizar_modelos(self):
        """Atualiza campos nos modelos"""
        # Operadores
        operadores = Operador.objects.filter(status='ATIVO')
        for operador in operadores:
            if hasattr(operador, 'qr_code'):
                operador.qr_code = f"qr_codes/operadores/op_{operador.codigo}_medium.png"
                operador.save(update_fields=['qr_code'])
        
        # Equipamentos
        equipamentos = Equipamento.objects.filter(ativo_nr12=True)
        for equipamento in equipamentos:
            if hasattr(equipamento, 'qr_code'):
                equipamento.qr_code = f"qr_codes/equipamentos/eq_{equipamento.id}_medium.png"
                equipamento.save(update_fields=['qr_code'])
        
        self.stdout.write('   ✅ Campos dos modelos atualizados')
    
    def _relatorio_final(self, qr_manager):
        """Gera relatório final"""
        # Contar arquivos
        operadores_dir = os.path.join(qr_manager.base_dir, 'operadores')
        equipamentos_dir = os.path.join(qr_manager.base_dir, 'equipamentos')
        checklists_dir = os.path.join(qr_manager.base_dir, 'checklists')
        
        count_op = len(os.listdir(operadores_dir)) if os.path.exists(operadores_dir) else 0
        count_eq = len(os.listdir(equipamentos_dir)) if os.path.exists(equipamentos_dir) else 0
        count_ch = len(os.listdir(checklists_dir)) if os.path.exists(checklists_dir) else 0
        
        # Calcular tamanho
        total_size = 0
        for root, dirs, files in os.walk(qr_manager.base_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        total_size_mb = total_size / (1024 * 1024)
        
        self.stdout.write(f'   📁 Estrutura: {qr_manager.base_dir}')
        self.stdout.write(f'   👥 Operadores: {count_op} QR codes')
        self.stdout.write(f'   🔧 Equipamentos: {count_eq} QR codes') 
        self.stdout.write(f'   📋 Checklists: {count_ch} QR codes')
        self.stdout.write(f'   💾 Tamanho total: {total_size_mb:.2f} MB')
        self.stdout.write(f'   🎯 Padrão: UNIFICADO - qr_codes/{{tipo}}/{{prefixo}}_{{id}}_{{tamanho}}.png')