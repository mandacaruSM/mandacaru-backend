# ================================================================
# COMANDO ADICIONAL PARA GERAR CHECKLISTS DIÁRIOS
# ARQUIVO: backend/apps/nr12_checklist/management/commands/gerar_checklists_diarios.py
# ================================================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from backend.apps.nr12_checklist.models import ChecklistNR12, TipoEquipamentoNR12
import uuid

class Command(BaseCommand):
    help = 'Gera checklists diários para equipamentos NR12'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='Data para gerar checklists (formato: YYYY-MM-DD). Padrão: hoje',
        )
        parser.add_argument(
            '--dias-avanco',
            type=int,
            default=0,
            help='Número de dias para gerar à frente (padrão: 0)',
        )
        parser.add_argument(
            '--turno',
            type=str,
            choices=['MANHA', 'TARDE', 'NOITE', 'MADRUGADA'],
            help='Turno específico (padrão: todos)',
        )
        parser.add_argument(
            '--equipamento-id',
            type=int,
            help='ID específico do equipamento',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("📅 Gerando checklists diários NR12...")
        
        # Determinar data
        if options['data']:
            try:
                data_checklist = date.fromisoformat(options['data'])
            except ValueError:
                self.stderr.write("❌ Formato de data inválido. Use YYYY-MM-DD")
                return
        else:
            data_checklist = date.today()
        
        # Gerar para múltiplos dias se especificado
        dias_para_gerar = options['dias_avanco'] + 1
        
        total_gerados = 0
        
        for i in range(dias_para_gerar):
            data_atual = data_checklist + timedelta(days=i)
            gerados_dia = self._gerar_checklists_para_data(
                data_atual, 
                options['turno'], 
                options['equipamento_id']
            )
            total_gerados += gerados_dia
            
            if gerados_dia > 0:
                self.stdout.write(f"  📋 {data_atual}: {gerados_dia} checklists gerados")
        
        self.stdout.write(f"\n✅ Total de checklists gerados: {total_gerados}")
        
        if total_gerados == 0:
            self.stdout.write("ℹ️  Nenhum checklist foi gerado. Possíveis motivos:")
            self.stdout.write("   • Checklists já existem para a data/turno especificado")
            self.stdout.write("   • Nenhum equipamento NR12 ativo encontrado")
            self.stdout.write("   • Equipamento especificado não encontrado")
    
    def _gerar_checklists_para_data(self, data_checklist, turno_especifico=None, equipamento_id=None):
        """Gera checklists para uma data específica"""
        
        # Buscar equipamentos NR12 ativos
        try:
            from backend.apps.equipamentos.models import Equipamento
            
            if equipamento_id:
                equipamentos = Equipamento.objects.filter(
                    id=equipamento_id,
                    ativo_nr12=True
                )
            else:
                equipamentos = Equipamento.objects.filter(ativo_nr12=True)
                
        except ImportError:
            self.stderr.write("❌ Modelo Equipamento não encontrado")
            return 0
        
        if not equipamentos.exists():
            return 0
        
        # Definir turnos
        turnos = [turno_especifico] if turno_especifico else ['MANHA', 'TARDE', 'NOITE']
        
        gerados = 0
        
        for equipamento in equipamentos:
            for turno in turnos:
                # Verificar se já existe checklist para esta data/turno
                if not ChecklistNR12.objects.filter(
                    equipamento=equipamento,
                    data_checklist=data_checklist,
                    turno=turno
                ).exists():
                    
                    # Criar checklist
                    checklist = ChecklistNR12.objects.create(
                        equipamento=equipamento,
                        data_checklist=data_checklist,
                        turno=turno,
                        status='PENDENTE',
                        uuid=uuid.uuid4()
                    )
                    gerados += 1
        
        return gerados
