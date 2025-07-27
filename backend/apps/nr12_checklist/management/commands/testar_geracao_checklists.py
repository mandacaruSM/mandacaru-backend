# backend/apps/nr12_checklist/management/commands/testar_geracao_checklists.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from backend.apps.equipamentos.models import Equipamento
from backend.apps.nr12_checklist.models import ChecklistNR12, ItemChecklistPadrao, TipoEquipamentoNR12
from backend.apps.nr12_checklist.tasks import gerar_checklists_diarios, gerar_checklists_semanais, gerar_checklists_mensais

class Command(BaseCommand):
    help = 'Testa a geração automática de checklists NR12'

    def add_arguments(self, parser):
        parser.add_argument(
            '--frequencia',
            type=str,
            choices=['diaria', 'semanal', 'mensal', 'todas'],
            default='todas',
            help='Frequência dos checklists a gerar'
        )
        parser.add_argument(
            '--equipamento',
            type=int,
            help='ID específico do equipamento para testar'
        )
        parser.add_argument(
            '--listar',
            action='store_true',
            help='Lista equipamentos configurados para NR12'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 TESTE DE GERAÇÃO DE CHECKLISTS NR12'))
        self.stdout.write('=' * 60)
        
        # Se apenas listar equipamentos
        if options['listar']:
            self.listar_equipamentos()
            return
        
        # Verificar configuração geral
        self.verificar_configuracao()
        
        # Testar geração por frequência
        frequencia = options['frequencia']
        equipamento_id = options.get('equipamento')
        
        if equipamento_id:
            self.testar_equipamento_especifico(equipamento_id)
        else:
            if frequencia == 'todas':
                self.testar_todas_frequencias()
            else:
                self.testar_frequencia_especifica(frequencia)

    def verificar_configuracao(self):
        """Verifica configuração básica do sistema"""
        self.stdout.write('\n📋 VERIFICANDO CONFIGURAÇÃO:')
        self.stdout.write('-' * 40)
        
        # Contar tipos NR12
        tipos_nr12 = TipoEquipamentoNR12.objects.count()
        self.stdout.write(f'   Tipos de Equipamento NR12: {tipos_nr12}')
        
        # Contar itens padrão
        itens_padrao = ItemChecklistPadrao.objects.count()
        self.stdout.write(f'   Itens de Checklist Padrão: {itens_padrao}')
        
        # Equipamentos ativos para NR12
        equipamentos_nr12 = Equipamento.objects.filter(ativo_nr12=True).count()
        self.stdout.write(f'   Equipamentos ativos NR12: {equipamentos_nr12}')
        
        # Equipamentos com frequência configurada
        with_freq = Equipamento.objects.filter(
            ativo_nr12=True,
            frequencias_checklist__len__gt=0
        ).count()
        self.stdout.write(f'   Com frequência configurada: {with_freq}')
        
        # Checklists existentes hoje
        hoje = date.today()
        checklists_hoje = ChecklistNR12.objects.filter(data_checklist=hoje).count()
        self.stdout.write(f'   Checklists hoje ({hoje}): {checklists_hoje}')

    def listar_equipamentos(self):
        """Lista equipamentos configurados para NR12"""
        self.stdout.write('\n🔧 EQUIPAMENTOS CONFIGURADOS PARA NR12:')
        self.stdout.write('-' * 50)
        
        equipamentos = Equipamento.objects.filter(
            ativo_nr12=True
        ).select_related('tipo_nr12', 'cliente')
        
        if not equipamentos.exists():
            self.stdout.write('   ❌ Nenhum equipamento configurado para NR12')
            return
        
        for eq in equipamentos:
            frequencias = eq.frequencias_checklist or []
            freq_str = ', '.join(frequencias) if frequencias else 'Nenhuma'
            
            itens_count = 0
            if eq.tipo_nr12:
                itens_count = ItemChecklistPadrao.objects.filter(
                    tipo_equipamento=eq.tipo_nr12,
                    ativo=True
                ).count()
            
            # ✅ CORRIGIDO: usar razao_social em vez de nome
            cliente_nome = "N/A"
            if eq.cliente:
                cliente_nome = eq.cliente.razao_social or eq.cliente.nome_fantasia or "N/A"
            
            self.stdout.write(f'   📌 {eq.nome}')
            self.stdout.write(f'      Cliente: {cliente_nome}')
            self.stdout.write(f'      Tipo NR12: {eq.tipo_nr12.nome if eq.tipo_nr12 else "❌ NÃO CONFIGURADO"}')
            self.stdout.write(f'      Frequências: {freq_str}')
            self.stdout.write(f'      Itens padrão: {itens_count}')
            self.stdout.write('')

    def testar_equipamento_especifico(self, equipamento_id):
        """Testa geração para equipamento específico"""
        try:
            equipamento = Equipamento.objects.get(id=equipamento_id, ativo_nr12=True)
            self.stdout.write(f'\n🔧 TESTANDO EQUIPAMENTO: {equipamento.nome}')
            self.stdout.write('-' * 50)
            
            if not equipamento.tipo_nr12:
                self.stdout.write('   ❌ Equipamento não tem tipo NR12 configurado')
                return
            
            itens_padrao = ItemChecklistPadrao.objects.filter(
                tipo_equipamento=equipamento.tipo_nr12,
                ativo=True
            ).count()
            
            self.stdout.write(f'   Tipo NR12: {equipamento.tipo_nr12.nome}')
            self.stdout.write(f'   Itens padrão: {itens_padrao}')
            self.stdout.write(f'   Frequências: {equipamento.frequencias_checklist or []}')
            
            # Simular criação de checklist
            hoje = date.today()
            for freq in (equipamento.frequencias_checklist or []):
                checklist, criado = ChecklistNR12.objects.get_or_create(
                    equipamento=equipamento,
                    data_checklist=hoje,
                    turno='MANHA',
                    defaults={
                        'frequencia': freq,
                        'status': 'PENDENTE'
                    }
                )
                
                if criado:
                    self.stdout.write(f'   ✅ Checklist {freq} criado')
                else:
                    self.stdout.write(f'   ℹ️ Checklist {freq} já existe')
            
        except Equipamento.DoesNotExist:
            self.stdout.write(f'   ❌ Equipamento {equipamento_id} não encontrado ou não ativo para NR12')

    def testar_frequencia_especifica(self, frequencia):
        """Testa geração para frequência específica"""
        self.stdout.write(f'\n🔄 TESTANDO FREQUÊNCIA: {frequencia.upper()}')
        self.stdout.write('-' * 40)
        
        freq_map = {
            'diaria': 'DIARIA',
            'semanal': 'SEMANAL', 
            'mensal': 'MENSAL'
        }
        
        freq_db = freq_map.get(frequencia)
        if not freq_db:
            self.stdout.write('   ❌ Frequência inválida')
            return
        
        # Contar equipamentos para esta frequência
        equipamentos = Equipamento.objects.filter(
            ativo_nr12=True,
            frequencias_checklist__contains=[freq_db],
            tipo_nr12__isnull=False
        )
        
        self.stdout.write(f'   Equipamentos encontrados: {equipamentos.count()}')
        
        if equipamentos.count() == 0:
            self.stdout.write(f'   ⚠️ Nenhum equipamento configurado para frequência {freq_db}')
            return
        
        # Executar task correspondente
        try:
            if frequencia == 'diaria':
                resultado = gerar_checklists_diarios.delay()
            elif frequencia == 'semanal':
                resultado = gerar_checklists_semanais.delay()
            elif frequencia == 'mensal':
                resultado = gerar_checklists_mensais.delay()
            
            self.stdout.write(f'   ✅ Task executada: {resultado.id}')
            self.stdout.write(f'   Resultado: {resultado.get(timeout=30)}')
            
        except Exception as e:
            self.stdout.write(f'   ❌ Erro ao executar task: {e}')

    def testar_todas_frequencias(self):
        """Testa geração para todas as frequências"""
        self.stdout.write('\n🔄 TESTANDO TODAS AS FREQUÊNCIAS')
        self.stdout.write('-' * 40)
        
        for freq in ['diaria', 'semanal', 'mensal']:
            self.testar_frequencia_especifica(freq)

        # Resumo final
        self.stdout.write('\n📊 RESUMO FINAL:')
        self.stdout.write('-' * 30)
        
        hoje = date.today()
        total_hoje = ChecklistNR12.objects.filter(data_checklist=hoje).count()
        pendentes = ChecklistNR12.objects.filter(
            data_checklist=hoje,
            status='PENDENTE'
        ).count()
        
        self.stdout.write(f'   Checklists criados hoje: {total_hoje}')
        self.stdout.write(f'   Checklists pendentes: {pendentes}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Teste concluído!'))