# backend/apps/operadores/management/commands/sync_operators.py
# Comando para sincronizar operadores com sistema

from django.core.management.base import BaseCommand
from backend.apps.operadores.models import Operador
from backend.apps.equipamentos.models import Equipamento
from backend.apps.clientes.models import Cliente

class Command(BaseCommand):
    help = 'Sincroniza vínculos entre operadores, equipamentos e clientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-assign',
            action='store_true',
            help='Atribuir automaticamente todos os equipamentos a todos os operadores'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Sincronizando operadores...')
        
        # Contar operadores
        total_operadores = Operador.objects.filter(status='ATIVO').count()
        total_equipamentos = Equipamento.objects.filter(ativo_nr12=True).count()
        
        self.stdout.write(f'👥 {total_operadores} operadores ativos')
        self.stdout.write(f'🔧 {total_equipamentos} equipamentos NR12')
        
        if options['auto_assign']:
            self.stdout.write('🔗 Vinculando todos os equipamentos a todos os operadores...')
            
            operadores = Operador.objects.filter(status='ATIVO')
            equipamentos = Equipamento.objects.filter(ativo_nr12=True)
            
            for operador in operadores:
                # Limpar vínculos existentes
                operador.equipamentos_autorizados.clear()
                
                # Adicionar todos os equipamentos
                operador.equipamentos_autorizados.set(equipamentos)
                
                self.stdout.write(f'✅ {operador.nome}: {equipamentos.count()} equipamentos')
        
        # Verificar operadores sem vínculos
        operadores_sem_vinculos = Operador.objects.filter(
            status='ATIVO',
            equipamentos_autorizados__isnull=True,
            clientes_autorizados__isnull=True
        ).distinct()
        
        if operadores_sem_vinculos.exists():
            self.stdout.write('⚠️ Operadores sem vínculos:')
            for op in operadores_sem_vinculos:
                self.stdout.write(f'   - {op.codigo}: {op.nome}')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sincronização concluída!')
        )